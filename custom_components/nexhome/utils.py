from .const import DOMAIN

def get_value_by_identifier(data_list, identifier):
    for item in data_list:
        if item.get('identifier') == identifier:
            return item.get('value', None)
    return None


def get_key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None

def set_hass_obj(hass, key, value):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if key not in hass.data[DOMAIN]:
        hass.data[DOMAIN][key] = {}
    hass.data[DOMAIN][key] = value

def format_upd_mes(received_data):
    decoded_message = received_data.decode("utf-8")
    lines = decoded_message.split("\n")

    headers = {}
    content = []

    for line in lines:
        if line:  # 判断非空行
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()
            else:
                content.append(line)

    return content, headers
