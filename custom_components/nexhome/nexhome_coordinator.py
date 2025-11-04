import asyncio
import logging
from datetime import timedelta
import async_timeout

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from homeassistant.const import *
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, TIME_NUMBER

_LOGGER = logging.getLogger(__name__)

class NexhomeCoordinator(DataUpdateCoordinator):
    """Manages polling for state changes from the device"""

    def __init__(self, hass, tool, params, update_interval=None):
        """Initialize the data update coordinator.
        
        Args:
            hass: Home Assistant instance
            tool: ServiceTool instance
            params: Parameters for device property query
            update_interval: Update interval in seconds (default: TIME_NUMBER from const)
        """
        if update_interval is None:
            update_interval = TIME_NUMBER
        DataUpdateCoordinator.__init__(
            self,
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )
        self._tool = tool
        self._params = params
        self._results = {}

    async def _async_update_data(self):
        try:
            device_property = await self._tool.getProperties(self.hass, self._params)
            if device_property:
                return device_property
            else:
                return False
        except Exception as err:
            return False
