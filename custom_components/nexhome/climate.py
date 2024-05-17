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
                        await coordinator.async_config_entry_first_refresh()
                        if device_key == '3':
                            climates.append(NexhomeClimateTypeThree(device, entity_key, Tool, coordinator))
                        elif device_key == '11':
                            climates.append(NexhomeBasicClimate(device, entity_key, Tool, coordinator))
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