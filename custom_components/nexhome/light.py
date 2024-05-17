import logging
from .nexhome_entity import NexhomeEntity
from .nexhome_device import NEXHOME_DEVICE
from .header import ServiceTool
from .const import DEVICES, DOMAIN, PowerSwitch, Brightness, IP_CONFIG, SN_CONFIG
from homeassistant.components.light import *
from homeassistant.const import Platform
from .nexhome_coordinator import NexhomeCoordinator
from .const import (
    DOMAIN,
    DEVICES
)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    IP = config_entry.data.get(IP_CONFIG)
    SN = config_entry.data.get(SN_CONFIG)
    Tool = ServiceTool(IP, SN)
    devices = hass.data[DOMAIN][DEVICES]
    if devices:
        lights = []
        for device in devices:
            device_key = device.get("device_type_id")
            device_address = device.get("address")
            if device_key in NEXHOME_DEVICE:
                for entity_key, config in NEXHOME_DEVICE[device_key]["entities"].items():
                    if config["type"] == Platform.LIGHT:
                        identifiers = config["identifiers"]
                        params = [{'identifier': item, 'address': device_address} for item in identifiers]
                        coordinator = NexhomeCoordinator(hass, Tool, params)
                        await coordinator.async_config_entry_first_refresh()
                        lights.append(NexhomeLight(device, entity_key, Tool, coordinator))
        async_add_entities(lights)    


class NexhomeLight(NexhomeEntity, LightEntity):
    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, coordinator)
        self._tool = tool

    @property
    def is_on(self):
        if self._device.get(PowerSwitch) is not None:
            return self._device[PowerSwitch] == '1'
        else:
            return False

    @property
    def brightness(self):
        if self._device.get(Brightness) is not None:
            return float(self._device.get(Brightness))
        else:
            return None

    # @property
    # def color_temp(self):
    #     return round(1000000 / self.color_temp_kelvin)

    # @property
    # def color_temp_kelvin(self):
    #     return self._device.get_attribute(X13Attributes.color_temperature)

    # @property
    # def min_color_temp_kelvin(self) -> int:
    #     return self._device.color_temp_range[0]

    # @property
    # def max_color_temp_kelvin(self) -> int:
    #     return self._device.color_temp_range[1]
    

    @property
    def supported_features(self) -> LightEntityFeature:
        return SUPPORT_BRIGHTNESS

    def turn_on(self, **kwargs: Any):
        if not self.is_on:
            data = {'identifier': PowerSwitch, 'value': '1'}
            self._tool.device_control(data, self._device['address'])
        for key in kwargs:
            value = kwargs.get(key)
            if key == ATTR_BRIGHTNESS:
                data = {'identifier': Brightness, 'value': value}
                self._tool.device_control(data, self._device['address'])
                

    def turn_off(self):
        data = {'identifier': PowerSwitch, 'value': '0'}
        self._tool.device_control(data, self._device['address'])

    # async def async_added_to_hass(self):
    #     await super().async_added_to_hass()
    #     await self._update_state()
    #     self.hass.async_create_task(self.async_poll_properties())
    
    # async def async_poll_properties(self):
    #     while True:
    #         await asyncio.sleep(TIME_NUMBER)
    #         await self._update_state()

    # async def _update_state(self):
    #     """更新状态"""
    #     address = self._device['address']
    #     params = [
    #         {
    #             'identifier': 'PowerSwitch',
    #             'address': address,
    #         },
    #         {
    #             'identifier': 'Brightness',
    #             'address': address,
    #         },
    #     ]
    #     property = await self._tool.getProperties(self.hass, params)  # 调用获取属性值的方法
    #     if property is not None:
    #         self._property = property
    #         self.schedule_update_ha_state()
