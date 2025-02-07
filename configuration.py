import os
import yaml
import json

def get_configuration(filename, items = None, root = './'):
    if filename is not None:
        items = filename

    if isinstance(items, str):
        if os.path.exists(root + items):
            filename = root + items
            with open(filename, 'r', encoding="utf-8") as file:
                subitems = get_configuration(None, yaml.safe_load(file), os.path.dirname(filename) + '/')
            if subitems is None:
                return {}
            return subitems

        return items

    if isinstance(items, list):
        newitems = []
        for value in items:
            newitems.append(get_configuration(None, value, root))
        return newitems

    if isinstance(items, dict):
        newitems = {}
        for key, value in items.items():
            newitems[key] = get_configuration(None, value, root)
        return newitems

    return items

print(json.dumps(get_configuration('config.yml'), sort_keys=False, indent=2))