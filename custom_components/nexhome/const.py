from homeassistant.const import Platform


IP = '192.168.10.1:8085'
DEVICES = "devices"
SCENES = "scene"
DOMAIN = "NEXHome"
SN_CONFIG = 'sn_input'
IP_CONFIG = "ip_address"
DEVICE_DATA = "device_list"
DISCOVER = 'discover_obj'

# 轮询时间
TIME_NUMBER = 3

FAN_MODEL_MAP = {
    "0": "自动",
    "1": "低速",
    "2": "中速",
    "3": "高速",
    "4": "超静",
    "5": "超强",
    "6": "中低",
    "7": "中高",
}

EXTRA_SENSOR = [Platform.SENSOR]
EXTRA_SWITCH = [Platform.SWITCH, Platform.NUMBER, Platform.SELECT, Platform.COVER]
EXTRA_CONTROL = [Platform.CLIMATE, Platform.FAN, Platform.LIGHT]
ALL_PLATFORM =  EXTRA_SENSOR + EXTRA_CONTROL + EXTRA_SWITCH

PowerSwitch = "PowerSwitch"
TemperatureSet = "TemperatureSet"
Temperature = "Temperature"
Windspeed = "Windspeed"
WorkMode = "WorkMode"
Location = "Location"
Brightness = "Brightness"
Humidity = "Humidity"
PM25 = "PM25"
HCHO = "HCHO"
CO2 = "CO2"
LUX = "LUX"
VOC = "VOC"
Default_Device = {
    'id': 'teshudechangjingmianban', 
    'address': '680AE2FFFE33326D-2222222', 
    'name': '场景面板',
    'type': 'default',
}