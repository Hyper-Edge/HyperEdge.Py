from .types import *
from .models import DataModelTemplate
from .data import BaseData


class Reward(object):
    _assets: typing.List[typing.Tuple[DataModelTemplate, int]]
    _items: typing.List[typing.Tuple[BaseData, int]]

    def __init__(self, name: str = ''):
        self._name = name
        self._assets = []
        self._items = []

    @property
    def items(self):
        return iter(self._items)

    def add(self, item, amount: int = 1):
        if isinstance(item, BaseData):
            self._items.append((item, amount))
        elif isinstance(item, DataModelTemplate):
            self._assets.append((item, amount))
        else:
            assert False
        return self

    def to_dict(self):
        return dict(
            Erc721Rewards=[],
            Erc1155Rewards=[dict(
                ItemId=item.id,
                Amount=amount
            ) for item, amount in self._items]
        )
