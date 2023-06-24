import os
import pydantic
import requests
import typing
from ulid import ULID

from .ws import HeWsClient


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


class ExportAppResponse(pydantic.BaseModel):
    AppId: str


class HEClient(object):
    def __init__(self, url='localhost:9000'):
        self._api_key = os.environ.get('HE_API_KEY') #'/Ul0pgk/MZBrcM2l9STgJEdPHFGHIaQI/ZfpF/tNrxQ=')
        self._host = url
        self._url = f'http://{url}'
        self._ws = None

    @property
    def ws(self):
        if self._ws is None:
            ticket = self.get_ticket()
            self._ws = HeWsClient(url=f'ws://{self._host}/ws/', ticket=ticket)
        return self._ws

    @property
    def _auth_base_url(self):
        return f'{self._url}/api/IAuthService'

    @property
    def _depot_base_url(self):
        return f'{self._url}/api/IDepotService'

    @property
    def _misc_base_url(self):
        return f'{self._url}/api/bc'

    def export_app(self, data: AppDefDTO, app_uid: ulid.ULID = _EMPTY_ULID):
        req = ExportAppRequest(AppId=str(app_uid), AppDef=data)
        resp = self._post_json(f'{self._depot_base_url}/ExportApp', req.json())
        job_data = self.ws.wait_for_job(resp['JobId'])
        if not job_data.success:
            raise Exception()
        return ExportAppResponse(AppId=job_data.retval['AppId'])

    def get_ticket(self) -> str:
        resp = self._get_json(f"{self._misc_base_url}/ws/ticket")
        return resp['ticket']

    def _get_headers(self) -> dict:
        if not self._api_key:
            raise ValueError('HyperEdge API key is not defined')
        return {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'X-API-Key': self._api_key
        }

    def _get_json(self, url: str) -> dict:
        headers = self._get_headers()
        resp = requests.get(url, headers=headers)
        print(f'Status: {resp.status_code}')
        print(resp.json())
        return resp.json()

    def _post_json(self, url: str, data: str) -> dict:
        headers = self._get_headers()
        resp = requests.post(url, data=data, headers=headers)
        print(f'Status: {resp.status_code}')
        try:
            print(resp.json())
        except requests.exceptions.JSONDecodeError:
            print(resp.text)
            raise
        return resp.json()
