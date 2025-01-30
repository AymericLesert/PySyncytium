import copy

class DSDatabase:
    def __getattr__(self, name):
        return self.__tables[name]

    def __init__(self, tables):
        self.__tables = copy.deepcopy(tables);
