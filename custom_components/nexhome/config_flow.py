import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, SN_CONFIG, IP_CONFIG, DISCOVER
from .nexhome_discover import discover, send_test_message
from .utils import set_hass_obj, get_network_info


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
                # response_ip = send_test_message(validated_ip_port)
                # if response_ip:  # 确保找到了有效的IP地址
                #     discover_result = await discover(self.hass)
                #     data = {
                #         SN_CONFIG: sn,
                #         IP_CONFIG: response_ip
                #     }
                #     set_hass_obj(self.hass, DISCOVER, discover_result)
                #     return self.async_create_entry(title="My Component", data=data)
                # else:
                #     raise vol.Invalid("err_ip")
                data = {
                    SN_CONFIG: sn,
                    IP_CONFIG: validated_ip_port
                }
                # set_hass_obj(self.hass, DISCOVER, discover_result)
                return self.async_create_entry(title="My Component", data=data)

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