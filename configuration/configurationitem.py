# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles a sub part of the configuration.
"""

import re
import os
import datetime

class DSConfigurationItem:
    """This class describes a generic item from a part of configuration"""

    EVALUATION_REGEX = re.compile(r"\$\{([^\$\{\}]*)\}")
    MAX_CHANGES = 5
    MASK_HIDDEN = "*"

    @property
    def root(self):
        """Retrieve the configuration root"""
        return self.__root

    @property
    def items(self):
        """Retrieve the current configuration items"""
        return self.__items

    def keys(self):
        """Retrieve the current configuration keys"""
        return self.__items.keys()

    def to_dict(self):
        """Convert the item to a dict"""
        def subitem(item):
            items = []
            for value in item:
                if isinstance(value, (list, tuple)):
                    items.append(subitem(value))
                elif isinstance(value, DSConfigurationItem):
                    items.append(value.to_dict())
                else:
                    items.append(self.__evaluate(value))
            return items

        items = {}
        for key, value in self.__items.items():
            if not key in self.__masks:
                if isinstance(value, (list, tuple)):
                    items[key] = subitem(value)
                elif isinstance(value, DSConfigurationItem):
                    items[key] = value.to_dict()
                else:
                    items[key] = self.__evaluate(value)
        return items

    def __evaluate(self, value):
        """This function replaces the substitution strings into a field from the configuration.

        The format of this kind of string is '${KEY}' or '${KEY?DefaultValue}

        Where KEY can be another configuration item (.item.subitem from the root, or item.subitem from the current item)
              KEY can be a keyword (VERSION or APPLICATION)
              KEY can be an environment variable

        The character '?' means that if the KEY doesn't exist the default value replace it.

        Sample :
            ${PWD}/config => /home/developer/workspace/SDK/config
            ${ENV_NOT_FOUND?hello world}/config => hello world/config
            ${name} - ${version} => PySyncytium - v0.0.0.0
            ${triggers.csv.filename} => fait référence au nom du fichier csv "filename" du trigger "csv"
            ${triggers.${environment.name}.filename} => fait référence au nom du fichier csv "filename" du trigger
            dont l'alias a la même valeur que le nom de l'environnement
        """

        def replace_key(match):
            key = match.group(1)
            default_value = ""
            if "?" in key:
                default_value = key.split("?")[1]
                key = key.split("?")[0]
            value = default_value

            # Check keywords

            if key == 'VERSION':
                try:
                    value = self.root.version
                except:
                    pass
                return value
            if key == 'APPLICATION':
                try:
                    value = self.root.application
                except:
                    pass
                return value
            if key.startswith("date:"):
                try:
                    value = datetime.datetime.now().strftime(key[5:])
                except:
                    pass
                return value

            # Check existing the configuration item

            if key[0] == '.':
                value = self.root.get(key[1:])
            else:
                value = self.get(key)
            if value is not None:
                return value

            # Check environment variable

            value = os.getenv(key)
            if value is None:
                return default_value
            return value

        if not isinstance(value, str):
            return value

        # on autorise jusqu'à 5 référence de référence
        # Exemple de référence de référence : ${parameters.${environment.name}.value}

        try:
            i = 0
            change = True
            while i < self.MAX_CHANGES and change:
                previousvalue = value
                value = self.EVALUATION_REGEX.sub(replace_key, value)
                change = value != previousvalue
                i += 1
        except:
            # ignore l'exception et retourne la valeur dans l'état où elle est ...
            pass

        return value

    def get(self, key, default_value = None):
        """
        Retrieve a value from a key, describing a path of a value from the current item
        if the key doesn't exist, the default value is retrieved
        """
        item = self
        for itemkey in key.split('.'):
            try:
                item = item.items[itemkey]
            except:
                for i, itemkey in enumerate(itemkey.split('[')):
                    if i == 0:
                        try:
                            item = item.items[itemkey]
                        except:
                            return default_value
                    else:
                        if itemkey[-1] != ']':
                            return default_value
                        try:
                            item = item[int(itemkey[:-1])]
                        except:
                            return default_value
        return self.__evaluate(item)

    def __getattr__(self, name):
        if name in self.__items:
            return self.__evaluate(self.__items[name])
        raise KeyError(f"Field '{name}' not found in record.")

    def __getitem__(self, name):
        if name in self.__items:
            return self.__evaluate(self.__items[name])
        raise KeyError(f"Field '{name}' not found in record.")

    def __init__(self, root, item):
        def subitem(root, item):
            items = []
            for value in item:
                if isinstance(value, (list, tuple)):
                    items.append(subitem(root, value))
                elif isinstance(value, dict):
                    items.append(DSConfigurationItem(root, value))
                else:
                    items.append(value)
            return items

        self.__dict__["_DSConfigurationItem__root"] = root
        items = {}
        masks = []
        for key, value in item.items():
            if key.endswith(self.MASK_HIDDEN):
                key = key[0:-len(self.MASK_HIDDEN)]
                masks.append(key)
            if isinstance(value, dict):
                items[key] = DSConfigurationItem(root, value)
            elif isinstance(value, (list, tuple)):
                items[key] = subitem(root, value)
            else:
                items[key] = value
        self.__dict__["_DSConfigurationItem__items"] = items
        self.__dict__["_DSConfigurationItem__masks"] = masks
