import os
import pydantic
import requests
import typing
from ulid import ULID


_EMPTY_ULID = ULID(bytes(16))


class DataClassFieldDTO(pydantic.BaseModel):
    Name: str
    Typename: str
    DefaultValue: typing.Optional[str]


class DataClassDTO(pydantic.BaseModel):
    Id: str = str(_EMPTY_ULID)
    Name: str
    Fields: typing.List[DataClassFieldDTO]


class DataClassInstanceFieldDTO(pydantic.BaseModel):
    Name: str
    Value: str


class DataClassInstanceDTO(pydantic.BaseModel):
    Id: str = str(_EMPTY_ULID)
    Name: str
    Fields: typing.List[DataClassInstanceFieldDTO]


class InventoryItemDefDTO(pydantic.BaseModel):
    Id: str
    Typename: str


class InventoryDefDTO(pydantic.BaseModel):
    Name: str
    Items: typing.List[InventoryItemDefDTO]


class AppDefDTO(pydantic.BaseModel):
    Name: str
    DataClasses: typing.List[DataClassDTO]
    ModelClasses: typing.List[DataClassDTO]
    StructClasses: typing.List[DataClassDTO]
    DataClassInstances: typing.Dict[str, typing.List[DataClassInstanceDTO]]
    Inventories: typing.List[InventoryDefDTO]


class ExportAppRequest(pydantic.BaseModel):
    AppId: str
    AppDef: AppDefDTO


class HEClient(object):
    def __init__(self, url='http://localhost:9000'):
        self._api_key = os.environ.get('HE_API_KEY') #'/Ul0pgk/MZBrcM2l9STgJEdPHFGHIaQI/ZfpF/tNrxQ=')
        self._url = url

    @property
    def _auth_base_url(self):
        return f'{self._url}/api/IAuthService'

    @property
    def _depot_base_url(self):
        return f'{self._url}/api/IDepotService'

    def export_app(self, data: AppDefDTO, app_uid: ulid.ULID = _EMPTY_ULID):
        req = ExportAppRequest(AppId=str(app_uid), AppDef=data)
        return self._post_json(f'{self._depot_base_url}/ExportApp', req.json())

    def _get_headers(self):
        if not self._api_key:
            raise ValueError('HyperEdge API key is not defined')
        return {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'X-API-Key': self._api_key
        }

    def _post_json(self, url, data):
        headers = self._get_headers()
        resp = requests.post(url, data=data, headers=headers)
        print(f'Status: {resp.status_code}')
        try:
            print(resp.json())
        except requests.exceptions.JSONDecodeError:
            print(resp.text)
            raise
        return resp.json()
