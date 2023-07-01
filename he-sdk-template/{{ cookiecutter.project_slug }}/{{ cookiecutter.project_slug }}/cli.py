import inflection
import pathlib
import typing
import typer
import json 

from {{ cookiecutter.project_slug }}.sdk.dataloader import DataLoader
from {{ cookiecutter.project_slug }}.sdk.client import HEClient, AppDefDTO
from {{ cookiecutter.project_slug }}.sdk.appdata import AppData


cli_app = typer.Typer()



@cli_app.command()
def collect():
    """
    Collects all data model definitions in the project, and prints them out in JSON format.
    """
    dl = DataLoader('{{cookiecutter.project_slug}}.models')
    print(dl.to_json())


@cli_app.command()
def export():
    """
    Exports all data model definitions in the project to hyperedge's backend
    """
    app_manifest = AppData.load()
    dl = DataLoader('{{cookiecutter.project_slug}}.models')
    j_app_data = dl.to_dict()
    app_def = AppDefDTO(Name=app_manifest.Name, **j_app_data)
    client = HEClient()
    resp = client.export_app(app_def)
    app_manifest.Id = resp.AppId
    app_manifest.save()
    #
    current_app_def_filepath = pathlib.Path(__file__).parents[1].joinpath('data', 'current.json')
    client.download_file_by_id(resp.AppDefFileId, str(current_app_def_filepath))


@cli_app.command()
def gen_code():
    app_manifest = AppData.load()
    client = HEClient()
    resp = client.gen_code(app_manifest.Id)
    print(resp)


@cli_app.command()
def build():
    app_manifest = AppData.load()
    client = HEClient()
    resp = client.build_server(app_manifest.Id)
    print(resp)
    #app_manifest.save()


@cli_app.command()
def start_server():
    app_manifest = AppData.load()
    client = HEClient()
    resp = client.start_server(app_manifest.Id)
    print(resp)


def _get_models_paths():
    return pathlib.Path(__file__).parent.joinpath('models')


@cli_app.command()
def create_dataclass(name, fields: typing.List[str]):
    """
    Create a new data class, provided with <name> and <fields>. Fields should be seperated by space and each field is in the <name>:<type> attribute format.
    """
    fname = inflection.underscore(name)
    fpath = _get_models_paths().joinpath('data', f'{fname}.py')
    #
    s = f"""from {{ cookiecutter.project_slug }}.sdk.models import BaseData, DataRef
from {{ cookiecutter.project_slug }}.sdk.models.types import *


class {inflection.camelize(name)}Data(BaseData):
"""
    if not fields:
        s += "    Name: str\n"
    #
    for fld in fields:
        fld_ = fld.split(':')
        fname, ftype = fld_
        s += f"    {inflection.camelize(fname)}: {ftype}\n"
    #
    if fpath.exists():
        raise Exception(f"File {str(fpath)} already exists")
    #
    with open(str(fpath), 'w') as f:
        f.write(s)


@cli_app.command()
def create_model(name: str, dataref: str, fields: typing.List[str]):
    """
    Create a new data model, provided with <name>, <dataref>, and <fields>. Dataref should be an exisiting data class. Fields should be seperated by space and each field is in the <name>:<type> attribute format.
    """
    fname = inflection.underscore(name)
    fpath = _get_models_paths().joinpath(f'{fname}.py')
    #
    s = f"""from {{ cookiecutter.project_slug }}.sdk.models import DataModel, DataRef
from {{ cookiecutter.project_slug }}.models.data.{inflection.underscore(dataref)} import {inflection.camelize(dataref)}Data


class {inflection.camelize(name)}(DataModel):
    Data: DataRef[{inflection.camelize(dataref)}Data]
"""
    for fld in fields:
        fld_ = fld.split(':')
        fname, ftype = fld_
        s += f"    {inflection.camelize(fname)}: {ftype}\n"

    if fpath.exists():
        raise Exception(f"File {str(fpath)} already exists")

    with open(str(fpath), 'w') as f:
        f.write(s)



@cli_app.command( )
def create_upgradeable(name: str, dataref: str, fields: typing.List[str]):
    """
    Create an upgradeable.
    """
    fname = inflection.underscore(name)
    fpath = _get_models_paths().joinpath(f'{fname}.py')
    #
    s = f"""from {{ cookiecutter.project_slug }}.sdk.models import DataRef, Upgradeable
from {{ cookiecutter.project_slug }}.models.{inflection.underscore(dataref)} import {inflection.camelize(dataref)}


class {inflection.camelize(name)}(Upgradeable):
    Ladder: DataRef[{inflection.camelize(dataref)}]
"""

    for fld in fields:
        fld_ = fld.split(':')
        fname, ftype = fld_
        s += f"    {inflection.camelize(fname)}: {ftype}\n"
    #
    if fpath.exists():
        raise Exception(f"File {str(fpath)} already exists")

    with open(str(fpath), 'w') as f:
        f.write(s)


@cli_app.command()
def create_ladder(name: str, fields: typing.List[str]):
    """
    Create a ladder.
    """
    fname = inflection.underscore(name)
    fpath = _get_models_paths().joinpath(f'{fname}.py')
    #
    s = f"""from {{ cookiecutter.project_slug }}.sdk.models import DataModel

class {inflection.camelize(name)}(DataModel):
"""

    for fld in fields:
        fld_ = fld.split(':')
        fname, ftype = fld_
        s += f"    {inflection.camelize(fname)}: {ftype}\n"
    #
    if fpath.exists():
        raise Exception(f"File {str(fpath)} already exists")

    with open(str(fpath), 'w') as f:
        f.write(s)
