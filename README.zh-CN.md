# NEXhome
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Stable](https://img.shields.io/github/v/release/nexhome-org/nexhome-homeassistant-component)](https://github.com/nexhome-org/nexhome-homeassistant-component/releases/latest)

[English](https://github.com/nexhome-org/nexhome-homeassistant-component/blob/main/README.md) | 简体中文

通过本地局域网控制你的NEXhome智能设备

- 通过Home Assistant UI完成设备的配置.
- 生成额外的传感器和开关方便进行设备控制.
- 实时同步设备状态.

⭐如果本集成对你有所帮助, 请不吝为它点个星, 这将是对我的极大激励。

## 已支持的设备

| 设备类型 | 名称     |
|------|--------|
| 1    | 灯      | 
| 2    | 调光灯    | 
| 3    | 空调     |
| 5    | 温湿度传感器 |
| 6    | 窗帘     | 
| 10   | 新风     | 
| 11   | 地暖     | 
| 12   | 空气检测仪  |
| 51   | 色温灯    |
| 107  | 空调（模式+地暖）    |
| 132  | 雾化玻璃   |
| 133  | 排风扇    |

## 安装或升级

以下两种安装/升级方法，选择其中一种即可。  
请不要使用一种方法安装然后用另一种方法升级，可能导致问题。

### 通过 HACS 自动安装

1. 打开 Home Assistant 的 HACS 页面。
2. 点击`集成`。
3. 点击右下角的`浏览并添加存储库`。
4. 在新打开的页面中找到`NEXhome`，安装即可。  
   **注意**：如果您刚刚安装好 HACS，或者网络不通畅，您可能看不到`NEXhome`插件。  
   如果在 HACS 中找不到此插件，可以使用下面的手动安装方法。
5. 重新启动 Home Assistant。

- **如需升级：** 在您打开 HACS 页面时，会自动出现升级提示。按照提示操作即可。

### 手动安装
1. 下载插件 [zip 压缩包](https://github.com/nexhome-org/nexhome-homeassistant-component/archive/refs/heads/main.zip)（该链接始终为最新版本）。
2. 依次打开压缩包中的`nexhome-homeassistant-component-main`/`custom_components`文件夹。
3. 将该文件夹中的`nexhome`文件夹拷贝至自己 HA 安装目录的`custom_components`文件夹。
4. 重新启动 Home Assistant。

> 若不知道自己的 HA 安装目录：在 HA 中点击`配置`-底部`信息`，页面中的`configuration.yaml 路径`即为 HA 的安装目录。  
> 若无`custom_components`文件夹，可自己新建。

- **如需升级：** 下载最新版插件压缩包后，按照上述方法，覆盖原有文件即可。

## 使用方法
将中控网关接入到家庭局域网中，通过**施工APP**或**AIHome**获取IP地址和IOTID，输入到配置项即可

## 调试
要打开调试日志输出, 在configuration.yaml中做如下配置
```yaml
logger:
  default: warn
  logs:
    custom_components.NEXhome: debug
```
