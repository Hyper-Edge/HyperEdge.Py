import inflection
import pathlib
import typing
import typer
from typing import List, Optional
import json 

from {{ cookiecutter.project_slug }}.sdk.dataloader import DataLoader
from {{ cookiecutter.project_slug }}.sdk.client import HEClient, AppDefDTO
from {{ cookiecutter.project_slug }}.sdk.appdata import AppData, AppEnvData, AppVersionData


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
    if app_manifest.Id:
        app_def.Id = app_manifest.Id
    client = HEClient()
    resp = client.export_app(app_def)
    app_manifest.Id = resp.AppId
    app_manifest.save()
    #
    current_app_def_filepath = pathlib.Path(__file__).parents[1].joinpath('data', 'current.json')
    client.download_file_by_id(resp.AppDefFileId, str(current_app_def_filepath))


@cli_app.command()
def release(version_name: str):
    """
    Make a release and push all data model definitions in the project to hyperedge's backend
    """
    app_manifest = AppData.load()
    if not app_manifest.Id:
        raise Exception("AppId is empty. You should export app first")
    if app_manifest.has_version(version_name):
        print(f"Version {version_name} already exist")
        return
    dl = DataLoader('{{cookiecutter.project_slug}}.models')
    j_app_data = dl.to_dict()
    app_def = AppDefDTO(Name=app_manifest.Name, **j_app_data)
    client = HEClient()
    resp = client.release_app(app_def, app_manifest.Id, version_name)
    #
    app_manifest.add_version(AppVersionData(Id=resp.VersionId, Name=resp.VersionName))
    app_manifest.save()
    #
    current_app_def_filepath = pathlib.Path(__file__).parents[1].joinpath('data', f'app-{version_name}.json')
    client.download_file_by_id(resp.AppDefFileId, str(current_app_def_filepath))


@cli_app.command()
def build(version_name: str):
    app_manifest = AppData.load()
    if not app_manifest.has_version(version_name):
        raise Exception(f"Unknown version: {version_name}")
    client = HEClient()
    resp = client.build_app(app_manifest.Id, version_name)
    print(resp)


@cli_app.command()
def create_env(env_name: str):
    app_manifest = AppData.load()
    if app_manifest.has_app_env(env_name):
        print(f'AppEnv {env_name} already exists.')
        return
    client = HEClient()
    resp = client.create_app_env(app_manifest.Id, env_name)
    app_manifest.add_app_env(AppEnvData(Id=resp.Id, Name=resp.Name))
    app_manifest.save()


@cli_app.command()
def run(version_name: str, env_name: str):
    app_manifest = AppData.load()
    version = app_manifest.get_version(version_name)
    if version is None:
        print(f"Version {env_name} doesn't exist.")
        return
    app_env = app_manifest.get_app_env(env_name)
    if app_env is None:
        print(f"AppEnv {env_name} doesn't exist.")
        return
    client = HEClient()
    resp = client.run_app(app_manifest.Id, version.Id, app_env.Id)


@cli_app.command()
def gen_code():
    app_manifest = AppData.load()
    client = HEClient()
    resp = client.gen_code(app_manifest.Id)
    print(resp)


@cli_app.command()
def start_server():
    app_manifest = AppData.load()
    client = HEClient()
    resp = client.start_server(app_manifest.Id)
    print(resp)


def _get_models_paths():
    return pathlib.Path(__file__).parent.joinpath('models')


@cli_app.command()
def create_dataclass(name: str = typer.Argument(..., help="Name of the Dataclass"), 
                  fields: Optional[List[str]] = typer.Option(None, '--fields', help='Custom Fields')):
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
def create_model(name: str = typer.Argument(..., help="Name of the Model"),
                dataref: str = typer.Argument(..., help="Reference to the Dataclass"),
                fields: Optional[List[str]] = typer.Option(None, '--fields', help='Custom Fields')):
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


@cli_app.command()
def create_reward(name: str = typer.Argument(..., help="Name of the Reward"), 
                  fields: Optional[List[str]] = typer.Option(None, '--fields', help='Custom Fields')):
    """
    Create a reward.
    """
    fname = inflection.underscore(name)
    fpath = _get_models_paths().joinpath(f'{fname}.py')
    #
    s = f"""from {{ cookiecutter.project_slug }}.sdk.models import DataModel

class Reward{inflection.camelize(name)}(DataModel):
    ItemId: str
    Amount: int
"""
    for fld in fields:
        fld_ = fld.split(':')
        fname, ftype = fld_
        s += f"    {inflection.camelize(fname)}: {ftype}\n"

    
    if fpath.exists():
        raise Exception(f"File {str(fpath)} already exists")

    with open(str(fpath), 'w') as f:
        f.write(s)


