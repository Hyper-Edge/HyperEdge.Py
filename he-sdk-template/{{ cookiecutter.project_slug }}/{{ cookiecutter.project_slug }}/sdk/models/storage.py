from .base import _BaseModel
from .types import *
from .data import BaseData


class StorageFlags:
    STATIC_DATA = 0
    USER_DATA = 1
    USER_DATA_UNIQUE = 2
    GLOBAL_DATA = 3
    GLOBAL_DATA_UNIQUE = 4
    STRUCT = 5


class StorageBase(_BaseModel):
    @classmethod
    def storage_type(cls):
        return StorageFlags.STRUCT


class UserStorage(StorageBase):
    @classmethod
    def storage_type(cls):
        return StorageFlags.USER_DATA


class UserVariable(StorageBase):
    @classmethod
    def storage_type(cls):
        return StorageFlags.USER_DATA_UNIQUE


class GlobalStorage(StorageBase):
    @classmethod
    def storage_type(cls):
        return StorageFlags.GLOBAL_DATA


class GlobalVariable(StorageBase):
    @classmethod
    def storage_type(cls):
        return StorageFlags.GLOBAL_DATA_UNIQUE
