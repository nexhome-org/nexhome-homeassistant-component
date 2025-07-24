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
    Humidity, ColorTem, PM25, HCHO, VOC, CO2, LUX, Open, Close, Stop
)
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
    "12": {
        "name": "ZB-智能空气检测仪",
        "entities": {
            "12_humidity": {
                "type": Platform.SENSOR,
                "identifiers": [Humidity],
                "name": "湿度",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "12_temperature": {
                "type": Platform.SENSOR,
                "identifiers": [Temperature],
                "name": "温度",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "12_pm25": {
                "type": Platform.SENSOR,
                "identifiers": [PM25],
                "name": "PM 2.5",
                "device_class": SensorDeviceClass.PM25,
                "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "12_hoco": {
                "type": Platform.SENSOR,
                "identifiers": [HCHO],
                "name": "甲醛",
                "icon": "mdi:molecule",
                "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "12_co2": {
                "type": Platform.SENSOR,
                "identifiers": [CO2],
                "name": "CO2",
                "device_class": SensorDeviceClass.CO2,
                "unit": CONCENTRATION_PARTS_PER_MILLION,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "12_lux": {
                "type": Platform.SENSOR,
                "name": "LUX",
                "identifiers": [LUX],
                "device_class": SensorDeviceClass.ILLUMINANCE,
                "unit": LIGHT_LUX,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "12_voc": {
                "type": Platform.SENSOR,
                "identifiers": [VOC],
                "name": "VOC",
                "icon": "mdi:heat-wave",
                "unit": CONCENTRATION_PARTS_PER_MILLION,
                "state_class": SensorStateClass.MEASUREMENT
            },
        }
    },
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
