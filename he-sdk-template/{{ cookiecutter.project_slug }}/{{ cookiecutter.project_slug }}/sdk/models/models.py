from .base import _BaseModel
from .types import *
from .data import BaseData


class DataModelMeta(type(_BaseModel)):
    def __new__(mcs, cls_name, bases, namespace):
        new_cls = super().__new__(mcs, cls_name, bases, namespace)
        setattr(new_cls, '__templates', dict())
        setattr(new_cls, '__data_class', None)
        return new_cls

    def __getattr__(cls, name):
        if name in cls.__dict__.get('__templates', {}):
            return cls.__dict__['__templates'][name]
        raise AttributeError(f"{cls.__name__} object has no attribute {name}")


class DataModelTemplate(object):
    def __init__(self, cls, data):
        self._cls = cls
        self._data = data


class DataModel(_BaseModel, metaclass=DataModelMeta):
    _abstract = True

    @classmethod
    def new_template(cls, data: BaseData) -> DataModelTemplate:
        if not isinstance(data, cls.dataclass()):
            raise TypeError()
        tmpl = DataModelTemplate(cls, data)
        cls.__templates[data.id] = tmpl
        return tmpl

    @classmethod
    def dataclass(cls):
        if cls.__data_class:
            return cls.__data_class
        dcs = []
        data_fld_cls = None
        for fname, fdef in cls.__fields__.items():
            t_origin = typing.get_origin(fdef)
            if not t_origin:
                continue
            if t_origin.__name__ != 'DataRef':
                continue
            t_args = typing.get_args(fdef)
            dcs.append(t_args[0])
            if fname == 'Data':
                data_fld_cls = t_args[0]
        if data_fld_cls:
            cls.__data_class = data_fld_cls
        else:
            cls.__data_class = dcs[0] if dcs else None
        return cls.__data_class


class Upgradeable(DataModel):
    _abstract = True
    Level: int


class UpgradeableWithExp(DataModel):
    _abstract = True
    Exp: UInt64 = 0
    Level: UInt32 = 0
