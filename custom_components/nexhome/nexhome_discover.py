import asyncio
import socket
from .const import DEVICES, DOMAIN
from .utils import format_upd_mes
import time
async def get_entity_by_unique_id(hass, unique_id):
    entity_registry = await async_get_entity_registry(hass)
    
    # 从实体注册表中获取实体条目
    entry = entity_registry.async_get_by_unique_id(unique_id)
    
    if entry is None:
        return None

    # 获取实体实例
    entity = hass.states.get(entry.entity_id)

    return entity

def build_ssdp_message(host, model):
    message = f"M-SEARCH * HTTP/1.1\r\n"
    message += f"HOST: {host}\r\n"
    message += f"ST: nsdp:all\r\n"
    message += f"MAN: nsdp:discover\r\n"
    message += f"MODEL: {model}\r\n"
    message += f"USN: 80e6f61f5869453b8f8c3212a50ed667\r\n"
    message += f"SN: 1\r\n"
    message += "\r\n"
    return message.encode("utf-8")

MES = (
    b'M-SEARCH * HTTP/1.1\r\n'
    b'HOST: 127.0.0.1:1912\r\n'
    b'ST: nsdp:all\r\n'
    b'MAN: "urn:schemas-upnp-org:service:WANIPConnection:1"\r\n'
    b'USN: uuid:0e6f61f58694538b8f8c3212a50ed677::urn:schemas-upnp-org:service:WANIPConnection:1\r\n'
    b'SN: 1\r\n'
    b'\r\n'
)
class UDPListener(asyncio.DatagramProtocol):

    def __init__(self, hass, callback=None):
        self.hass = hass
        self._listeners = []
        self._callback = callback

    async def start(self):
        loop = asyncio.get_running_loop()
        listener = loop.create_datagram_endpoint(
            lambda: self, local_addr=("0.0.0.0", 1912), reuse_port=True
        )
        self._listeners = await asyncio.gather(listener)

    def close(self):
        self._callback = None
        for transport, _ in self._listeners:
            transport.close()
            
    def datagram_received(self, data, addr):
        try:
            content, headers = format_upd_mes(data)
            devices = self.hass.data[DOMAIN][DEVICES]

            # 解析HTTP头部信息
            host = headers.get("HOST")
            nts = headers.get("NTS")
            model_info = headers.get("MODEL")

            # 解析模型信息里的键值对
            model_params = {}
            for param in model_info.split("&"):
                key, value = param.split("=")
                model_params[key] = value


            # entity_registry = async_get_registry(self.hass)
            # if devices:
            #     for device in devices:
            #         identifier = model_params.get("identifier")
            #         device_id = device.get("device_id")
            #         if device.get("address") == model_params.get("address"):
            #             entity_id = f"{DOMAIN}.{device_id}"
            #             # 获取实体
            #             entity = get_entity_by_unique_id(self.hass, entity_id)
            #             print(entity)
            #             # 更新实体属性并安排状态更新
            #             if entity is not None:
            #                 device[identifier]= value
            #                 self.hass.add_job(entity.async_schedule_update_ha_state())
            if devices:
                for device in devices:
                    device_address = device.get("address")
                    identifier = model_params.get("identifier")
                    if device_address == model_params.get("address"):
                        device[identifier]= value
            print(model_params)
        except Exception as exception:
            print(exception)


# 客户端推送消息
def send_test_message(host, port=1912, message=MES, timeout=5):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.sendto(message, (host, port))
            print("send....")
        except Exception:
            print(f"Can't access network {host}")
            return

        deadline = time.time() + timeout
        while time.time() < deadline:
            sock.settimeout(deadline - time.time())  # 设置剩余超时时间
            try:
                received_data, server_address = sock.recvfrom(1024)
                content, headers = format_upd_mes(received_data)
                location = headers.get("LOCATION")
                key, value = location.split("://")
                return value
                # 收到数据后退出循环
            except socket.timeout:
                print(f"No response received within {timeout} seconds.")
                break
            except Exception as e:
                print(f"An error occurred while receiving: {e}")
                break

async def discover(hass):
    discovery = UDPListener(hass)
    try:
        await discovery.start()
        return discovery
    except Exception as ex:
        print(f"Error starting UDP listener: {ex}")
        raise