import re
import logging
import copy
from potnanny.plugins.base import (BluetoothDevicePlugin, GPIODevicePlugin,
    ActionPlugin, PipelinePlugin)
from potnanny.models.interface import ObjectInterface
from potnanny.models.keychain import Keychain
logger = logging.getLogger(__name__)


class InterfaceMixin:
    """
    Many Models have an "interface" attribute, which is a string reference to
    a plugin class. This mixin searches for the actual plugin class
    """

    @classmethod
    def interface_class(cls, name):
        klass = None
        parents = [BluetoothDevicePlugin, GPIODevicePlugin,
            ActionPlugin, PipelinePlugin]

        for p in parents:
            klass = p.get_named_class(name)
            if klass is not None:
                break

        return klass


class PluginMixin(InterfaceMixin):
    """
    Class for interfacing with Plugin object instance via the $parent.plugin property
    """

    @property
    def plugin(self):
        """
        Attribute to fetch an instantiated copy of our interfaces plugin.

        Required object attributes:
            - interface = like 'input.ble.govee.Hygrometer'
            - attributes = like {'address': '11:22:33:44:55:66'}

        Now, can communicate with the instance directly with initialized
        instance with self.plugin
        """

        if not hasattr(self, '_plugin'):
            self._plugin = None

        try:
            klass = self.interface_class(self.interface)
            self._plugin = klass(**self.attributes)
        except:
            pass

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
        except:
            pass

        return self._plugin


class KeychainMixin:
    """
    A mixin class for a plugin (especially plugins that inherit from the
    ActionPlugin class) that must be associated with a named keychain.
    This requires the plugin has a self._keychain_name attribute.
    The keychain must be loaded async during setup:
        await self._load_my_keychain()

    Then, the plugin can access it's keychain data like:
        self.keychain.attributes
    """

    async def _load_my_keychain(self):
        if not hasattr(self, '_keychain'):
            self._keychain = None

        if not hasattr(self, '_keychain_name'):
            self._keychain_name = ''

        if self._keychain is None:
            self._keychain = await ObjectInterface(Keychain).get_by_name(
                self._keychain_name)

    @property
    def keychain(self):
        return self._keychain


class FingerprintMixin:
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
