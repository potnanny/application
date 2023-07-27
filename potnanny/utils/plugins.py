import os
import re
import sys
import glob
import logging
import importlib
import types
from potnanny.utils import resolve_path

logger = logging.getLogger(__name__)

def load_plugins(path):
    """
    Load plugins from named path
    """

    files = []
    forbidden = ('.', '_', '__init__.py')

    path = resolve_path(path)
    logger.debug("Loading plugins from %s" % path)
    if not os.path.exists(path):
        raise IOError("Plugin path '%s' does not exist" % path)

    for dir, subdirs, flist in os.walk(path):
        subdirs[:] = [ d for d in subdirs if not d.startswith(forbidden) ]

        for f in flist:
            fpath = os.path.join(dir, f)
            if f.endswith('.py') and f not in forbidden:
                files.append(fpath)

    for f in files:
        try:
            # build plug module name like 'input.ble.govee.Hygrometer'
            tree = re.split(r'\\|/', re.sub(path, '', f))
            tree[-1] = tree[-1].split('.')[0]
            mod_name = '.'.join(tree[1:])
            loader = importlib.machinery.SourceFileLoader(mod_name, f)
            mod = types.ModuleType(loader.name)
            loader.exec_module(mod)
            logger.info("Loaded plugin %s" % mod_name)
        except Exception as x:
            logger.warning(str(x))
