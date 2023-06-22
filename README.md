# Potnanny
*"Plant care when you're not there!"*

Potnanny turns your Raspberry Pi into powerful grow-room automation system
using inexpensive, off-the-shelf Bluetooth sensors, power outlets, and other devices.
The basic installation allows you to monitor 1 grow room, with 5 devices.

## Description
Potnanny provides a simple dashboard for monitoring and insight into your grow environment.
<img src="/docs/screenshots/dashboard.png" width="400">

Clicking on any of the dashboard values will show graph trends.
<img src="/docs/screenshots/graph.png" width="400">

## Advanced Controls
Beyond basic monitoring, Potnanny also makes it possible to configure Schedules and Smart Controls of the bluetooth power outlets.
A Smart Control is like saying "When the humidiy reading of a sensor is over 65%, turn the fan outlet on".
- Turns *dumb* devices (humidifiers, fans, etc) into *smart* devices.
- Saves energy. Turning fans and dehumidifiers on only when needed reduces energy consumption.
- Automate your irrigation, ventilation, and temperature controls to maintain an ideal growing environment.

## Reliable
Potnanny does not rely on WiFi or cloud-connectivity. So even if your internet goes down, Potnanny will continue to work to control your environment. Once your Potnanny system is configured the way you want, it is very much a *set it and forget it* system.

## Hotspot
Most users will want to connect their Potnanny controller to their home WiFi network. But, If your grow is in a remote area without WiFi, Potnanny will automatically become its own WiFi hotspot (SSID=PNCTRL) you can connect to with a mobile device. Log into the system with your phone's web browser.

## Supported Bluetooth Devices
This list includes only hygrometers, soil sensors, and power outlets that we have tested and found to have good, stable communication.

- Govee H5080 Bluetooth Outlet
- Govee H5082 Bluetooth Dual Outlet
- Smartbot PLUS Bluetooth Hygrometer
- Smartbot Bluetooth Hygrometer
- Xiaomi Mi Bluetooth Soil Sensor
- Xiaomi Mi MJHT Bluetooth Hygrometer

We are constantly working to write new plugins for bluetooth devices. So this list may grow over time.

## Expandable Plugin System
All communication to bluetooth and GPIO devices is based on plugins.
You are free to write and install your own plugins, in order to communicate with new devices.
See the Plugin Documentation for more.

## Hardware Requirements
Potnanny was written specifically targeting the low-priced Raspberry Pi Zero W.
<img src="/docs/screenshots/rpizerow.png" width="400">

But it will work on most models with integrated WiFi and Bluetooth.
- Raspberry Pi Zero W
- Raspberry Pi Zero W2
- Raspberry Pi 3 B+
- Raspberry Pi 4

## OS Requirements
32-bit Raspberry Pi OS Bullseye is the minimum recommended OS.
64-bit versions will not work on the original Raspberry Pi Zero W

## Python Requirements
Python 3.9 is the minimum requirement (included with Raspberry Pi OS Bullseye version)

## Installation
```
pip install potnanny
```

## Startup
```
potnanny start
```

## Login
Using a web browser, connect to "http://potnanny.local"
The initial login/password is set to "admin/potnanny!". Please secure your system and reset the password as soon as you log in for the first time.
