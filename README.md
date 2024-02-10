# Potnanny
*"Plant care when you're not there!"*

Potnanny turns your Raspberry Pi into powerful grow-room automation system
using inexpensive, off-the-shelf Bluetooth sensors, power outlets, and other devices.

## Description
Potnanny provides a simple dashboard for monitoring your grow environment.

<img src="/docs/screenshots/dashboard.png" width="400">

Clicking on any of the dashboard values will show graph trends.

<img src="/docs/screenshots/graph.png" width="400">

## Hardware Requirements
Potnanny was written specifically targeting the low-priced Raspberry Pi Zero W.

<img src="/docs/screenshots/rpizerow.png" width="300">

But it will work on most models with integrated WiFi and Bluetooth.
- Raspberry Pi Zero W
- Raspberry Pi Zero W2
- Raspberry Pi 3B+
- Raspberry Pi 4
- Raspberry Pi 5

## OS Requirements
32-bit Raspberry Pi OS "Bookworm" (Debian 12.0) is the minimum recommended OS.
64-bit versions will not work on the original Raspberry Pi Zero W. But may work on other models.

## Python Requirements
Python 3.11 is the minimum requirement (included with Raspberry Pi OS *Bookworm* version, or higher)

## Installation
The recommended way to install potnanny, is with the installer script found at https://github.com/potnanny/installer
This script will handle the installation, as well as permissions, web server setup, certificates, secret codes, and other items.

## Smart Controls
Beyond basic monitoring, Potnanny also makes it possible to configure Smart Controls of the bluetooth power outlets.

A Smart Control is like saying "When the humidity reading of a sensor is over 65%, turn the dehumidifier outlet on".

Potnanny's Smart Controls:
- Turn simple devices (humidifiers, fans, etc) into *smart* devices.
- Saves energy. Turning fans and dehumidifiers on only when actually needed reduces energy consumption.
- Automate your irrigation, ventilation, and temperature controls to maintain the ideal growing environment.

## Reliable
Potnanny does not rely on WiFi or cloud-connectivity. So even if your home internet goes down, Potnanny will continue working to maintain your environment. Once your Potnanny system is configured the way you want, it is very much a *set it and forget it* system. It is not fancy. It just does what you want.

## Supported Bluetooth Devices
This list includes only hygrometers, soil sensors, and power outlets that we have tested and found to have good stable communication.

- Govee H5080 Bluetooth Outlet
- Govee H5082 Bluetooth Dual Outlet
- Smartbot PLUS Bluetooth Hygrometer
- Smartbot Bluetooth Hygrometer
- Xiaomi Mi Bluetooth Soil Sensor
- Xiaomi Mi MJHT Bluetooth Hygrometer

We are constantly looking out for new bluetooth devices that would be useful to home growers, and writing new plugins. So this list will grow in the future.

## Expandable Plugin System
All communication to bluetooth and GPIO devices is based on plugins.
You are free to write and install your own device plugins.
See the Plugin Documentation for more.

## Basic Install
```
pip3 install potnanny
```

## Startup
```
potnanny start
```

## Login
Using a web browser, connect to https://potnanny.local
The initial login/password is set to "admin/potnanny!". Please secure your system and reset the password as soon as you log in the first time.
NOTE: *If the address above cannot be reached on your wifi network, you may need to check your wifi network admin tool, to find the IP address assigned to your raspberry pi.
Then, access it by that address. Like, https://192.168.1.14*

## Navigation
Clicking on the POTNANNY logo will return you to the main dashboard page.
The navigation menu button is the *hamburger* logo in the top-right corner of the page.

## System Settings
Click the menu button, and select the *Settings* page.
By default, device temperatures are stored and displayed in Fahrenheit. This can be changed on the settings page.
(Note: After changing *Temperature Display, Polling Interval, Leaf Temperature Offset, or Measurement Retention settings* you must reboot the Pi to register the changes).

## Initial Setup
Before performing the initial setup, ensure your bluetooth devices are nearby and are powered on.

1. On the main screen, press the button labeled "+" to create a new room. Give the room a useful name, like "Grow Tent 1"
2. Go to the menu, and select the *Devices* page.
3. Press the *Discover New Devices* button.
4. Wait for the devices to be discovered and displayed on the page.
5. Click on the devices and assign them to your room (Potnanny will not collect measurements from any device until they are assigned to a room)

## Setting up the power outlets
The Govee H5080 and H5082 require a secret code to communicate with them. You must press the "Capture" button on the device page, then wait for the light on the outlet to turn blue. Then, slowly press the outlet button 3 or 4 times to send the code to the potnanny software.

## Configuring Smart Controls for an outlet
To configure a smart-control for a power outlet, click on the outlet control button (center)
<img src="/docs/screenshots/outlet_control.png" width="400">
Then, you will assign:
- which device (like, a thermometer) will control the outlet.
- what measurement from that device will control the outlet.
- when will the outlet turn ON? (for example, when humidity is greater than 60)
- when will the outlet turn OFF? (for example, when the humidity is below 55)

A smart control can also use a short timed-on setting. This can be useful for situations where an outlet should power on for a short time, instead of waiting the full 10 minutes for the next measurment polling interval.
For instance, turn on an irrigation system on for 60 seconds, when soil mositure is below 15%
