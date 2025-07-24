import logging
from homeassistant.components.switch import SwitchEntity
from .const import DEVICES, DOMAIN, PowerSwitch, IP_CONFIG, SN_CONFIG
from .nexhome_entity import NexhomeEntity
from .header import ServiceTool
from .nexhome_device import NEXHOME_DEVICE
from .nexhome_coordinator import NexhomeCoordinator
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntryState
_LOGGER = logging.getLogger(__name__)
StateMap = {
    '0': False,
    '1': True
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    IP = config_entry.data.get(IP_CONFIG)
    SN = config_entry.data.get(SN_CONFIG)
    Tool = ServiceTool(IP, SN)
    devices = hass.data[DOMAIN][DEVICES]
    if devices:
        switches = []
        for device in devices:
            device_key = device.get("device_type_id")
            device_address = device.get("address")
            if device_key in NEXHOME_DEVICE:
                for entity_key, config in NEXHOME_DEVICE[device_key]["entities"].items():
                    if config["type"] == Platform.SWITCH:
                        identifiers = config["identifiers"]
                        params = [{'identifier': item, 'address': device_address} for item in identifiers]
                        coordinator = NexhomeCoordinator(hass, Tool, params)
                        if config_entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
                            await coordinator.async_config_entry_first_refresh()
                        switches.append(NexhomeSwitch(device, entity_key, Tool, coordinator))
        async_add_entities(switches, update_before_add=True)


class NexhomeSwitch(NexhomeEntity, SwitchEntity):

    def __init__(self, device, entity_key, tool, coordinator):
        super().__init__(device, entity_key, coordinator)
        self._state = False
        self._tool = tool

    @property
    def is_on(self):
        if self._device.get(PowerSwitch) is not None:
            return self._device[PowerSwitch] == '1'
        else:
            return False
    
    # 1=开，0=关    
    def switch_control(self, val):
        data = {'identifier': PowerSwitch, 'value': val}
        self._tool.device_control(data, self._device['address'])

    def turn_on(self, **kwargs):
        self._device[PowerSwitch] = '1'
        _LOGGER.info("nexhome开")
        self.schedule_update_ha_state()
        self.switch_control('1')

    def turn_off(self, **kwargs):
        self._device[PowerSwitch] = '0'
        _LOGGER.info("nexhome关")
        self.schedule_update_ha_state()
        self.switch_control('0')
        
# class NexhomeSceneSwitch(NexhomeSwitch):
#     # 1=开，0=关    
#     def switch_control(self, val):
#         data = {'identifier': 'PowerSwitch', 'value': val}
#         self._tool.device_control(data, self._device['address'])