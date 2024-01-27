import copy
import logging
from potnanny.plugins.base import (BluetoothDevicePlugin, GPIODevicePlugin,
    ActionPlugin, PipelinePlugin)
from potnanny.models.keychain import Keychain


logger = logging.getLogger(__name__)


class InterfaceMixin:
    """
    Many Models have an "interface" attribute, which is a string reference to
    a plugin class. This mixin searches for the actual plugin class
    """

    @classmethod
    def interface_class(cls, name:str):
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
        except Exception as x:
            logger.warning(str(x))
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
            results = await Keychain.select().where(
                Keychain.name == self._keychain_name)
            if results:
                self._keychain = results[0]

    @property
    def keychain(self):
        return self._keychain


class DeviceMixin(PluginMixin):
    """
    Add ability for device to interact with plugins/controllers
    """

    async def poll(self):
        """
        Poll our plugin instance for measurements, if possible
        """

        if (not hasattr(self.plugin, 'is_pollable') or
            self.plugin.is_pollable is not True):
            return None

        results = {
            'id': self.id,
            'name': self.name,
            'values': {},
        }

        try:
            values = await self.plugin.poll()
            results.update({'values': values})
        except Exception as x:
            logger.warning(str(x))

        return results


    def read_advertisement(self, device, advertisement):
        """
        Use plugin instance to decode the BLE advertisement data
        args:
            the device reporting data
            the advertisement data
        returns:
            dict, or None
        """

        if (not hasattr(self.plugin, 'is_reader') or
            self.plugin.is_reader is not True):
            return None

        results = {
            'id': self.id,
            'name': self.name,
            'values': {},
        }

        try:
            values = self.plugin.read_advertisement(device, advertisement)
            if values:
                results['values'] = values
        except:
            pass

        return results


    async def on(self, outlet:int = 1):
        """
        Switch device ON
        """

        if (not hasattr(self.plugin, 'is_switchable') or
            self.plugin.is_switchable is not True):
            return None

        result = await self.plugin.on(outlet)
        return result


    async def off(self, outlet:int = 1):
        """
        Switch device OFF
        """

        if (not hasattr(self.plugin, 'is_switchable') or
            self.plugin.is_switchable is not True):
            return None

        result = await self.plugin.off(outlet)
        return result


    async def set_value(self, data:dict):
        """
        Set key/value data on device (future?).
        """

        if (not hasattr(self.plugin, 'is_settable') or
            self.plugin.is_settable is not True):
            return None

        if type(data) is not dict:
            logger.warning(f"Expecting dict but got {type(data)}")
            return None

        try:
            result = await self.plugin.set_value(data)
            return result
        except Exception as x:
            logger.warning(str(x))
            return None
