import os
import logging
import yaml
from types import SimpleNamespace
from potnanny.models.interface import ObjectInterface
from potnanny.models.keychain import Keychain
from potnanny.utils import resolve_path


logger = logging.getLogger(__name__)
DB_PATH = resolve_path('~/potnanny/potnanny.db')
DEFAULTS = {
    'database_uri': 'sqlite+aiosqlite:///' + DB_PATH,
    'log_path': resolve_path('~/potnanny/errors.log'),
}


class Config:
    def __init__(self, **kwargs):
        self._file = resolve_path('~/potnanny/config.yml')
        self._yaml_loader = yaml.SafeLoader

        for k,v in kwargs.items():
            setattr(self, k, v)

        self._load_file()


    @classmethod
    async def load(cls):
        """
        Load config settings from database keychain.
        Ensure DB has been initiated before running this!
        """

        self = cls()
        obj = await ObjectInterface(Keychain).get_by_name('settings')
        self._load_data(obj.attributes)

        return self


    def __iter__(self):
        """
        Set up iter, so our object can be dumped correctly with dict(obj)
        """

        for k in self.__dict__.keys():
            if not k.startswith("_") and not k.startswith("load"):
                yield (k, self._ns_to_dict(getattr(self, k)))
            else:
                continue


    def _ns_to_dict(self, data):
        """
        If item is a SimpleNamespace, convert to dict, else return item.

        args:
            an object
        returns:
            object, or dict
        """

        if type(data) is SimpleNamespace:
            return {k: self._ns_to_dict(v) for k, v in data.__dict__.items()}

        return data


    def _dict_to_ns(self, data):
        """
        If item is a dict, convert to a SimpleNamespace, else return item.

        args:
            an object
        returns:
            object, or SimpleNamespace
        """

        if type(data) is not dict:
            return data

        ns = SimpleNamespace()
        for k,v in data.items():
            setattr(ns, k, self._dict_to_ns(v))

        return ns


    def _load_data(self, data):
        """
        Set dict values as self attributes
        """

        for k, v in data.items():
            setattr(self, k, self._dict_to_ns(v))


    def _load_file(self):
        """
        Load config data from the default file
        """

        if not os.path.exists(self._file):
            logger.debug(f"Creating initial config file {self._file}")
            self._dump_yaml_config(DEFAULTS, self._file)

        logger.debug(f"Reading config {self._file}")
        with open(self._file, 'r', encoding='utf-8') as fh:
            data = yaml.load(fh, Loader=self._yaml_loader)
            self._load_data(data)


    def _dump(self):
        """
        Dump config data to default file
        """

        logger.debug(f"Dumping config to file {self._file}")
        self._dump_yaml_config(dict(self), self._file)


    def _dump_yaml_config(self, data, path):
        """
        Dump dict as yaml to named file.

        args:
            - dict
            - pathname
        """

        with open(path, 'w', encoding='utf-8') as fh:
            yaml.dump(data, fh)
