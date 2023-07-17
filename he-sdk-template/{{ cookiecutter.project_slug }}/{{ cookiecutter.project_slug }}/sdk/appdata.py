import json
import pathlib
import pydantic
import typing


class AppEnvData(pydantic.BaseModel):
    Id: str
    Name: str


class AppVersionData(pydantic.BaseModel):
    Id: str
    Name: str


class AppData(pydantic.BaseModel):
    Id: str
    Name: str
    Versions: typing.List[AppVersionData]
    AppEnvironments: typing.List[AppEnvData]

    @staticmethod
    def default_path():
        return pathlib.Path(__file__).parents[2].joinpath('app.json')

    @classmethod
    def load(cls, path=None):
        path = path or AppData.default_path()
        with open(path, 'r') as j_file:
            j_data = json.load(j_file)
        return AppDataWrapper(cls(**j_data))

    def save(self, path=None):
        path = path or AppData.default_path()
        with open(path, 'w') as j_file:
            json.dump(self.dict(), j_file, indent=4)


class AppDataWrapper(object):
    def __init__(self, app_data: AppData):
        self._app_data = app_data
        self._versions = {}
        for version in self._app_data.Versions:
            self._versions[version.Name] = version
        self._envs = {}
        for env in self._app_data.AppEnvironments:
            self._envs[env.Name] = env

    @property
    def Id(self):
        return self._app_data.Id

    @Id.setter
    def Id(self, value):
        self._app_data.Id = value

    @property
    def Name(self):
        return self._app_data.Name

    def has_version(self, version_name: str) -> bool:
        return version_name in self._versions

    def has_app_env(self, env_name: str) -> bool:
        return env_name in self._envs

    def add_version(self, version: AppVersionData):
        self._app_data.Versions.append(version)
        self._versions[version.Name] = version

    def add_app_env(self, env: AppEnvData):
        self._app_data.AppEnvironments.append(env)
        self._envs[env.Name] = env

    def get_version(self, version_name: str) -> AppVersionData:
        return self._versions.get(version_name)

    def get_app_env(self, env_name: str) -> AppEnvData:
        return self._envs.get(env_name)

    def save(self, path=None):
        return self._app_data.save(path)
