from homeassistant.helpers.entity import Entity
from .const import DOMAIN, TIME_NUMBER
from .nexhome_device import NEXHOME_DEVICE
import logging
import asyncio
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback
_LOGGER = logging.getLogger(__name__)


class NexhomeEntity(CoordinatorEntity, Entity):
    def __init__(self, device, entity_key: str, coordinator):
        CoordinatorEntity.__init__(self, coordinator)
        self._device = device
        self._entity_key = entity_key
        self._config = NEXHOME_DEVICE[self._device['device_type_id']]["entities"][entity_key]
        self._unique_id = f"{DOMAIN}.{self._device['device_id']}_{entity_key}"
        self._device_name = self._device['device_name']
        self._property = None
        

    # identifiers (必需): 一个集合，包含唯一标识设备的元组。通常，元组至少包含一个组件的域名和设备的唯一ID。这个唯一标识符用于确保Home Assistant可以准确地识别每个设备。

    # name (可选): 设备的友好名称，它将在Home Assistant的UI中显示。

    # manufacturer (可选): 制造设备的公司或个人的名称。

    # model (可选): 设备的型号。这有助于用户识别设备的具体版本或类型。

    # sw_version (可选): 设备的软件版本。这对于跟踪更新或解决问题可能很有用。

    # via_device (可选): 如果这个设备是通过另一个设备连接到Home Assistant的（例如，一个传感器通过一个网关连接），这里应该填写那个“网关”设备的标识符。

    # configuration_url (可选): 如果设备提供了一个用于配置或管理的web界面，这里可以填写那个界面的URL。

    # entry_type (可选): 设备条目类型，比如 gateway, service 等，用于进一步描述设备的角色或类型。

    # connections (可选): 一个集合，包含元组，用于表示设备的其他连接信息，如MAC地址、序列号等。每个元组的第一个元素是连接类型（例如，homeassistant.const.CONNECTION_NETWORK_MAC），第二个元素是实际的连接值。

    # suggested_area (可选): 建议的区域名称，可以帮助自动将设备分配到Home Assistant中的一个区域。
    @property
    def device(self):
        return self._device

    @property
    def device_info(self):
        return {
            "manufacturer": "Nexhome",
            "model": f"{self._device_name}-{self._device['device_type_id']}",
            "identifiers": {(DOMAIN, self._device['device_id'])},
            "name": self._device_name
        }

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._config.get("name")
    @property
    def icon(self):
        return self._config.get("icon")
    
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        await self._update_state()
        self.hass.async_create_task(self.async_poll_properties())
    
    async def async_poll_properties(self):
        await self._update_state()
            
    async def _update_state(self):
        """更新状态"""
        address = self._device['address']
        identifiers = self._config["identifiers"]
        params = [{'identifier': item, 'address': address} for item in identifiers]
        propertys = await self._tool.getProperties(self.hass, params)  # 调用获取属性值的方法
        if propertys and len(propertys) > 0:
            for property in propertys:
                self._device[property.get('identifier')] = property.get('value', None)
                self.schedule_update_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._property = self.coordinator.data
        if self._property and len(self._property) > 0:
            for property in self._property:
                self._device[property.get('identifier')] = property.get('value', None)
        self.async_write_ha_state()