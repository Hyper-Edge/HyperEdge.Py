import json
import importlib
import inspect
import inflection
import pathlib
import typing

from {{ cookiecutter.project_slug }}.sdk.models.types import is_new_type, Ulid
from {{ cookiecutter.project_slug }}.sdk.models.base import _BaseModel
from {{ cookiecutter.project_slug }}.sdk.models import *


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


def datadef_to_json(cls):
    flds = []
    for fname, fdef in cls.__fields__.items():
        if fname == 'id':
            continue
        flds.append({'Name': fname, 'Typename': get_cs_type(fdef.outer_type_)})
    return dict(
        Name=cls.__name__,
        Fields=flds
    )

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


def get_cs_type(fdef: type, dto=False):
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
            return f"List<{get_cs_type(t_args[0], dto=dto)}>"
        elif t_origin is dict:
            return f"Dict<{get_cs_type(t_args[0], dto=dto)}, {get_cs_type(t_args[1], dto=dto)}>"
        elif t_origin == DataRef:
            return f"{get_cs_type(t_args[0], dto=dto)}"
        else:
            assert False, f"{t_origin} not supported"
    else:
        if issubclass(fdef, _BaseModel) and dto:
            wrp_cls = Wrapped(fdef)
            return f'{wrp_cls.var_name_camel}DTO'
        return fdef.__name__


class DataLoader(object):
    def __init__(self, package_name):
        self._data_classes = []
        self._model_classes = []
        self.iterate_dataclasses(package_name)

    def iterate_dataclasses_in_package(self, package_name):
        package = importlib.import_module(package_name)
        for (name, obj) in inspect.getmembers(package):
            if inspect.isclass(obj):
                if not issubclass(obj, _BaseModel):
                    continue
                if obj.__module__ != package.__name__:
                    continue
                if obj is _BaseModel:
                    continue
                if issubclass(obj, DataModel):
                    print(obj)
                    self._model_classes.append(obj)
                elif issubclass(obj, BaseData):
                    self._data_classes.append(obj)
            elif isinstance(obj, BaseData):
                pass

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
        data_classes = []
        model_classes = []
        struct_classes = []
        data_class_instances = {}
        #
        for cls in self._data_classes:
            j = datadef_to_json(cls)
            if issubclass(cls, BaseData):
                data_classes.append(j)
            else:
                struct_classes.append(j)
        #
        for cls in self._model_classes:
            j = datadef_to_json(cls)
            model_classes.append(j)
        #
        for cls in BaseData.dataclasses():
            for data_inst in BaseData.instances(cls):
                j = datainst_to_json(cls, data_inst)
                if cls.__name__ not in data_class_instances:
                    data_class_instances[cls.__name__] = []
                data_class_instances[cls.__name__].append(j)
        #
        return dict(
            DataClasses=data_classes,
            ModelClasses=model_classes,
            StructClasses=struct_classes,
            StorageClasses=[],
            DataClassInstances=data_class_instances,
            Inventories=[inv.to_dict() for inv in Inventory.all()],
            Quests=[],
            Tournaments=[],
            BattlePasses=[],
            Progressions=[],
            ProgressionLadders=[],
            CraftRules=[],
            Rewards=[],
            EnergySystems=[],
            RequestHandlers=[]
        )
