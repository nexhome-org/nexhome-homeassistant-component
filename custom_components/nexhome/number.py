from homeassistant.components.number import NumberEntity
import logging
from .nexhome_entity import NexhomeEntity
from .header import ServiceTool
from .const import DOMAIN, Location, DEVICES, IP_CONFIG, SN_CONFIG
from .nexhome_device import NEXHOME_DEVICE
from homeassistant.const import Platform
from .nexhome_coordinator import NexhomeCoordinator
from .coordinator_manager import CoordinatorManager
from homeassistant.config_entries import ConfigEntryState
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    IP = config_entry.data.get(IP_CONFIG)
    SN = config_entry.data.get(SN_CONFIG)
    Tool = ServiceTool(IP, SN)
    devices = hass.data[DOMAIN][DEVICES]
    
    # 获取协调器管理器实例
    coordinator_manager = CoordinatorManager.get_instance(hass, Tool, config_entry.entry_id)
    
    if devices:
        numbers = []
        for device in devices:
            device_key = device.get("device_type_id")
            device_address = device.get("address")
            if device_key in NEXHOME_DEVICE:
                for entity_key, config in NEXHOME_DEVICE[device_key]["entities"].items():
                    if config["type"] == Platform.NUMBER:
                        identifiers = config["identifiers"]
                        # 使用协调器管理器获取或创建共享协调器
                        coordinator = coordinator_manager.get_or_create_coordinator(device_address, identifiers)
                        if config_entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
                            await coordinator.async_config_entry_first_refresh()
                        numbers.append(NexhomeInputNumber(device, entity_key, Tool, coordinator))
        async_add_entities(numbers)

class NexhomeInputNumber(NexhomeEntity, NumberEntity):

    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, coordinator)
        self._state = False
        self._tool = tool
        # 使用原生数值范围属性，兼容新的 NumberEntity API
        self._attr_native_max_value = self._config.get("max")
        self._attr_native_min_value = self._config.get("min")
        self._attr_native_step = self._config.get("step")

    @property
    def native_value(self):
        if self._device.get(Location) is not None:
            return self._device[Location]
        else:
            return 0

    async def async_set_native_value(self, value: float) -> None:
        """使用新的异步接口设置数值，替代已弃用的 set_value。"""
        _LOGGER.info("NEXhome 设置为 %s", value)
        self._device[Location] = value
        data = {'identifier': 'Location', 'value': value}
        # 在执行器中调用同步 HTTP 控制，避免阻塞事件循环
        await self.hass.async_add_executor_job(
            self._tool.device_control,
            data,
            self._device['address'],
        )
        self.async_write_ha_state()
