# NEXhome
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Stable](https://img.shields.io/github/v/release/nexhome-org/nexhome-homeassistant-component)](https://github.com/nexhome-org/nexhome-homeassistant-component/releases/latest)

English | [简体中文](https://github.com/nexhome-org/nexhome-homeassistant-component/blob/main/README.zh-CN.md)

Control your NEXhome smart devices through the local area network

- Complete device configuration through the Home Assistant UI.
- Generate additional sensors and switches for easy device control.
- Synchronize device status in real time.

⭐ If this little project brightened your day, why not sprinkle some stardust our way? A quick star from you would rocket our motivation to the moon! 🚀

## Supported devices

| Device Model | Name                            |
|--------------|---------------------------------|
| 1            | Light                           | 
| 2            | Dimming light                   | 
| 3            | Air conditioner                 |
| 5            | Temperature and humidity sensor |
| 6            | Curtain                         | 
| 10           | Fresh air                       | 
| 11           | Floor heating                   | 
| 12           | Air detector                    |
| 51           | Color temperature light         |
| 107          | Air conditioner（mode floor heating）         |
| 132          | Atomized glass                  |
| 133          | Exhaust fan                     |
## Install or Upgrade

Choose one of the following two installation/upgrade methods.
Do not install using one method and then upgrade using another method, as this may cause problems.

### Automatic installation via HACS

1. Open Home Assistant's HACS page.
2. Click `integrations`。
3. Click on `ADD INTEGRATION ` in the bottom right corner.
4. Find `NEXhome` in the newly opened page and install it.  
   **Note**：If you have just installed HACS or the network is not smooth, you may not see the `NEXhome` plugin.
If you can't find this plugin in HACS, you can use the manual installation method below.
5. Restart Home Assistant.

- **To upgrade:** When you open the HACS page, an upgrade prompt will automatically appear. Just follow the prompts.

### Manual installation
1. Download the plugin [zip archive](https://github.com/nexhome-org/nexhome-homeassistant-component/archive/refs/heads/main.zip) (this link is always the latest version).
2. Open the `nexhome-homeassistant-component-main`/`custom_components` folders in the archive one by one.
3. Copy the `nexhome` folder in the folder to the `custom_components` folder in your HA installation directory.
4. Restart Home Assistant.

> If you don't know your HA installation directory: In HA, click on `Configuration`-`Information` at the bottom，The `configuration.yaml path` on the page is your HA installation directory. 
> If there's no`custom_components` folder, you can create one yourself.

- **To upgrade** : After downloading the latest version of the plugin zip file, follow the above method to overwrite the existing files.

## Usage
Connect the central control gateway to the home LAN, obtain the IP address and IOTID through the **Engineering APP** or **AIHome**, and enter them into the configuration items

## Debug
To turn on debug log output, configure as follows in configuration.yaml
```yaml
logger:
  default: warn
  logs:
    custom_components.NEXhome: debug
```
