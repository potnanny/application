import re
import logging
from potnanny.plugins.base import (BluetoothDevicePlugin, GPIODevicePlugin, 
    ActionPlugin, PipelinePlugin)

logger = logging.getLogger(__name__)


class PluginInterfaceMixin:
    @property
    def plugin(self):
        """
        Attribute to fetch an instantiated copy of our interfaces plugin.

        Required object attributes:
            - interface = like 'input.ble.govee.Hygrometer'
            - attributes = like {'address': '11:22:33:44:55:66'}
        """

        collection = [BluetoothDevicePlugin, GPIODevicePlugin,
            ActionPlugin, PipelinePlugin]

        if not hasattr(self, '_plugin'):
            self._plugin = None

        for p in collection:
            if self._plugin is not None:
                break

            try:
                klass = p.get_named_class(self.interface)
                self._plugin = klass(**self.attributes)
                break
            except Exception as x:
                logger.debug(x)

        try:
            # set up plugin specific introspection attributes, like:
            #   - is_bluetooth, 
            #   - is_gpio, 
            #   - is_reader, 
            #   - is_pollable, 
            #   - is_switchable, 
            #   - is_key_required, etc

            if hasattr(self._plugin, 'poll') and callable(self._plugin.poll):
                setattr(self._plugin, 'is_pollable', True)

            if isinstance(self._plugin, BluetoothDevicePlugin):
                setattr(self._plugin, 'is_bluetooth', True)
                if (hasattr(self._plugin, 'read_advertisement') and 
                    callable(self._plugin.read_advertisement)):
                    setattr(self._plugin, 'is_reader', True)
            elif isinstance(self._plugin, GPIODevicePlugin):
                setattr(self._plugin, 'is_gpio', True)
  
            if (hasattr(self._plugin, 'set_state') and 
                callable(self._plugin.set_state)):
                setattr(self._plugin, 'is_switchable', True)

            if hasattr(self._plugin, 'key_code'):
                setattr(self._plugin, 'is_key_required', True)

        except Exception as x:
            logger.debug(x)

        return self._plugin


class FingerprintReader:
    """
    This is a class mixin for BLE plugins, to be able to recognize a
    BLE device that can be communicated with (by its device address or name)
    
    Each entry in a class fingerprint definition must match, in order for
    this to return True.
    """

    @classmethod
    def recognize_this(cls, fp):
        if not hasattr(cls, 'fingerprint'):
            logger.warning("Class %s no fingerprint defined" % cls)
            return False

        for key, regex in cls.fingerprint.items():
            if key not in fp:
                return False

            if not regex.search(fp[key]):
                return False

        return True

