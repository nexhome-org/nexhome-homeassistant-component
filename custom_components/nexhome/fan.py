from homeassistant.components.fan import *
from homeassistant.const import Platform
from .utils import get_value_by_identifier
import asyncio
from .const import TIME_NUMBER, DEVICES, DOMAIN, PowerSwitch, IP_CONFIG, SN_CONFIG
from .nexhome_entity import NexhomeEntity
from .header import ServiceTool
from .nexhome_device import NEXHOME_DEVICE
from .nexhome_coordinator import NexhomeCoordinator
import logging
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    IP = config_entry.data.get(IP_CONFIG)
    SN = config_entry.data.get(SN_CONFIG)
    Tool = ServiceTool(IP, SN)
    devices = hass.data[DOMAIN][DEVICES]
    if devices:
        fans = []
        for device in devices:
            device_key = device.get("device_type_id")
            device_address = device.get("address")
            if device_key in NEXHOME_DEVICE:
                for entity_key, config in NEXHOME_DEVICE[device_key]["entities"].items():
                    if config["type"] == Platform.FAN:
                        identifiers = config["identifiers"]
                        params = [{'identifier': item, 'address': device_address} for item in identifiers]
                        coordinator = NexhomeCoordinator(hass, Tool, params)
                        await coordinator.async_config_entry_first_refresh()
                        fans.append(NexhomeFan(device, entity_key, Tool, coordinator))
        async_add_entities(fans)    


class NexhomeFan(NexhomeEntity, FanEntity):

    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, coordinator)
        self._tool = tool
        
    @property
    def is_on(self) -> bool:
        if self._device.get(PowerSwitch) is not None:
            return self._device[PowerSwitch] == '1'
        else:
            return False
        
    def turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        data = {'identifier': PowerSwitch, 'value': '1'}
        self._tool.device_control(data, self._device['address'])

    def turn_off(self):
        data = {'identifier': PowerSwitch, 'value': '0'}
        self._tool.device_control(data, self._device['address'])


