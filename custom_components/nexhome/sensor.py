from .nexhome_entity import NexhomeEntity
from .nexhome_device import NEXHOME_DEVICE
from .header import ServiceTool
from .nexhome_coordinator import NexhomeCoordinator
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import Platform
from .const import (
    DOMAIN,
    DEVICES,
    IP_CONFIG,
    SN_CONFIG
)
from homeassistant.config_entries import ConfigEntryState


async def async_setup_entry(hass, config_entry, async_add_entities):
    IP = config_entry.data.get(IP_CONFIG)
    SN = config_entry.data.get(SN_CONFIG)
    Tool = ServiceTool(IP, SN)
    devices = hass.data[DOMAIN][DEVICES]
    if devices:
        sensors = []
        for device in devices:
            device_key = device.get("device_type_id")
            device_address = device.get("address")
            if device_key in NEXHOME_DEVICE:
                for entity_key, config in NEXHOME_DEVICE[device_key]["entities"].items():
                    if config["type"] == Platform.SENSOR:
                        identifiers = config["identifiers"]
                        params = [{'identifier': item, 'address': device_address} for item in identifiers]
                        coordinator = NexhomeCoordinator(hass, Tool, params)
                        # 只在setup阶段调用首次刷新
                        if config_entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
                            await coordinator.async_config_entry_first_refresh()
                        sensors.append(NexhomeSensor(device, entity_key, Tool, coordinator))
        async_add_entities(sensors)


class NexhomeSensor(NexhomeEntity, SensorEntity):

    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, coordinator)
        self._tool = tool
        self._native_value_key = self._config.get("identifiers")[0]

    @property
    def native_value(self):
        return self._device.get(self._native_value_key, None)

    @property
    def device_class(self):
        return self._config.get("device_class")

    @property
    def state_class(self):
        return self._config.get("state_class")

    @property
    def native_unit_of_measurement(self):
        return self._config.get("unit")

    @property
    def capability_attributes(self):
        return {"state_class": self.state_class} if self.state_class else {}
