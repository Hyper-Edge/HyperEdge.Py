import json
import importlib
import inspect
import pathlib
import typing

from {{ cookiecutter.project_slug }}.sdk.models.types import *
from {{ cookiecutter.project_slug }}.sdk.models.base import _BaseModel
from {{ cookiecutter.project_slug }}.sdk.models import *


def datainst_to_json(cls, data_inst):
    flds = []
    for fname, fdef in cls.__fields__.items():
        if fname == 'id':
            continue
        flds.append({'Name': fname, 'Value': getattr(data_inst, fname)})
    #
    return dict(
        Name=data_inst.id,
        Fields=flds
    )


class DataLoader(object):
    def __init__(self, package_name):
        self._data_classes = []
        self._model_classes = []
        self._struct_classes = []
        self._storage_classes = []
        self._rewards: typing.List[Reward] = []
        self._crafts: typing.List[CraftRule] = []
        self._progressions: typing.List[ProgressionLadder] = []
        self._battle_passes: typing.List[BattlePass] = []
        self._quests: typing.List[Quest] = []
        self._energy_systems: typing.List[EnergySystem] = []
        self._tournaments: typing.List[Tournament] = []
        self._request_handlers: typing.List[Handler] = []

        self.iterate_dataclasses(package_name)

    def iterate_dataclasses_in_package(self, package_name):
        package = importlib.import_module(package_name)
        for (name, obj) in inspect.getmembers(package):
            if inspect.isclass(obj):
                #
                if not issubclass(obj, _BaseModel):
                    continue
                if obj.__module__ != package.__name__:
                    continue
                if obj is _BaseModel:
                    continue
                if issubclass(obj, StorageBase):
                    self._storage_classes.append((obj.get_storage_type(), obj))
                elif issubclass(obj, DataModel):
                    self._model_classes.append(obj)
                elif issubclass(obj, BaseData):
                    self._data_classes.append(obj)
                else:
                    self._struct_classes.append(obj)
            elif isinstance(obj, Reward):
                self._rewards.append(obj)
            elif isinstance(obj, CraftRule):
                self._crafts.append(obj)
            elif isinstance(obj, ProgressionLadder):
                self._progressions.append(obj)
            elif isinstance(obj, BattlePass):
                self._battle_passes.append(obj)
            elif isinstance(obj, Quest):
                self._quests.append(obj)
            elif isinstance(obj, EnergySystem):
                self._energy_systems.append(obj)
            elif isinstance(obj, Tournament):
                self._tournaments.append(obj)
            elif isinstance(obj, Handler):
                self._request_handlers.append(obj)

    def iterate_dataclasses(self, package_name: str):
        package = importlib.import_module(package_name)
        package_path = pathlib.Path(package.__path__[0])
        for fpath in package_path.rglob("*.py"):
            print(fpath)
            rel_path = str(fpath.relative_to(package_path))
            rel_path = rel_path[:-len(".py")]
            pname = package_name + '.' + '.'.join(rel_path.split('/'))
            #
            self.iterate_dataclasses_in_package(pname)

    def to_json(self):
        data = self.to_dict()
        return json.dumps(data, indent=4)

    def to_dict(self):
        data_class_instances = {}
        #
        for cls in BaseData.dataclasses():
            for data_inst in BaseData.instances(cls):
                j = datainst_to_json(cls, data_inst)
                if cls.__name__ not in data_class_instances:
                    data_class_instances[cls.__name__] = []
                data_class_instances[cls.__name__].append(j)
        #
        return dict(
            DataClasses=[cls.to_dict() for cls in self._data_classes],
            ModelClasses=[cls.to_dict() for cls in self._model_classes],
            StructClasses=[cls.to_dict() for cls in self._struct_classes],
            StorageClasses=[(st_type, cls.to_dict()) for (st_type, cls) in self._storage_classes],
            DataClassInstances=data_class_instances,
            Inventories=[inv.to_dict() for inv in Inventory.all()],
            Quests=[q.to_dict() for q in self._quests],
            Tournaments=[t.to_dict() for t in self._tournaments],
            BattlePasses=[bp.to_dict() for bp in self._battle_passes],
            Progressions=[p.to_dict() for p in self._progressions],
            ProgressionLadders=[],
            CraftRules=[c.to_dict() for c in self._crafts],
            Rewards=[r.to_dict() for r in self._rewards],
            EnergySystems=[es.dict() for es in self._energy_systems],
            RequestHandlers=[h.to_dict() for h in self._request_handlers]
        )
