from .base import _BaseModel
from .types import *


class DataModel(_BaseModel):
    _abstract = True


class Upgradeable(DataModel):
    _abstract = True
    Level: int


class UpgradeableWithExp(DataModel):
    _abstract = True
    Exp: UInt64 = 0
    Level: UInt32 = 0
