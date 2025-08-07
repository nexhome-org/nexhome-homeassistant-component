from homeassistant.const import (
    Platform,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    UnitOfTemperature,
    PERCENTAGE,
    LIGHT_LUX
)
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from .const import (
    FAN_MODEL_MAP, PowerSwitch, TemperatureSet, Temperature, Windspeed, WorkMode, Location, Brightness,
    Humidity, ColorTem, PM25, HCHO, VOC, CO2, LUX, Open, Close, Stop, WindDirection, PM10
)

def create_air_monitor_config(device_id: str, name: str, sensors: list) -> dict:
    """
    工厂函数：动态生成空气检测仪设备配置
    
    Args:
        device_id: 设备ID
        name: 设备名称
        sensors: 传感器列表
    """
    sensor_configs = {
        Humidity: {
            "type": Platform.SENSOR,
            "identifiers": [Humidity],
            "name": "湿度",
            "device_class": SensorDeviceClass.HUMIDITY,
            "unit": PERCENTAGE,
            "state_class": SensorStateClass.MEASUREMENT
        },
        Temperature: {
            "type": Platform.SENSOR,
            "identifiers": [Temperature],
            "name": "温度",
            "device_class": SensorDeviceClass.TEMPERATURE,
            "unit": UnitOfTemperature.CELSIUS,
            "state_class": SensorStateClass.MEASUREMENT
        },
        PM25: {
            "type": Platform.SENSOR,
            "identifiers": [PM25],
            "name": "PM 2.5",
            "device_class": SensorDeviceClass.PM25,
            "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            "state_class": SensorStateClass.MEASUREMENT
        },
        PM10: {
            "type": Platform.SENSOR,
            "identifiers": [PM10],
            "name": "PM 10",
            "device_class": SensorDeviceClass.PM10,
            "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            "state_class": SensorStateClass.MEASUREMENT
        },
        HCHO: {
            "type": Platform.SENSOR,
            "identifiers": [HCHO],
            "name": "甲醛",
            "icon": "mdi:molecule",
            "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            "state_class": SensorStateClass.MEASUREMENT
        },
        CO2: {
            "type": Platform.SENSOR,
            "identifiers": [CO2],
            "name": "CO2",
            "device_class": SensorDeviceClass.CO2,
            "unit": CONCENTRATION_PARTS_PER_MILLION,
            "state_class": SensorStateClass.MEASUREMENT
        },
        LUX: {
            "type": Platform.SENSOR,
            "name": "LUX",
            "identifiers": [LUX],
            "device_class": SensorDeviceClass.ILLUMINANCE,
            "unit": LIGHT_LUX,
            "state_class": SensorStateClass.MEASUREMENT
        },
        VOC: {
            "type": Platform.SENSOR,
            "identifiers": [VOC],
            "name": "VOC",
            "icon": "mdi:heat-wave",
            "unit": CONCENTRATION_PARTS_PER_MILLION,
            "state_class": SensorStateClass.MEASUREMENT
        }
    }
    
    entities = {}
    for sensor in sensors:
        if sensor in sensor_configs:
            entities[f"{device_id}_{sensor}"] = sensor_configs[sensor]
    
    return {
        "name": name,
        "entities": entities
    }

