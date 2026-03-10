"""协调器管理器 - 按设备共享协调器以减少请求频率"""
import asyncio
import logging
from typing import Dict, Set
from .nexhome_coordinator import NexhomeCoordinator
from .header import ServiceTool

_LOGGER = logging.getLogger(__name__)


class CoordinatorManager:
    """管理设备协调器，确保同一设备的所有实体共享一个协调器"""
    
    _instances: Dict[str, 'CoordinatorManager'] = {}
    
    def __init__(self, hass, tool: ServiceTool):
        self.hass = hass
        self.tool = tool
        # 按设备地址存储协调器: {device_address: coordinator}
        self._coordinators: Dict[str, NexhomeCoordinator] = {}
        # 按设备地址存储所需的所有标识符: {device_address: set(identifiers)}
        self._device_identifiers: Dict[str, Set[str]] = {}
    
    @classmethod
    def get_instance(cls, hass, tool: ServiceTool, config_entry_id: str):
        """获取或创建协调器管理器实例"""
        if config_entry_id not in cls._instances:
            cls._instances[config_entry_id] = cls(hass, tool)
        return cls._instances[config_entry_id]

    @classmethod
    async def async_remove_instance(cls, config_entry_id: str) -> None:
        """移除并清理指定配置条目的协调器管理器实例（支持集成 reload）"""
        instance = cls._instances.pop(config_entry_id, None)
        if instance is None:
            return
        await instance.async_shutdown()

    async def async_shutdown(self) -> None:
        """关闭所有协调器并清理内部缓存"""
        coordinators = list(self._coordinators.values())
        self._coordinators.clear()
        self._device_identifiers.clear()

        for coordinator in coordinators:
            shutdown = getattr(coordinator, "async_shutdown", None)
            if shutdown is None:
                continue
            try:
                result = shutdown()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as err:
                _LOGGER.debug("关闭协调器失败: %s", err)
    
    def get_or_create_coordinator(self, device_address: str, identifiers: list) -> NexhomeCoordinator:
        """
        获取或创建设备协调器
        :param device_address: 设备地址
        :param identifiers: 需要查询的标识符列表
        :return: 协调器实例
        """
        # 如果已存在协调器，更新标识符集合
        if device_address in self._coordinators:
            coordinator = self._coordinators[device_address]
            # 更新标识符集合
            if device_address not in self._device_identifiers:
                self._device_identifiers[device_address] = set()
            self._device_identifiers[device_address].update(identifiers)
            # 更新协调器的参数
            self._update_coordinator_params(device_address)
            return coordinator
        
        # 创建新的协调器
        if device_address not in self._device_identifiers:
            self._device_identifiers[device_address] = set()
        self._device_identifiers[device_address].update(identifiers)
        
        params = [{'identifier': item, 'address': device_address} 
                  for item in self._device_identifiers[device_address]]
        
        coordinator = NexhomeCoordinator(self.hass, self.tool, params)
        self._coordinators[device_address] = coordinator
        
        _LOGGER.debug(f"创建新协调器: {device_address}, 标识符: {self._device_identifiers[device_address]}")
        
        return coordinator
    
    def _update_coordinator_params(self, device_address: str):
        """更新协调器的参数"""
        if device_address not in self._coordinators:
            return
        
        coordinator = self._coordinators[device_address]
        params = [{'identifier': item, 'address': device_address} 
                  for item in self._device_identifiers[device_address]]
        coordinator._params = params
    
    def remove_coordinator(self, device_address: str):
        """移除设备协调器（当设备被移除时）"""
        if device_address in self._coordinators:
            del self._coordinators[device_address]
        if device_address in self._device_identifiers:
            del self._device_identifiers[device_address]

