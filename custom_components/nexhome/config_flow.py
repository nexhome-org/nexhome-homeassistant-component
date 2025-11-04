import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, SN_CONFIG, IP_CONFIG, DISCOVER, FILTER_MODE_CONFIG, FILTER_DEVICES_CONFIG
from .header import ServiceTool
from .nexhome_discover import discover, send_test_message
from .utils import set_hass_obj


def validate_ip_port(value):
    parts = value.split(":")
    if len(parts) != 2:
        raise vol.Invalid("err_ip")

    ip_address, port = parts
    if not ip_address or not port:
        raise vol.Invalid("err_ip")

    try:
        # 检查 IP 地址的有效性
        ip_parts = ip_address.split(".")
        if len(ip_parts) != 4 or not all(0 <= int(part) < 256 for part in ip_parts):
            raise vol.Invalid("err_ip")

        # 检查端口号范围
        port_num = int(port)
        if not (0 < port_num < 65536):
            raise vol.Invalid("err_ip")

    except ValueError:
        raise vol.Invalid("err_ip")

    return value

class NexhomeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            ip_address = user_input.get("ip_address")
            sn = user_input["sn"]
            try:
                # 校验 IP 地址和端口格式
                validated_ip_port = validate_ip_port(ip_address)
                # 保存IP和SN到flow，跳转到设备筛选步骤
                self._ip_address = validated_ip_port
                self._sn = sn
                return await self.async_step_device_filter()

            except vol.Invalid as err:
                print(err)
                errors["base"] = err.error_message

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str,
                vol.Required("sn"): str,
            }),
            errors=errors,
        )

    async def async_step_device_filter(self, user_input=None):
        """设备筛选步骤"""
        errors = {}
        
        # 获取设备列表
        if not hasattr(self, '_device_list'):
            tool = ServiceTool(self._ip_address, self._sn)
            try:
                await tool.login(self.hass)
                device_list = await tool.getDevice(self.hass)
                if not device_list:
                    errors["base"] = "无法获取设备列表"
                    return await self.async_step_user(errors=errors)
                self._device_list = device_list
            except Exception as e:
                errors["base"] = f"获取设备列表失败: {str(e)}"
                return await self.async_step_user(errors=errors)

        if user_input is not None:
            # 用户提交了筛选结果
            filter_mode = user_input.get(FILTER_MODE_CONFIG, "exclude")
            selected_device_ids = user_input.get(FILTER_DEVICES_CONFIG, [])
            
            # 保存配置
            data = {
                SN_CONFIG: self._sn,
                IP_CONFIG: self._ip_address,
                FILTER_MODE_CONFIG: filter_mode,
                FILTER_DEVICES_CONFIG: selected_device_ids,
            }
            return self.async_create_entry(title="Nexhome", data=data)

        # 构建设备选项字典（用于MultiSelect）
        device_options = {}
        for device in self._device_list:
            device_id = device.get('id')
            device_name = device.get('name', 'Unknown')
            device_address = device.get('address', '')
            # 显示格式：设备名称 (地址)
            display_name = f"{device_name} ({device_address})" if device_address else device_name
            device_options[device_id] = display_name

        # 构建数据schema
        schema_dict = {
            vol.Required(FILTER_MODE_CONFIG, default="exclude"): vol.In({
                "exclude": "排除",
                "include": "包含"
            }),
            vol.Optional(FILTER_DEVICES_CONFIG, default=[]): vol.All(
                cv.multi_select(device_options),
                vol.Length(min=0)
            ),
        }

        return self.async_show_form(
            step_id="device_filter",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
            description_placeholders={
                "instruction": "你可以通过筛选只接入想要的设备。",
                "note": "在排除模式中,如果不勾选任何设备,则相当于接入所有设备"
            }
        )
