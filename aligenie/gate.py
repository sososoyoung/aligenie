# coding: utf-8

import json
import logging

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from homeassistant.components.http import HomeAssistantView
from homeassistant.const import (MAJOR_VERSION, MINOR_VERSION)
from homeassistant.auth.const import ACCESS_TOKEN_EXPIRATION
import homeassistant.auth.models as models
from typing import Optional
from datetime import timedelta
from homeassistant.helpers.state import AsyncTrackStates
from urllib.request import urlopen

from .config import LOGGER, PLACES, ALIASES, ALL_ACTIONS, TRANSLATIONS, MAIN, MAIN, DOMAIN
from .util import errorResult, getControlService, guessDeviceType, guessDeviceName, groupsAttributes, guessZone, guessPropertyAndAction, guessDeviceIcon


class AliGenieGateView(HomeAssistantView):
    """View to handle Configuration requests."""

    url = '/genie'
    name = 'genie'
    requires_auth = False

    def __init__(self, hass, expire_hours):
        """Initialize the AliGenieGateView."""
        self._sensorZoneMap = {}
        self._load = False
        self._hass = hass
        self._expire_hours = expire_hours
        if expire_hours is not None:
            if MAJOR_VERSION == 0 and MINOR_VERSION <= 77:
                self._hass.auth._store.async_create_refresh_token = self.async_create_refresh_token77
            else:
                self._hass.auth._store.async_create_refresh_token = self.async_create_refresh_token78

    async def post(self, request):
        """Update state of entity."""
        if not self._load:
            self.discoveryDevice()
        try:
            data = await request.json()
            response = await self.handle_request(data)
        except:
            import traceback
            LOGGER.error(traceback.format_exc())
            response = {'header': {'name': 'errorResult'}, 'payload': errorResult(
                'SERVICE_ERROR', 'service exception')}

        return self.json(response)

    async def handle_request(self, data):
        """Handle request"""
        header = data['header']
        payload = data['payload']
        properties = None
        name = header['name']
        LOGGER.info("--- Request ---\n%s\n", json.dumps(
            data, indent=2, ensure_ascii=False))

        token = await self._hass.auth.async_validate_access_token(payload['accessToken'])
        if token is not None:
            namespace = header['namespace']
            if namespace == 'AliGenie.Iot.Device.Discovery':
                result = self.discoveryDevice()
            elif namespace == 'AliGenie.Iot.Device.Control':
                result = await self.controlDevice(name, payload)
            elif namespace == 'AliGenie.Iot.Device.Query':
                result = self.queryDevice(name, payload)
                if not 'errorCode' in result:
                    properties = result
                    result = {}
            else:
                result = errorResult('SERVICE_ERROR')
        else:
            result = errorResult('ACCESS_TOKEN_INVALIDATE')

        # Check error and fill response name
        header['name'] = (
            'Error' if 'errorCode' in result else name) + 'Response'

        # Fill response deviceId
        if 'deviceId' in payload:
            result['deviceId'] = payload['deviceId']

        response = {'header': header, 'payload': result}
        if properties:
            response['properties'] = properties

        LOGGER.info("--- Respnose ---\n%s\n", json.dumps(response, indent=2, ensure_ascii=False))
        return response

    def discoveryDevice(self):

        states = self._hass.states.async_all()
        groups_attributes = groupsAttributes(states)

        devices = []
        for state in states:
            attributes = state.attributes

            if attributes.get('hidden') or attributes.get('hagenie_hidden'):
                continue

            friendly_name = attributes.get('friendly_name')
            if friendly_name is None:
                continue

            entity_id = state.entity_id
            deviceType = guessDeviceType(entity_id, attributes)
            if deviceType is None:
                continue

            deviceName = guessDeviceName(
                entity_id, attributes, PLACES, ALIASES)
            if deviceName is None:
                continue

            icon = guessDeviceIcon(
                entity_id, attributes, deviceType)
            if icon is None:
                icon = 'https://home-assistant.io/images/favicon-192x192.png'

            zone = guessZone(entity_id, attributes, groups_attributes, PLACES)
            if zone is None:
                continue

            prop, action = guessPropertyAndAction(
                entity_id, attributes, state.state)
            if prop is None:
                continue

            # Merge all sensors into one for a zone
            # https://bbs.hassbian.com/thread-2982-1-1.html
            if deviceType == 'sensor':
                mapKey = 'groupsensor_' + zone
                if mapKey not in self._sensorZoneMap:
                    self._sensorZoneMap[mapKey] = set()
                self._sensorZoneMap[mapKey].add(entity_id)

                for sensor in devices:
                    if sensor['deviceType'] == 'sensor' and zone == sensor['zone']:
                        deviceType = None
                        if not action in sensor['actions']:
                            sensor['properties'].append(prop)
                            sensor['actions'].append(action)
                            sensor['model'] += ',' + friendly_name
                            # SHIT, length limition in deviceId: sensor['deviceId'] += '_' + entity_id
                        else:
                            LOGGER.info('SKIP: ' + entity_id)
                        break
                    else:
                        pass
                if deviceType is None:
                    continue
                deviceName = '传感器'
                entity_id = mapKey

            devices.append({
                'deviceId': entity_id,
                'deviceName': deviceName,
                'deviceType': deviceType,
                'zone': zone,
                'model': friendly_name,
                'brand': 'HomeAssistant',
                'icon': icon,
                'properties': [prop],
                'actions': ALL_ACTIONS + ['Query'] if action == 'QueryPowerState' else ['Query', action],
            })

        for sensor in devices:
            if sensor['deviceType'] == 'sensor':
                LOGGER.info('devices sensor: %s', json.dumps(sensor, indent=2, ensure_ascii=False))
        self._load = True
        return {'devices': devices}

    async def controlDevice(self, action, payload):
        entity_id = payload['deviceId']
        domain = entity_id[:entity_id.find('.')]
        data = {"entity_id": entity_id}
        if domain in TRANSLATIONS.keys():
            translation = TRANSLATIONS[domain][action]
            if callable(translation):
                service, content = translation(
                    self._hass.states.get(entity_id), payload)
                data.update(content)
            else:
                service = translation
        else:
            service = getControlService(action)

        with AsyncTrackStates(self._hass):
            result = await self._hass.services.async_call(domain, service, data, True)

        return {} if result else errorResult('IOT_DEVICE_OFFLINE')

    def queryDevice(self, name, payload):
        deviceId = payload['deviceId']

        if payload['deviceType'] == 'sensor' and deviceId.startswith('groupsensor'):

            states = self._hass.states.async_all()

            entity_ids = self._sensorZoneMap[deviceId]

            properties = [{'name': 'powerstate', 'value': 'on'}]
            for state in states:
                entity_id = state.entity_id
                attributes = state.attributes
                if entity_id in entity_ids:
                    prop, action = guessPropertyAndAction(
                        entity_id, attributes, state.state)
                    if prop is None:
                        continue
                    properties.append(prop)

            return properties
        else:
            state = self._hass.states.get(deviceId)
            LOGGER.info('state:')
            LOGGER.info(state)
            if state is not None or state.state != 'unavailable':
                return {'name': 'powerstate', 'value': 'off' if state.state == 'off' else 'on'}
        return errorResult('IOT_DEVICE_OFFLINE')

    async def async_create_refresh_token77(self,
                                           user: models.User, client_id: Optional[str] = None) \
            -> models.RefreshToken:
        """Create a new token for a user."""
        LOGGER.info('access token expiration: %d hours', self._expire_hours)
        refresh_token = models.RefreshToken(user=user,
                                            client_id=client_id,
                                            access_token_expiration=timedelta(hours=self._expire_hours))
        user.refresh_tokens[refresh_token.id] = refresh_token
        self._hass.auth._store._async_schedule_save()
        return refresh_token

    async def async_create_refresh_token78(self,
                                           user: models.User, client_id: Optional[str] = None,
                                           client_name: Optional[str] = None,
                                           client_icon: Optional[str] = None,
                                           token_type: str = models.TOKEN_TYPE_NORMAL,
                                           access_token_expiration: timedelta = ACCESS_TOKEN_EXPIRATION) \
            -> models.RefreshToken:
        """Create a new token for a user."""
        if access_token_expiration == ACCESS_TOKEN_EXPIRATION:
            access_token_expiration = timedelta(hours=self._expire_hours)
        LOGGER.info('Access token expiration: %d hours', self._expire_hours)
        kwargs = {
            'user': user,
            'client_id': client_id,
            'token_type': token_type,
            'access_token_expiration': access_token_expiration
        }  # type: Dict[str, Any]
        if client_name:
            kwargs['client_name'] = client_name
        if client_icon:
            kwargs['client_icon'] = client_icon

        refresh_token = models.RefreshToken(**kwargs)
        user.refresh_tokens[refresh_token.id] = refresh_token

        self._hass.auth._store._async_schedule_save()
        return refresh_token
