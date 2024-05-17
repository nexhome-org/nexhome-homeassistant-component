from homeassistant.components.cover import *
import logging
from .nexhome_entity import NexhomeEntity
from .header import ServiceTool
from .const import DOMAIN, Location, DEVICES, IP_CONFIG, SN_CONFIG
from .nexhome_device import NEXHOME_DEVICE
from homeassistant.const import Platform
from .nexhome_coordinator import NexhomeCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    IP = config_entry.data.get(IP_CONFIG)
    SN = config_entry.data.get(SN_CONFIG)
    Tool = ServiceTool(IP, SN)
    devices = hass.data[DOMAIN][DEVICES]
    if devices:
        numbers = []
        for device in devices:
            device_key = device.get("device_type_id")
            device_address = device.get("address")
            if device_key in NEXHOME_DEVICE:
                for entity_key, config in NEXHOME_DEVICE[device_key]["entities"].items():
                    if config["type"] == Platform.COVER:
                        identifiers = config["identifiers"]
                        params = [{'identifier': item, 'address': device_address} for item in identifiers]
                        coordinator = NexhomeCoordinator(hass, Tool, params)
                        await coordinator.async_config_entry_first_refresh()
                        numbers.append(NexhomeInputCover(device, entity_key, Tool, coordinator))
        async_add_entities(numbers)    

class NexhomeInputCover(NexhomeEntity, CoverEntity):

    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, coordinator)
        self._tool = tool
    
    @property
    def current_cover_position(self):
        if self._device.get(Location) is not None:
            return float(self._device[Location])
        else:
            return None
        
    @property
    def is_closed(self):
        if self._device.get(Location) is not None:
            return float(self._device[Location]) <= 0
        else:
            return None
        
    def open_cover(self, **kwargs):
        data = {'identifier': 'Open', 'value': 1}
        self._tool.device_control(data, self._device['address'])
        self.schedule_update_ha_state()

    def close_cover(self, **kwargs):
        data = {'identifier': 'Close', 'value': 1}
        self._tool.device_control(data, self._device['address'])
        self.schedule_update_ha_state()

    def stop_cover(self, **kwargs):
        data = {'identifier': 'Stop', 'value': 1}
        self._tool.device_control(data, self._device['address'])
        self.schedule_update_ha_state()

    def set_cover_position(self, **kwargs):
        data = {'identifier': 'Location', 'value': kwargs['position']}
        self._tool.device_control(data, self._device['address'])
        self.schedule_update_ha_state()