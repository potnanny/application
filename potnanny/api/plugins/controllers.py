import logging
from potnanny.plugins.category import plugin_category_map


logger = logging.getLogger(__name__)


async def get_plugin_map() -> dict:
    """
    Get dict of plugins mapped by category
    """

    data = {}
    for k in plugin_category_map.keys():
        if k not in data:
            data[k] = []

        for klass in plugin_category_map[k]:
            for p in klass.plugins:
                try:
                    data[k].append(extract_plugin_data(p))
                except Exception as x:
                    logger.warning(x)

    return data


def extract_plugin_data(p) -> dict:
    data = {'interface': '.'.join((p.__module__, p.__name__))}

    try:
        data['name']  = p.name
    except:
        pass
    try:
        data['description'] = p.description
    except:
        pass

    return data
