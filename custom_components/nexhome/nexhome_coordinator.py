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

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class NexhomeCoordinator(DataUpdateCoordinator):
    """Manages polling for state changes from the device"""

    def __init__(self, hass, tool, params):
        """Initialize the data update coordinator."""
        DataUpdateCoordinator.__init__(
            self,
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=5),
        )
        self._tool = tool
        self._params = params
        self._results = {}

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(20):  # 尝试在20秒内获取数据
                data = await self._tool.getProperties(self.hass, self._params)
                return data  # 成功获取数据则返回
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout fetching NEXHome data")  # 超时捕获并记录错误信息
            return False
        except Exception as err:
            _LOGGER.exception("An unexpected error occurred during data fetch: %s", err)
            return False