@cli_app.command()
def create_cost(name: str = typer.Argument(..., help="Name of the Cost"), 
                  fields: Optional[List[str]] = typer.Option(None, '--fields', help='Custom Fields')):
    """
    Create a cost.
    """
    fname = inflection.underscore(name)
    fpath = _get_models_paths().joinpath(f'{fname}.py')
    #
    s = f"""from {{ cookiecutter.project_slug }}.sdk.models import DataModel

class Cost{inflection.camelize(name)}(DataModel):
    ItemId: str
    Amount: int
"""
    for fld in fields:
        fld_ = fld.split(':')
        fname, ftype = fld_
        s += f"    {inflection.camelize(fname)}: {ftype}\n"

    
    if fpath.exists():
        raise Exception(f"File {str(fpath)} already exists")

    with open(str(fpath), 'w') as f:
        f.write(s)


@cli_app.command()
def create_craft(name: str = typer.Argument(..., help="Name of the Craft"), 
                  fields: Optional[List[str]] = typer.Option(None, '--fields', help='Custom Fields')):
    """
    Create a craft.
    """
    fname = inflection.underscore(name)
    fpath = _get_models_paths().joinpath(f'{fname}.py')
    #
    s = f"""from {{ cookiecutter.project_slug }}.sdk.models import DataModel, Dataref

class Cost{inflection.camelize(name)}(DataModel):
    Cost: Dataref[str]
    Reward: Dataref[str]
"""
    for fld in fields:
        fld_ = fld.split(':')
        fname, ftype = fld_
        s += f"    {inflection.camelize(fname)}: {ftype}\n"

    if fpath.exists():
        raise Exception(f"File {str(fpath)} already exists")

    with open(str(fpath), 'w') as f:
        f.write(s)


@cli_app.command()
def create_quest(name: str = typer.Argument(..., help="Name of the Craft"), 
                  fields: Optional[List[str]] = typer.Option(None, '--fields', help='Custom Fields')):
    """
    Create a quest.
    """
    fname = inflection.underscore(name)
    fpath = _get_models_paths().joinpath(f'{fname}.py')
    #
    s = f"""from {{ cookiecutter.project_slug }}.sdk.models import DataModel, str

class Quest{inflection.camelize(name)}(DataModel):
    AcceptConditions: str
    FinishConditions: str
    Reward: DataRef[str]
"""
    for fld in fields:
        fld_ = fld.split(':')
        fname, ftype = fld_
        s += f"    {inflection.camelize(fname)}: {ftype}\n"

    if fpath.exists():
        raise Exception(f"File {str(fpath)} already exists")
    
    with open(str(fpath), 'w') as f:
        f.write(s)


@cli_app.command()
def create_ladder(name: str = typer.Argument(..., help="Name of the Ladder"), 
                  fields: Optional[List[str]] = typer.Option(None, '--fields', help='Custom Fields')):
    """
    Create a ladder.
    """
    fname = inflection.underscore(name)
    fpath = _get_models_paths().joinpath(f'{fname}.py')
    #
    s = f"""from {{ cookiecutter.project_slug }}.sdk.models import DataModel

class Ladder{inflection.camelize(name)}(DataModel), List:
    Levels: List[str]
"""
    for fld in fields:
        fld_ = fld.split(':')
        fname, ftype = fld_
        s += f"    {inflection.camelize(fname)}: {ftype}\n"
    #
    s += """
    def addLevel(level):
        self.Levels.append(level)
"""

    if fpath.exists():
        raise Exception(f"File {str(fpath)} already exists")

    with open(str(fpath), 'w') as f:
        f.write(s)


@cli_app.command()
def create_battlepass(name: str = typer.Argument(..., help="Name of the Battlepass"), 
                  fields: Optional[List[str]] = typer.Option(None, '--fields', help='Custom Fields')):
    """
    Create a battlepass.
    """
    fname = inflection.underscore(name)
    fpath = _get_models_paths().joinpath(f'{fname}.py')
    #
    s = f"""from {{ cookiecutter.project_slug }}.sdk.models import DataModel, DataRef

class BattlePass{inflection.camelize(name)}(DataModel):
    BattleLevel: DataRef[str]
    Score: int
"""
    for fld in fields:
        fld_ = fld.split(':')
        fname, ftype = fld_
        s += f"    {inflection.camelize(fname)}: {ftype}\n"
    s += """
    def getScore():
        return this.Score

    def addScore(score):
        this.Score += score
        return this.Score
"""

    if fpath.exists():
        raise Exception(f"File {str(fpath)} already exists")
        
    with open(str(fpath), 'w') as f:
        f.write(s)


