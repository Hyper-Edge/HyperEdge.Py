from {{ cookiecutter.project_slug }}.sdk.models import BaseData, DataRef

import inflection


class Inventory(object):
    _registry = {}

    def __init__(self, name='UserInventory'):
        self._name = name
        self._items = {}
        #
        if name in Inventory._registry:
            raise Exception(f"Inventory with name '{name}' already defined")
        Inventory._registry[name] = self

    @staticmethod
    def all():
        return Inventory._registry.values()

    @staticmethod
    def user():
        global _default_inventory
        return _default_inventory

    @property
    def name(self):
        return self._name

    def add(self, item: BaseData):
        if item.id in self._items:
            raise Exception(f"Inventory already have item with id='{item.id}'")
        self._items[item.id] = item
        return self

    def to_dict(self):
        return dict(
            Name=self._name,
            Items=[dict(Id=item.id, Typename=inflection.camelize(type(item).__name__)) for item in self._items.values()]
        )


_default_inventory = Inventory()