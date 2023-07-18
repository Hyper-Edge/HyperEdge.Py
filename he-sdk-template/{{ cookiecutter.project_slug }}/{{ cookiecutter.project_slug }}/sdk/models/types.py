import inflection
import sys
import typing
from ulid import ULID


UInt64 = typing.NewType("UInt64", int)
Int64 = typing.NewType("Int64", int)
UInt32 = typing.NewType("UInt32", int)
Int32 = typing.NewType("Int32", int)


class Ulid(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        u = ULID.from_str(v)
        return cls(str(u))

    def __repr__(self):
        return f'Ulid({super().__repr__()})'


def is_new_type(tp):
    if sys.version_info[:3] >= (3, 10, 0) and sys.version_info.releaselevel != 'beta':
        return tp is typing.NewType or isinstance(tp, typing.NewType)
    elif sys.version_info[:3] >= (3, 0, 0):
        return (tp is typing.NewType or
                (getattr(tp, '__supertype__', None) is not None and
                 getattr(tp, '__qualname__', '') == 'NewType.<locals>.new_type' and
                 tp.__module__ in ('typing', 'typing_extensions')))
    else:
        assert False


def get_cs_type(fdef: type):
    #
    t_origin = typing.get_origin(fdef)
    #
    if is_new_type(fdef):
        return fdef.__name__.lower()
    elif fdef == int:
        return "int"
    elif fdef == str:
        return "string"
    elif fdef == Ulid:
        return "Ulid"
    elif t_origin:
        t_args = typing.get_args(fdef)
        if t_origin is typing.Optional:
            return get_cs_type(t_args[0])
        elif t_origin is list:
            return f"List<{get_cs_type(t_args[0])}>"
        elif t_origin is dict:
            return f"Dict<{get_cs_type(t_args[0])}, {get_cs_type(t_args[1])}>"
        elif t_origin.__name__ == 'DataRef':
            return f"{get_cs_type(t_args[0])}"
        else:
            assert False, f"{t_origin} not supported"
    else:
        return fdef.__name__


class Wrapped(object):
    def __init__(self, cls):
        self._cls = cls
        self._entity_name = inflection.camelize(cls.__name__)
        self._entity_name_plural = inflection.pluralize(self._entity_name)
        self._entity_name_us = inflection.underscore(self._entity_name)
        self._var_name = inflection.underscore(cls.__name__)
        self._var_name_camel = inflection.camelize(self._var_name)
        self._var_name_camel_plural = inflection.pluralize(self._var_name_camel)
        self._var_name_plural = inflection.pluralize(self._var_name)
        self._data = None

    @property
    def uid(self):
        return self._cls._uid

    @property
    def storage_flags(self):
        return self._cls._storage_flags

    @property
    def data(self):
        return self._data

    @property
    def entity_name(self):
        return self._entity_name

    @property
    def entity_name_plural(self):
        return self._entity_name_plural

    @property
    def entity_name_us(self):
        return self._entity_name_us

    @property
    def var_name(self):
        return self._var_name

    @property
    def var_name_camel(self):
        return self._var_name_camel

    @property
    def var_name_camel_plural(self):
        return self._var_name_camel_plural

    @property
    def var_name_plural(self):
        return self._var_name_plural

