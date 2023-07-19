import inflection
import pydantic
import typing

from .base import _BaseModel
from .data import BaseData
from .models import DataModel
from .progression import GenericLadderLevel, GenericLadder


class BattlePass(_BaseModel):
    Name: str
    LevelData: typing.Type[BaseData]
    Model: typing.Type[DataModel]
    Data: typing.Type[BaseData]
    #
    _FullLadderLevelData: typing.Type[GenericLadderLevel] = None
    _LadderClass: typing.Type[GenericLadder] = None

    @property
    def name(self):
        return inflection.camelize(self.Name)

    @property
    def ladder_class(self) -> typing.Type:
        if self._LadderClass:
            return self._LadderClass
        cls_name = f'{self.name}BattlePassLadder'
        dyn_cls_args = dict(__base__=GenericLadder)
        dyn_cls_args['Levels'] = (typing.List[self.ladder_level_data_class], ...)
        self._LadderClass = pydantic.create_model(cls_name, **dyn_cls_args)
        return self._LadderClass

    @property
    def ladder_level_data_class(self) -> typing.Type:
        if self._FullLadderLevelData:
            return self._FullLadderLevelData
        cls_name = f'{self.name}BattlePassLadderData'
        dyn_cls_args = dict(__base__=GenericLadderLevel)
        dyn_cls_args['Data'] = (self.LevelData, ...)
        self._FullLadderLevelData = pydantic.create_model(cls_name, **dyn_cls_args)
        return self._FullLadderLevelData

    def to_dict(self):
        return dict(
            Name=self.Name,
            LevelData=self.LevelData.to_dict(),
            Model=self.Model.to_dict(),
            Data=self.Data.to_dict()
        )
