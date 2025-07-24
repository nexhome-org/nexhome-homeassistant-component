import logging
import asyncio
from homeassistant.components.select import SelectEntity
from .const import TIME_NUMBER, DEVICES, DOMAIN, SCENES, IP_CONFIG, SN_CONFIG
from .nexhome_entity import NexhomeEntity
from .header import ServiceTool
from .nexhome_device import NEXHOME_DEVICE
from .nexhome_coordinator import NexhomeCoordinator
from .utils import get_key_from_value
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntryState
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    IP = config_entry.data.get(IP_CONFIG)
    SN = config_entry.data.get(SN_CONFIG)
    Tool = ServiceTool(IP, SN)
    devices = hass.data[DOMAIN][DEVICES]
    if devices:
        selects = []
        for device in devices:
            device_key = device.get("device_type_id")
            device_address = device.get("address")
            if device_key in NEXHOME_DEVICE:
                for entity_key, config in NEXHOME_DEVICE[device_key]["entities"].items():
                    if config["type"] == Platform.SELECT:
                        identifiers = config["identifiers"]
                        params = [{'identifier': item, 'address': device_address} for item in identifiers]
                        coordinator = NexhomeCoordinator(hass, Tool, params)
                        if config_entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
                            await coordinator.async_config_entry_first_refresh()
                        if device_key == 'default':
                            selects.append(NexhomeSceneSelect(device, entity_key, Tool, coordinator))
                        else:
                            selects.append(NexhomeSelect(device, entity_key, Tool, coordinator))
        async_add_entities(selects)


class NexhomeSelect(NexhomeEntity, SelectEntity):

    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, coordinator)
        self._select_key = self._config.get("identifiers")[0]
        self._select_list = self._config.get("options")
        self._tool = tool

    @property
    def options(self):
        return list(self._select_list.values())

    @property
    def current_option(self):
        if self._device.get(self._select_key) is not None:
            return self._select_list.get(self._device.get(self._select_key), None)

    def select_option(self, option: str):
        value = get_key_from_value(self._select_list, option)
        data = {'identifier': self._select_key, 'value': value}
        self._tool.device_control(data, self._device['address'])

    # async def _update_state(self):
    #     params = [
    #         {
    #             'identifier': self._select_key,
    #             'address': self._device['address'],
    #         }
    #     ]
    #     property = await self._tool.getProperties(self.hass, params)  # 调用获取属性值的方法
    #     if property is not None:
    #         self._property = property
    #         self.schedule_update_ha_state()

class NexhomeSceneSelect(NexhomeSelect):
    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, tool, coordinator)
        self._select_key = self._config.get("identifiers")[0]
        self._select_list = None

    @property
    def options(self):
        if self._select_list is not None:
            return [(item.get("name", '-'), item.get("sceneId", '-')) for item in self._select_list]

    @property
    def current_option(self):
        return None

    def select_option(self, option):
        for item in self._select_list:
            if item.get("name") == option:
                value = item.get("id")
                data = {'identifier': self._select_key, 'value': str(value)}  # 将value转换为字符串
                self._tool.device_control(data, self._device['address'])
                break
        # value = get_key_from_value(self._select_list, option)
        # data = {'identifier': self._select_key, 'value': value}
        # self._tool.device_control(data, self._device['address'])

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        await self._update_state()
        self.hass.async_create_task(self.async_poll_properties())

    async def async_poll_properties(self):
        while True:
            await asyncio.sleep(TIME_NUMBER)
            await self._update_state()

    async def _update_state(self):
        scenes = await self._tool.getScene(self.hass)  # 调用获取属性值的方法
        if scenes is not None:
            if SCENES not in self.hass.data[DOMAIN]:
                self.hass.data[DOMAIN][SCENES] = {}
            self.hass.data[DOMAIN][SCENES] = scenes
            self._select_list = scenes
            self.schedule_update_ha_state()
