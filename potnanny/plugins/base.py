class PluginBase(type):
    """
    This class is the base for all plugins
    """

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            if cls not in cls.plugins:
                cls.plugins.append(cls)

class PluginFinder:
    @classmethod
    def get_named_class(cls, name):
        for p in cls.plugins:
            klass = '.'.join((p.__module__, p.__name__))
            if klass == name:
                return p

        return None


class DevicePlugin(PluginFinder, metaclass=PluginBase):
    # DEPRACATED class, Jan 2023
    pass

class BluetoothDevicePlugin(PluginFinder, metaclass=PluginBase):
    pass

class GPIODevicePlugin(PluginFinder, metaclass=PluginBase):
    pass

class ActionPlugin(PluginFinder, metaclass=PluginBase):
    pass

class PipelinePlugin(PluginFinder, metaclass=PluginBase):
    pass

