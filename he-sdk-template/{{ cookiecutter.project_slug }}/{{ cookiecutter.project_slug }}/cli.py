import inflection
import pathlib
import typing
import typer


from {{ cookiecutter.project_slug }}.sdk.dataloader import DataLoader


cli_app = typer.Typer()


@cli_app.command()
def collect():
    dl = DataLoader('{{cookiecutter.project_slug}}.models')
    print(dl.to_json())


def _get_models_paths():
    return pathlib.Path(__file__).parent.joinpath('models')


@cli_app.command()
def create_dataclass(name, fields: typing.List[str]):
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
        s += f"\t{inflection.camelize(fname)}: {ftype}\n"

    if fpath.exists():
        raise Exception(f"File {str(fpath)} already exists")

    with open(str(fpath), 'w') as f:
        f.write(s)


@cli_app.command()
def create_upgradable():
    pass


@cli_app.command()
def create_ladder():
    pass
