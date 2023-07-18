from .types import *
from .base import _BaseModel
from .data import BaseData


class Reward(object):
    _items: typing.List[typing.Tuple[BaseData, int]]

    @property
    def items(self):
        return iter(self._items)

    def __getattr__(self, item):

    def add(self, item: BaseData, amount: int):
        self._items.append((item, amount))
        return self

    def to_dict(self):
        return dict(
            Erc721Rewards=[],
            Erc1155Rewards=[dict(
                ItemId=item.id,
                Amount=amount
            ) for item, amount in self._items]
        )
