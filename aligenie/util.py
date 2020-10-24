# coding: utf-8

import logging

from .config import LOGGER, EXCLUDE_DOMAINS, DEVICE_TYPES, INCLUDE_DOMAINS, DEVICE_TYPES_ICON

_LOGGER = logging.getLogger(__name__)


def errorResult(errorCode, messsage=None):
    """Generate error result"""
    messages = {
        'INVALIDATE_CONTROL_ORDER':    'invalidate control order',
        'SERVICE_ERROR': 'service error',
        'DEVICE_NOT_SUPPORT_FUNCTION': 'device not support',
        'INVALIDATE_PARAMS': 'invalidate params',
        'DEVICE_IS_NOT_EXIST': 'device is not exist',
        'IOT_DEVICE_OFFLINE': 'device is offline',
        'ACCESS_TOKEN_INVALIDATE': ' access_token is invalidate'
    }
    return {'errorCode': errorCode, 'message': messsage if messsage else messages[errorCode]}

def getControlService(action):
    i = 0
    service = ''
    for c in action:
        service += (('_' if i else '') + c.lower()) if c.isupper() else c
        i += 1
    return service

# http://doc-bot.tmall.com/docs/doc.htm?treeId=393&articleId=108271&docType=1
def guessDeviceType(entity_id, attributes):
    if 'hagenie_deviceType' in attributes:
        return attributes['hagenie_deviceType']

    # Exclude with domain
    domain = entity_id[:entity_id.find('.')]
    if domain in EXCLUDE_DOMAINS:
        return None

    # Guess from entity_id
    for deviceType in DEVICE_TYPES:
        if deviceType in entity_id:
            return deviceType

    # Map from domain
    return INCLUDE_DOMAINS[domain] if domain in INCLUDE_DOMAINS else None

def guessDeviceName(entity_id, attributes, places, aliases):
    if 'hagenie_deviceName' in attributes:
        return attributes['hagenie_deviceName']

    # Remove place prefix
    name = attributes['friendly_name']
    for place in places:
        if name.startswith(place):
            name = name[len(place):]
            break

    if aliases is None or entity_id.startswith('sensor'):
        return name

    # Name validation
    for alias in aliases:
        if name == alias['key'] or name in alias['value']:
            return name

    _LOGGER.error(
        '%s is not a valid name in https://open.bot.tmall.com/oauth/api/aliaslist', name)
    return None

def guessDeviceIcon(entity_id, attributes, deviceType):
    if 'hagenie_deviceIcon' in attributes:
        return attributes['hagenie_deviceIcon']

    return DEVICE_TYPES_ICON[deviceType] if deviceType in DEVICE_TYPES_ICON else None

def groupsAttributes(states):
    groups_attributes = []
    for state in states:
        group_entity_id = state.entity_id
        if group_entity_id.startswith('group.') and not group_entity_id.startswith('group.all_') and group_entity_id != 'group.default_view':
            group_attributes = state.attributes
            if 'entity_id' in group_attributes:
                groups_attributes.append(group_attributes)
    return groups_attributes

# https://open.bot.tmall.com/oauth/api/placelist
def guessZone(entity_id, attributes, groups_attributes, places):
    if 'hagenie_zone' in attributes:
        return attributes['hagenie_zone']

    # Guess with friendly_name prefix
    name = attributes['friendly_name']
    for place in places:
        if name.startswith(place):
            return place

    # Guess from HomeAssistant group
    for group_attributes in groups_attributes:
        for child_entity_id in group_attributes['entity_id']:
            if child_entity_id == entity_id:
                if 'hagenie_zone' in group_attributes:
                    return group_attributes['hagenie_zone']
                return group_attributes['friendly_name']

    return None

def guessPropertyAndAction(entity_id, attributes, state):
    # http://doc-bot.tmall.com/docs/doc.htm?treeId=393&articleId=108264&docType=1
    # http://doc-bot.tmall.com/docs/doc.htm?treeId=393&articleId=108268&docType=1
    # Support On/Off/Query only at this time
    if 'hagenie_propertyName' in attributes:
        name = attributes['hagenie_propertyName']

    elif entity_id.startswith('sensor.'):
        unit = attributes['unit_of_measurement'] if 'unit_of_measurement' in attributes else ''
        if unit == u'°C' or unit == u'℃':
            name = 'Temperature'
        elif unit == 'lx' or unit == 'lm':
            name = 'Brightness'
        elif ('hcho' in entity_id):
            name = 'Fog'
        elif ('humidity' in entity_id):
            name = 'Humidity'
        elif ('pm25' in entity_id):
            name = 'PM2.5'
        elif ('co2' in entity_id):
            name = 'WindSpeed'
        else:
            return (None, None)
    else:
        name = 'PowerState'
        if state != 'off':
            state = 'on'

    return ({'name': name.lower(), 'value': state}, 'Query' + name)
