from homeassistant.components.fan import *
from homeassistant.components.fan import FanEntityFeature  # Add this import
from homeassistant.const import Platform
from .utils import get_value_by_identifier
import asyncio
from .const import TIME_NUMBER, DEVICES, DOMAIN, PowerSwitch, IP_CONFIG, SN_CONFIG, Windspeed
from .nexhome_entity import NexhomeEntity
from .header import ServiceTool
from .nexhome_device import NEXHOME_DEVICE
from .nexhome_coordinator import NexhomeCoordinator
from homeassistant.config_entries import ConfigEntryState

import logging
_LOGGER = logging.getLogger(__name__)

FAN_MODEL_10 = {
    "0": "自动",
    "1": "低速",
    "2": "中速",
    "3": "高速",
}
FAN_MODEL_29 = {
    "1": "低速",
    "3": "高速",
}
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
                        if config_entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
                            await coordinator.async_config_entry_first_refresh()
                        
                        device_class_map = {
                            '10': NexhomeFan10,
                            '29': NexhomeFan29,
                            '75': NexhomeFan,
                            '133': NexhomeFan133,
                        }
                        if device_key in device_class_map:
                            fan_class = device_class_map[device_key]
                            fans.append(fan_class(device, entity_key, Tool, coordinator))
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
        print("turn_on", percentage, preset_mode)
        data = {'identifier': PowerSwitch, 'value': '1'}
        self._tool.device_control(data, self._device['address'])

    def turn_off(self):
        data = {'identifier': PowerSwitch, 'value': '0'}
        self._tool.device_control(data, self._device['address'])

class NexhomeFan10(NexhomeFan):
    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, tool, coordinator)
        self._attr_supported_features = FanEntityFeature.PRESET_MODE | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        self._attr_preset_modes = list(FAN_MODEL_10.values())
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
        if speed_value in FAN_MODEL_10:
            return FAN_MODEL_10[speed_value]
        return None

    def set_preset_mode(self, preset_mode: str) -> None:
        # 创建模式到值的反向映射
        reverse_map = {v: k for k, v in FAN_MODEL_10.items()}

        if preset_mode not in reverse_map:
            return

        data = {'identifier': Windspeed, 'value': reverse_map[preset_mode]}
        ss = self._tool.device_control(data, self._device['address'])
        print("Set Speed:", data, ss.json())

class NexhomeFan29(NexhomeFan):
    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, tool, coordinator)
        self._attr_supported_features = FanEntityFeature.PRESET_MODE | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        self._attr_preset_modes = list(FAN_MODEL_29.values())
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
        if speed_value in FAN_MODEL_29:
            return FAN_MODEL_29[speed_value]
        return None

    def set_preset_mode(self, preset_mode: str) -> None:
        # 创建模式到值的反向映射
        reverse_map = {v: k for k, v in FAN_MODEL_29.items()}

        if preset_mode not in reverse_map:
            return

        data = {'identifier': Windspeed, 'value': reverse_map[preset_mode]}
        ss = self._tool.device_control(data, self._device['address'])
        print("Set Speed:", data, ss.json())

class NexhomeFan133(NexhomeFan):
    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, tool, coordinator)
        self._attr_supported_features = FanEntityFeature.PRESET_MODE | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
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
