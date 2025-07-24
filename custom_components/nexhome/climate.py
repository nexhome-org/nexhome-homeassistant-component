import logging
from homeassistant.components.climate import *
from .const import DEVICES, DOMAIN, FAN_MODEL_MAP, PowerSwitch, TemperatureSet, Temperature, WorkMode, Windspeed, IP_CONFIG, SN_CONFIG
from .nexhome_entity import NexhomeEntity
from .header import ServiceTool
from .nexhome_device import NEXHOME_DEVICE
from .nexhome_coordinator import NexhomeCoordinator
from .utils import get_key_from_value
from homeassistant.const import (
    Platform,
    UnitOfTemperature,
    ATTR_TEMPERATURE,
)
from homeassistant.config_entries import ConfigEntryState

_LOGGER = logging.getLogger(__name__)

TEMPERATURE_MAX = 30
TEMPERATURE_MIN = 16
MODEL_MAP = {
    "0": HVACMode.COOL,
    "1": HVACMode.HEAT,
    "2": HVACMode.DRY,
    "3": HVACMode.FAN_ONLY,
    "4": HVACMode.AUTO,
}
# 107专用模式映射
MODEL_MAP_107 = {
    "0": HVACMode.COOL,
    "1": HVACMode.HEAT,
    "2": HVACMode.DRY,
    "3": HVACMode.FAN_ONLY,
    "4": HVACMode.AUTO,
    "11": HVACMode.HEAT,  # 地暖映射为HEAT
    "12": HVACMode.HEAT,  # 制热+地暖也映射为HEAT
}
CUSTOM_MODE_NAME_107 = {
    "0": "制冷",
    "1": "制热",
    "2": "除湿",
    "3": "送风",
    "4": "自动",
    "11": "地暖",
    "12": "制热+地暖",
}
FAN_MODEL_107 = {
    "0": "自动",
    "1": "低速",
    "2": "中速",
    "3": "高速",
}
async def async_setup_entry(hass, config_entry, async_add_entities):
    IP = config_entry.data.get(IP_CONFIG)
    SN = config_entry.data.get(SN_CONFIG)
    Tool = ServiceTool(IP, SN)
    devices = hass.data[DOMAIN][DEVICES]
    if devices:
        climates = []
        for device in devices:
            device_key = device.get("device_type_id")
            device_address = device.get("address")
            if device_key in NEXHOME_DEVICE:
                for entity_key, config in NEXHOME_DEVICE[device_key]["entities"].items():
                    if config["type"] == Platform.CLIMATE:
                        identifiers = config["identifiers"]
                        params = [{'identifier': item, 'address': device_address} for item in identifiers]
                        coordinator = NexhomeCoordinator(hass, Tool, params)
                        if config_entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
                            await coordinator.async_config_entry_first_refresh()
                        if device_key == '3':
                            climates.append(NexhomeClimateTypeThree(device, entity_key, Tool, coordinator))
                        elif device_key == '11':
                            climates.append(NexhomeBasicClimate(device, entity_key, Tool, coordinator))
                        elif device_key == '107':
                            climates.append(NexhomeClimateType107(device, entity_key, Tool, coordinator))
        async_add_entities(climates, update_before_add=True)


class NexhomeBasicClimate(NexhomeEntity, ClimateEntity):
    def __init__(self, device, entity_key, tool, coordinator):
        NexhomeEntity.__init__(self, device, entity_key, coordinator)
        self._modes = [HVACMode.OFF, HVACMode.HEAT]
        self._tool = tool

    @property
    def supported_features(self):
        return ClimateEntityFeature.TARGET_TEMPERATURE
    @property
    def min_temp(self):
        return TEMPERATURE_MIN

    @property
    def max_temp(self):
        return TEMPERATURE_MAX

    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def target_temperature_low(self):
        return TEMPERATURE_MIN

    @property
    def target_temperature_high(self):
        return TEMPERATURE_MAX

    @property
    def target_temperature_step(self):
        return 1

    @property
    def hvac_modes(self):
        return self._modes

    @property
    def is_on(self) -> bool:
        return self.hvac_mode != HVACMode.OFF

    @property
    def hvac_mode(self) -> str:
        if self._device.get(PowerSwitch) is not None:
            return HVACMode.OFF if self._device.get(PowerSwitch) == '0' else HVACMode.HEAT
        else:
            return HVACMode.OFF

    @property
    def target_temperature(self):
        if self._device.get(TemperatureSet) is not None:
            value = self._device.get(TemperatureSet)
            return float(value) if value else None
        else:
            return None

    @property
    def current_temperature(self):
        if self._device.get(Temperature) is not None:
            value = self._device.get(Temperature)
            return float(value) if value else None
        else:
            return self._device.get(Temperature, None)

    def turn_on(self):
        data = {'identifier': 'PowerSwitch', 'value': '1'}
        self._tool.device_control(data, self._device['address'])

    def turn_off(self):
        data = {'identifier': 'PowerSwitch', 'value': '0'}
        self._tool.device_control(data, self._device['address'])

    # 设置模式
    def set_hvac_mode(self, hvac_mode: str) -> None:
        hvac_mode = hvac_mode.lower()
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            self.turn_on()

    def set_temperature(self, **kwargs) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = int(kwargs.get(ATTR_TEMPERATURE))
        try:
            data = {'identifier': 'TemperatureSet', 'value': temperature}
            self._tool.device_control(data, self._device['address'])
        except ValueError as e:
            _LOGGER.error(f"set_temperature {e}, kwargs = {kwargs}")

