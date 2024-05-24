import hashlib
import time
import logging
import requests

_LOGGER = logging.getLogger(__name__)


class ServiceTool():
    def __init__(self, ip_address, sn):
        self.ip_address = ip_address
        self.sn = sn

    def get_ip_address(self):
        return self.ip_address

    def get_sn(self):
        return self.sn

    def getHeader(self):
        try:
            now_time = int(time.time() * 1000)
            now_time_md5 = hashlib.md5(str(now_time).encode()).hexdigest()

            if self.sn is None:
                return
            sn_md5 = hashlib.md5(self.sn.encode()).hexdigest()

            password_no_md5 = sn_md5.lower() + now_time_md5.lower()
            password = hashlib.md5(password_no_md5.encode()).hexdigest()
            return {
                "Time": str(now_time),
                "Password": password.lower(),
                "Appid": str(10000106),
                "Version": 'v1',
            }

        except Exception as exception:
            _LOGGER.error("SmartGatewayNativeAuthorizer error", exc_info=exception)

    # 获取场景列表
    def sceneList(self):
        Headers = self.getHeader()
        url = f"http://{self.ip_address}/smarthome/scenes"
        return requests.get(url, headers=Headers)

    # 获取设备属性: retry-超时重试的次数
    # def devicePost(self, params):
    #     Headers = self.getHeader()
    #     url = f"http://{self.ip_address}/smarthome/devices/properties/realtime"
    #     data = {
    #         'properties': params
    #     }
    #     return requests.post(url, headers=Headers, json=data)
    def devicePost(self, params, retry=3):
        Headers = self.getHeader()
        url = f"http://{self.ip_address}/smarthome/devices/properties/realtime"
        data = {
            'properties': params
        }

        for attempt in range(retry):
            try:
                response = requests.post(url, headers=Headers, json=data, timeout=10)
                response.raise_for_status()
                return response.json()['result']['deviceProperty']
            except requests.exceptions.Timeout:
                _LOGGER.error(f"{params}请求超时, 重试中... ({attempt + 1}/{retry})")
                if attempt == retry - 1:
                    _LOGGER.error("超时重试失败...")
                    return False
            except requests.exceptions.HTTPError as http_err:
                _LOGGER.error(f"HTTP error: {http_err}")
                return False
            except Exception as err:
                _LOGGER.error(f"An unexpected error occurred: {err}")
                return False
        return False

    # 获取设备列表
    def deviceList(self):
        Headers = self.getHeader()
        print(Headers)
        url = f"http://{self.ip_address}/smarthome/devices"
        return requests.get(url, headers=Headers)

    # 设备控制
    def device_control(self, data, address):
        try:
            Headers = self.getHeader()
            return requests.post(f"http://{self.ip_address}/smarthome/devices/{address}/control", headers=Headers, json=data)
        except requests.exceptions.RequestException as e:
            print('请求失败:', e)
            return False  # 返回默认值

    # 批量设备控制
    def batch_device_control(self, data):
        try:
            Headers = self.getHeader()
            params = {"devices": data}
            return requests.post(f"http://{self.ip_address}/smarthome/devices/control", headers=Headers, json=params)
        except requests.exceptions.RequestException as e:
            print('请求失败:', e)
            return False  # 返回默认值

    async def getDevice(self, hass):
        try:
            response = await hass.async_add_executor_job(self.deviceList)
            return response.json()['result']['elements']
        except requests.exceptions.RequestException as e:
            print('请求失败:', e)
            return False  # 返回默认值

    async def getScene(self, hass):
        try:
            response = await hass.async_add_executor_job(self.sceneList)
            return response.json()['result']['elements']
        except requests.exceptions.RequestException as e:
            print('请求失败:', e)
            return False  # 返回默认值
    # 获取设备
    # async def getProperties(self, hass, params):
    #     try:
    #         response = await hass.async_add_executor_job(self.devicePost, params)
    #         response.raise_for_status()  # 检查请求是否成功
    #         device_property = response.json()['result']['deviceProperty']
    #         if device_property and len(device_property) > 0:
    #             return device_property
    #         else:
    #             return False
    #     except requests.exceptions.RequestException as e:
    #         print('请求失败:', e)
    #         return False  # 返回默认值
    async def getProperties(self, hass, params):
        device_property = await hass.async_add_executor_job(self.devicePost, params)
        return device_property if device_property else False
