import typing

from .base import _BaseModel
from .data import BaseData
from .models import DataModel


class Quest(_BaseModel):
    Name: str
    AcceptConditions: typing.List[str]
    FinishConditions: typing.List[str]
    Model: typing.Type[DataModel]
    Data: typing.Optional[typing.Type[BaseData]]

    def to_dict(self):
        return dict(
            Name=self.Name,
            AcceptConditions=self.AcceptConditions,
            FinishConditions=self.FinishConditions,
            Model=self.Model.to_dict(),
            Data=self.Data.to_dict()
        )