NEXHOME_DEVICE = {
    "default": {
        "name": "场景面板",
        "entities": {
            "default_select": {
                "name": "场景",
                "type": Platform.SELECT,
                "options": FAN_MODEL_MAP,
                "identifiers": [Windspeed],
                "icon": "mdi:home-map-marker"
            },
            "default_fan": {
                "name": "开关",
                "type": Platform.SWITCH,
                "identifiers": [PowerSwitch],
                "icon": "mdi:power"
            }
        }
    },
    "6": {
        "name": "窗帘",
        "entities": {
            "6_curtain": {
                "name": '窗帘',
                "type": Platform.COVER,
                "icon": "mdi:curtains",
                "max": 100,
                "min": 0,
                "step": 1,
                "identifiers": [Location]
            },
        }
    },
    "108": {
       "name": "窗帘（开关停）",
       "entities": {
           "108_curtain": {
               "name": '窗帘（开关停）',
               "type": Platform.COVER,
               "icon": "mdi:curtains",
               "identifiers": [Open, Close, Stop],
           },
       }
   },
   "30": {
       "name": "窗帘（开关）",
       "entities": {
           "30_curtain": {
               "name": '窗帘（开关）',
               "type": Platform.COVER,
               "icon": "mdi:curtains",
               "identifiers": [Open, Close],
           },
       }
   },
    "2": {
        "name": "调光灯",
        "entities": {
            "2_light": {
                "name": '调光灯',
                "type": Platform.LIGHT,
                "icon": "mdi:lightbulb",
                "identifiers": [Brightness, PowerSwitch]
            }
        }
    },
    "51": {
        "name": "色温灯",
        "entities": {
            "51_light": {
                "name": '色温灯',
                "type": Platform.LIGHT,
                "icon": "mdi:lightbulb",
                "identifiers": [Brightness, PowerSwitch, ColorTem]
            }
        }
    },
    "1": {
        "name": "灯",
        "entities": {
            "1_light": {
                "name": '开关',
                "type": Platform.SWITCH,
                "icon": "mdi:power",
                "identifiers": [PowerSwitch]
            }
        }
    },
    "3": {
        "name": "空调",
        "entities": {
            "3_climate": {
                "name": "空调",
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "identifiers": [PowerSwitch, Windspeed, WorkMode, Temperature, TemperatureSet]
            },
        }
    },
    "73": {
        "name": "空调（摆风+风向3档）",
        "entities": {
            "73_climate": {
                "name": "空调（摆风+风向3档）",
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "identifiers": [PowerSwitch, Windspeed, WorkMode, Temperature, TemperatureSet, WindDirection]
            },
        }
    },
    "100": {
        "name": "空调（风速2档+自动）",
        "entities": {
            "100_climate": {
                "name": "空调（风速2档+自动）",
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "identifiers": [PowerSwitch, Windspeed, WorkMode, Temperature, TemperatureSet]
            },
        }
    },
    "101": {
        "name": "空调（风速5档+自动）",
        "entities": {
            "101_climate": {
                "name": "空调（风速5档+自动）",
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "identifiers": [PowerSwitch, Windspeed, WorkMode, Temperature, TemperatureSet]
            },
        }
    },
    "102": {
        "name": "空调（风速7档+自动）",
        "entities": {
            "102_climate": {
                "name": "空调（风速7档+自动）",
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "identifiers": [PowerSwitch, Windspeed, WorkMode, Temperature, TemperatureSet]
            },
        }
    },
    "107": {
        "name": "空调（模式+地暖）",
        "entities": {
            "107_climate": {
                "name": "空调（模式+地暖）",
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "identifiers": [PowerSwitch, Windspeed, WorkMode, Temperature, TemperatureSet]
            },
        }
    },
    "5": {
        "name": "温湿度传感器",
        "entities": {
            "5_humidity": {
                "type": Platform.SENSOR,
                "name": "湿度",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
                "identifiers": [Humidity]
            },
            "5_temperature": {
                "type": Platform.SENSOR,
                "name": "温度",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
                "identifiers": [Temperature]
            },
        }
    },
    "10": {
        "name": "新风",
        "entities": {
            "10_fan": {
                "name": "开关",
                "type": Platform.FAN,
                "icon": "mdi:fan",
                "identifiers": [PowerSwitch, Windspeed]
            }
        }
    },
    "75": {
        "name": "新风（仅支持开关）",
        "entities": {
            "75_fan": {
                "name": "新风（仅支持开关）",
                "type": Platform.FAN,
                "icon": "mdi:fan",
                "identifiers": [PowerSwitch]
            }
        }
    },
    "11": {
        "name": "地暖",
        "entities": {
            "11_climate": {
                "name": "地暖",
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "identifiers": [PowerSwitch, Temperature, TemperatureSet]
            },
        }
    },
    "35": {
        "name": "地暖（仅支持开关+温度）",
        "entities": {
            "35_climate": {
                "name": "地暖（仅支持开关+温度）",
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "identifiers": [PowerSwitch, Temperature, TemperatureSet]
            },
        }
    },
    "8": create_air_monitor_config("8", "空气质量传感器（PM2.5、CO2、甲醛、温度、湿度六合一隐藏光照）", [Humidity, Temperature, PM25, HCHO, CO2]),
    "12": create_air_monitor_config("12", "空气检测仪（PM2.5、CO2、甲醛、温度、湿度五合一）", [Humidity, Temperature, PM25, HCHO, CO2, LUX, VOC]),
    "13": create_air_monitor_config("13", "空气检测仪（CO2、温度、湿度三合一）", [CO2, Humidity, Temperature]),
    "14": create_air_monitor_config("14", "空气检测仪（PM2.5、CO2、温度、湿度四合一）", [CO2, Humidity, Temperature, CO2]),
    "15": create_air_monitor_config("15", "空气检测仪（PM2.5、温度、湿度三合一）", [Humidity, Temperature, PM25]),
    "16": create_air_monitor_config("16", "空气检测仪（CO2、甲醛、温度、湿度四合一）", [Humidity, Temperature, HCHO, CO2]),
    "59": create_air_monitor_config("59", "空气检测仪（PM2.5、CO2、甲醛、温度、湿度、VOC六合一）", [Humidity, Temperature, PM25, HCHO, CO2, VOC]),
    "60": create_air_monitor_config("60", "空气检测仪（PM2.5、CO2、甲醛、温度、湿度、PM10六合一）", [Humidity, Temperature, PM25, HCHO, CO2, PM10]),
    "61": create_air_monitor_config("61", "空气检测仪（PM2.5、CO2、温度、湿度、PM10五合一）", [Humidity, Temperature, PM25, CO2, PM10]),
    "62": create_air_monitor_config("62", "空气检测仪（PM2.5、温度、湿度、PM10四合一）", [Humidity, Temperature, PM25, PM10]),
    "110": create_air_monitor_config("110", "空气检测仪（PM2.5、PM10、CO2、温度、湿度、VOC六合一）", [Humidity, Temperature, PM25, PM10, CO2, VOC]),
    "132": {
        "name": "雾化",
        "entities": {
            "132_switch": {
                "name": '开关',
                "type": Platform.SWITCH,
                "icon": "mdi:power",
                "identifiers": [PowerSwitch]
            }
        }
    },
    "133": {
        "name": "排风扇",
        "entities": {
            "133_fan": {
                "name": '开关',
                "type": Platform.FAN,
                "icon": "mdi:fan",
                "identifiers": [PowerSwitch, Windspeed]
            }
        }
    },
}
