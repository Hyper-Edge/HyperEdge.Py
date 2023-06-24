import json
import pathlib
import pydantic
import typing


class AppData(pydantic.BaseModel):
    Id: str
    Name: str
    Versions: typing.List[str]

    @staticmethod
    def default_path():
        return pathlib.Path(__file__).parents[2].joinpath('app.json')

    @classmethod
    def load(cls, path=None):
        path = path or AppData.default_path()
        with open(path, 'r') as j_file:
            j_data = json.load(j_file)
        return cls(**j_data)

    def save(self, path=None):
        path = path or AppData.default_path()
        with open(path, 'w') as j_file:
            json.dump(self.dict(), j_file, indent=4)
