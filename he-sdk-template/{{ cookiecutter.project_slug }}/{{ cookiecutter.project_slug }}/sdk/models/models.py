import pydantic

from .base import _BaseModel
from .types import *
from .data import BaseData


class DataModel(_BaseModel):
    _abstract = True


class GameMechanics(_BaseModel):
    _abstract = True

    @classmethod
    def get_ignore_fields(cls):
        return list()

    @classmethod
    def dataclass(cls):
        cls_name = 'xxx'
        dyn_cls_args = dict(__base__=BaseData)
        ignore_fields = cls.get_ignore_fields()
        for fld_name, fdef in cls.__fields__.items():
            if fld_name in ignore_fields:
                continue
            dyn_cls_args[fld_name] = (fdef.outer_type_, ...)
        return pydantic.create_model(cls_name, **dyn_cls_args)


class Upgradeable(DataModel):
    _abstract = True
    Level: int


class UpgradeableWithExp(DataModel):
    _abstract = True
    Exp: UInt64 = 0
    Level: UInt32 = 0
