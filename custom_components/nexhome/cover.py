from homeassistant.components.cover import *
import logging
from .nexhome_entity import NexhomeEntity
from .header import ServiceTool
from .const import DOMAIN, Location, DEVICES, IP_CONFIG, SN_CONFIG, Open, Close
from .nexhome_device import NEXHOME_DEVICE
from homeassistant.const import Platform
from .nexhome_coordinator import NexhomeCoordinator
from homeassistant.config_entries import ConfigEntryState

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
                        if config_entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
                            await coordinator.async_config_entry_first_refresh()
                        if device_key == "30":
                            numbers.append(NexhomeCover30(device, entity_key, Tool, coordinator))
                        elif device_key == "108":
                            numbers.append(NexhomeCover108(device, entity_key, Tool, coordinator))
                        else:
                            numbers.append(NexhomeCover6(device, entity_key, Tool, coordinator))
        async_add_entities(numbers)

class NexhomeCover6(NexhomeEntity, CoverEntity):
    """有开关停和定位的窗帘（6类型）"""
    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, coordinator)
        self._tool = tool

    @property
    def current_cover_position(self):
        if self._device.get(Location) is not None:
            return float(self._device[Location])
        return None
    @property
    def is_closed(self):
        if self._device.get(Location) is not None:
            return float(self._device[Location]) <= 0
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

class NexhomeCover108(NexhomeEntity, CoverEntity):
    """只有开关停，没有定位（108类型）"""
    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, coordinator)
        self._tool = tool
    @property
    def supported_features(self):
        return CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
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
    @property
    def is_closed(self):
        if self._device.get(Close) is not None:
            return bool(self._device[Close])
        if self._device.get(Open) is not None:
            return not bool(self._device[Open])
        return None
    @property
    def current_cover_position(self):
        return None

class NexhomeCover30(NexhomeEntity, CoverEntity):
    """只有开关，没有停和定位（30类型）"""
    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, coordinator)
        self._tool = tool
    @property
    def supported_features(self):
        return CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
    def open_cover(self, **kwargs):
        data = {'identifier': 'Open', 'value': 1}
        self._tool.device_control(data, self._device['address'])
        self.schedule_update_ha_state()
    def close_cover(self, **kwargs):
        data = {'identifier': 'Close', 'value': 1}
        self._tool.device_control(data, self._device['address'])
        self.schedule_update_ha_state()
    @property
    def is_closed(self):
        if self._device.get(Close) is not None:
            return bool(self._device[Close])
        if self._device.get(Open) is not None:
            return not bool(self._device[Open])
        return None
    @property
    def current_cover_position(self):
        return None
