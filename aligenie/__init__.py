# coding: utf-8

"""The aligenie integration."""

from .config import DOMAIN, EXPIRE_HOURS, LOGGER
from .gate import AliGenieGateView

async def async_setup(hass, config):
    expire_hours = config[DOMAIN].get(EXPIRE_HOURS)
    hass.http.register_view(AliGenieGateView(hass, expire_hours))

    LOGGER.info('async_setup over')
    return True
