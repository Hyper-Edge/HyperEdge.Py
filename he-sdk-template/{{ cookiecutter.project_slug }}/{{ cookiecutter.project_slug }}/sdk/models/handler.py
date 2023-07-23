import typing

from .base import _BaseModel
from .data import BaseData


class Handler(_BaseModel):
    Name: str
    RequestClass: typing.Type[BaseData]
    ResponseClass: typing.Type[BaseData]
    Code: typing.Optional[str]

    def to_dict(self):
        return dict(
            Name=self.Name,
            Model=self.RequestClass.__name__,
            Data=self.ResponseClass.__name__,
            Code=self.Code
        )
