import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner
from importlib import import_module

project_slug = "{{ cookiecutter.project_slug }}"
cli_app_module = import_module(f"{project_slug}.{project_slug}.cli") # Import the cli module without messing up the imports
cli_app = cli_app_module.cli_app

runner = CliRunner()

def test_create_battlepass():
    # The invoke method is used to call the command
    # The input parameter is a list of strings that will be used as command line arguments
    result = runner.invoke(cli_app, ["create_battlepass", "MyBattlePass"])

    # You can check the output of the command
    assert "MyBattlePass created successfully" in result.output

    # You can also check the exit code of the command
    assert result.exit_code == 0