class NexhomeClimateTypeThree(NexhomeBasicClimate):
    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, tool, coordinator)
        self._modes = list(MODEL_MAP.values()) + [HVACMode.OFF]
        self._fan_speeds = list(FAN_MODEL_MAP.values())

    @property
    def supported_features(self):
        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE

    @property
    def hvac_mode(self) -> str:
        if self._device.get(PowerSwitch) is not None:
            power_switch = self._device.get(PowerSwitch)
            if power_switch == '0':
                mode = HVACMode.OFF
            else:
                mode = self._device.get(WorkMode)
            return MODEL_MAP.get(mode, HVACMode.OFF)
        else:
            return HVACMode.OFF

    @property
    def fan_modes(self):
        return self._fan_speeds

    @property
    def fan_mode(self):
        if self._device.get(Windspeed) is not None:
            value = self._device.get(Windspeed)
            return FAN_MODEL_MAP.get(value, FAN_MODEL_MAP["0"])
        else:
            return FAN_MODEL_MAP["0"]

    # 设置模式
    def set_hvac_mode(self, hvac_mode: str) -> None:
        hvac_mode = hvac_mode.lower()
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            # power_switch = get_value_by_identifier(self._property, 'PowerSwitch')
            power_switch = self._device.get(PowerSwitch)
            # 防止重复开启
            if power_switch == '0':
                self.turn_on()
            value = get_key_from_value(MODEL_MAP, hvac_mode)
            data = {'identifier': 'WorkMode', 'value': value}
            self._tool.device_control(data, self._device['address'])
    # 设置风速
    def set_fan_mode(self, fan_mode: str) -> None:
        if self.hvac_mode != HVACMode.OFF:
            value = get_key_from_value(FAN_MODEL_MAP, fan_mode)
            data = {'identifier': 'Windspeed', 'value': value}
            self._tool.device_control(data, self._device['address'])


class NexhomeClimateType107(NexhomeBasicClimate):
    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, tool, coordinator)
        self._modes = list(set(MODEL_MAP_107.values())) + [HVACMode.OFF]
        self._custom_mode = None
        self._preset_modes = ["none", "地暖", "制热+地暖"]
        self._preset_mode = "none"
        self._fan_speeds = list(FAN_MODEL_107.values())
    @property
    def supported_features(self):
        # 继承父类特性并增加预设模式
        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE | ClimateEntityFeature.PRESET_MODE

    @property
    def hvac_modes(self):
        return self._modes

    @property
    def preset_modes(self):
        return self._preset_modes

    @property
    def preset_mode(self):
        return self._preset_mode

    @property
    def fan_modes(self):
        return self._fan_speeds

    @property
    def fan_mode(self):
        if self._device.get(Windspeed) is not None:
            value = self._device.get(Windspeed)
            return FAN_MODEL_107.get(value, FAN_MODEL_107["0"])
        else:
            return FAN_MODEL_107["0"]

    @property
    def hvac_mode(self) -> str:
        mode_code = self._device.get(WorkMode)
        power_switch = self._device.get(PowerSwitch)
        if power_switch == '0':
            self._preset_mode = "none"
            return HVACMode.OFF
        if mode_code in MODEL_MAP_107:
            custom_mode = CUSTOM_MODE_NAME_107.get(mode_code)
            self._custom_mode = custom_mode
            if custom_mode in self._preset_modes:
                self._preset_mode = custom_mode
            else:
                self._preset_mode = "none"
            return MODEL_MAP_107[mode_code]
        self._preset_mode = "none"
        return HVACMode.OFF

    @property
    def extra_state_attributes(self):
        attrs = super().extra_state_attributes or {}
        if self._custom_mode:
            attrs["nexhome_custom_mode"] = self._custom_mode
        return attrs

    def set_hvac_mode(self, hvac_mode: str) -> None:
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            power_switch = self._device.get(PowerSwitch)
            if power_switch == '0':
                self.turn_on()
            # 默认切换到标准模式，不切换地暖/制热+地暖
            value = None
            for code, std_mode in MODEL_MAP_107.items():
                if std_mode == hvac_mode and code in ["0", "1", "2", "3", "4"]:
                    value = code
                    break
            if value:
                data = {'identifier': 'WorkMode', 'value': value}
                self._tool.device_control(data, self._device['address'])

    def set_preset_mode(self, preset_mode: str) -> None:
        # 切换地暖/制热+地暖
        if preset_mode in self._preset_modes and preset_mode != "none":
            for code, name in CUSTOM_MODE_NAME_107.items():
                if name == preset_mode:
                    data = {'identifier': 'WorkMode', 'value': code}
                    self._tool.device_control(data, self._device['address'])
                    self._preset_mode = preset_mode
                    break
        else:
            # 切换回标准模式
            self._preset_mode = "none"
    # 设置风速
    def set_fan_mode(self, fan_mode: str) -> None:
        if self.hvac_mode != HVACMode.OFF:
            value = get_key_from_value(FAN_MODEL_107, fan_mode)
            data = {'identifier': 'Windspeed', 'value': value}
            self._tool.device_control(data, self._device['address'])
