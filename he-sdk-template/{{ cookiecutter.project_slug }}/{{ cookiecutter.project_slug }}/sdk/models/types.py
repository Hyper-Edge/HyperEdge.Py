import sys
import typing
import ulid


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
        u = ulid.ULID.from_str(v)
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
