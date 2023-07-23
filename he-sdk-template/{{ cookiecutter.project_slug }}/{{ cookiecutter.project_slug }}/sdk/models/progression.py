import inflection
import pydantic

from .types import *
from .base import _BaseModel
from .models import DataModel
from .data import BaseData
from .reward import Reward
from .cost import Cost


class GenericLadderLevel(BaseData):
    Exp: typing.Optional[int]
    Reward: typing.Optional[Reward]
    Cost: typing.Optional[Cost]
    Conditions: typing.Optional[typing.List[str]]
    
    class Config:
        arbitrary_types_allowed = True


class GenericLadder(pydantic.BaseModel):
    Name: str
    ProgressionId: typing.Optional[str]
    ProgressionName: str
    Levels: typing.List[GenericLadderLevel]

    def add_level(self, ll: GenericLadderLevel):
        self.Levels.append(ll)

    def to_dict(self):
        return dict(
            Name=self.Name,
            ProgressionId=self.ProgressionId,
            ProgressionName=self.ProgressionName,
            Levels=[l.to_dict() for l in self.Levels]
        )


class ProgressionLadder(_BaseModel):
    Entity: typing.Type[DataModel]
    IsExperienceBased: bool
    LevelField: str = 'Level'
    ExperienceField: str = 'Exp'
    LadderLevelData: typing.Type[BaseData]
    _FullLadderLevelData: typing.Type[GenericLadderLevel] = None
    _LadderClass: typing.Type[GenericLadder] = None

    @property
    def ladder_class(self) -> typing.Type:
        if self._LadderClass:
            return self._LadderClass
        cls_name = f'{self.Entity.__name__}{self.LevelField}{self.ExperienceField}Ladder'
        dyn_cls_args = dict(__base__=GenericLadder)
        dyn_cls_args['Levels'] = (typing.List[self.ladder_level_data_class], ...)
        self._LadderClass = pydantic.create_model(cls_name, **dyn_cls_args)
        return self._LadderClass

    @property
    def ladder_level_data_class(self) -> typing.Type:
        if self._FullLadderLevelData:
            return self._FullLadderLevelData
        cls_name = f'{self.Entity.__name__}{self.LevelField}{self.ExperienceField}LadderData'
        dyn_cls_args = dict(__base__=GenericLadderLevel)
        dyn_cls_args['Data'] = (self.LadderLevelData, ...)
        self._FullLadderLevelData = pydantic.create_model(cls_name, **dyn_cls_args)
        return self._FullLadderLevelData

    def new_ladder(self, name: str):
        return self.ladder_class(
            Name=name,
            ProgressionName=type(self).__name__,
            Levels=list())

    def to_dict(self):
        return dict(
            EntityName=inflection.camelize(self.Entity.__name__),
            IsExperienceBased=self.IsExperienceBased,
            LevelField=self.LevelField,
            ExperienceField=self.ExperienceField,
            LadderLevelData=self.LadderLevelData.to_dict()
        )
