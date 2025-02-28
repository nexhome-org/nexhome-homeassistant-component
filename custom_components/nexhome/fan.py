from homeassistant.components.fan import *
from homeassistant.const import Platform
from .utils import get_value_by_identifier
import asyncio
from .const import TIME_NUMBER, DEVICES, DOMAIN, PowerSwitch, IP_CONFIG, SN_CONFIG, Windspeed
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
                        if device_key == '10':
                            fans.append(NexhomeFan(device, entity_key, Tool, coordinator))
                        elif device_key == '133':
                            fans.append(NexhomeFan133(device, entity_key, Tool, coordinator))
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


class NexhomeFan133(NexhomeFan):
    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, tool, coordinator)
        self._attr_supported_features = SUPPORT_PRESET_MODE
        self._attr_preset_modes = ["低速", "高速"]  # 定义风速
        self._attr_preset_mode = None  # 当前模式

    def turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        data = {'identifier': PowerSwitch, 'value': '1'}
        self._tool.device_control(data, self._device['address'])

        if preset_mode is not None:
            self.set_preset_mode(preset_mode)

    @property
    def preset_mode(self) -> str | None:
        speed_value = self._device.get(Windspeed)
        if speed_value == '1':
            return "低速"
        elif speed_value == '3':
            return "高速"
        return None

    def set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode == "低速":
            backend_value = '1'
        elif preset_mode == "高速":
            backend_value = '3'
        else:
            return

        data = {'identifier': Windspeed, 'value': backend_value}
        ss = self._tool.device_control(data, self._device['address'])
        print("Set Speed:", data, ss.json())
