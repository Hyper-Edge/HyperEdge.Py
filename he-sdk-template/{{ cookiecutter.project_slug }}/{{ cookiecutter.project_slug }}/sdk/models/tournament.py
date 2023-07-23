import inflection
import pydantic
import typing

from .base import _BaseModel
from .data import BaseData
from .models import DataModel


class Tournament(_BaseModel):
    Name: str
    ScoreFieldName: str = 'Score'
    Model: typing.Type[DataModel]
    Data: typing.Type[BaseData]

    def to_dict(self):
        return dict(
            Name=self.Name,
            ScoreFieldName=self.ScoreFieldName,
            Model=self.Model.to_dict(),
            Data=self.Data.to_dict())
