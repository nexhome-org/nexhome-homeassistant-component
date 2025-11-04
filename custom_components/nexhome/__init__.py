from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DEVICES, ALL_PLATFORM, Default_Device, SN_CONFIG, IP_CONFIG, DISCOVER, DOMAIN, FILTER_MODE_CONFIG, FILTER_DEVICES_CONFIG
from .header import ServiceTool
from .nexhome_discover import discover, send_test_message
from .utils import set_hass_obj
# 在组件全局作用域中存储监听器引用
# discoverObj = None

async def async_setup_entry(hass, entry):
    # global discoverObj
    await register_device_list_service(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, ALL_PLATFORM)
    # for platform in ALL_PLATFORM:
    #     await hass.async_create_task(hass.config_entries.async_forward_entry_setup(
    #         entry, platform))

    # discoverObj = hass.data[DOMAIN].get(DISCOVER)
    # if discoverObj is None:
    #     discoverObj = await discover(hass)
    # else:
    #     await discoverObj.start()

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # discoverObj.close()
    # 卸载平台
    for platform in ALL_PLATFORM:
        await hass.config_entries.async_forward_entry_unload(entry, platform)
    return True


async def register_device_list_service(hass, entry):
    SN = entry.data.get(SN_CONFIG)
    IP = entry.data.get(IP_CONFIG)
    tool = ServiceTool(IP, SN)
    await tool.login(hass)
    deviceList = await tool.getDevice(hass)
    # deviceList = [Default_Device] + deviceList
    
    # 从配置中获取筛选设置
    filter_mode = entry.data.get(FILTER_MODE_CONFIG, "exclude")
    filter_devices = entry.data.get(FILTER_DEVICES_CONFIG, [])
    
    # 过滤设备
    if deviceList and filter_devices:
        if filter_mode == "include":
            # 包含模式：只保留选中的设备
            deviceList = [
                device for device in deviceList
                if device.get('id') in filter_devices
            ]
        else:
            # 排除模式：排除选中的设备
            deviceList = [
                device for device in deviceList
                if device.get('id') not in filter_devices
            ]
    # 如果filter_devices为空，排除模式下相当于接入所有设备
    
    device_value = [
        {
            'device_id': device.get('id'),
            'device_type_id': device.get('type'),
            'device_name': device.get('name'),
            **device
        }
        for device in deviceList
    ]
    print('11', device_value)
    set_hass_obj(hass, DEVICES, device_value)
    # if DOMAIN not in hass.data:
    #     hass.data[DOMAIN] = {}
    # if DEVICES not in hass.data[DOMAIN]:
    #     hass.data[DOMAIN][DEVICES] = {}
    # if deviceList:
    #     hass.data[DOMAIN][DEVICES] = [
    #             {
    #                 'device_id': device.get('id'),
    #                 'device_type_id': device.get('type'),
    #                 'device_name': device.get('name'),
    #                 **device
    #             }
    #             for device in deviceList
    #         ]

