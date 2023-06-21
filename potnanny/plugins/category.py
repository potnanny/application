from .base import (DevicePlugin, BluetoothDevicePlugin, GPIODevicePlugin, 
    ActionPlugin, PipelinePlugin)

plugin_category_map = {
    'device': [DevicePlugin, BluetoothDevicePlugin, GPIODevicePlugin],
    'action': ActionPlugin,
    'pipeline': PipelinePlugin,
}
