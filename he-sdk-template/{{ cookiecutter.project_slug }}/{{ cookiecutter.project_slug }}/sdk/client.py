import os
import pydantic
import requests
import typing
import ulid

from .ws import HeWsClient


_EMPTY_ULID = ulid.ULID(bytes(16))


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


class DataClassInstanceFieldsDTO(pydantic.BaseModel):
    Fields: typing.List[DataClassInstanceFieldDTO]


class InventoryItemDefDTO(pydantic.BaseModel):
    Id: str
    Typename: str


class InventoryDefDTO(pydantic.BaseModel):
    Name: str
    Items: typing.List[InventoryItemDefDTO]


class Erc721RewardDTO(pydantic.BaseModel):
    EntityName: str
    ItemId: str
    Amount: int


class Erc1155RewardDTO(pydantic.BaseModel):
    ItemId: str
    Amount: int


class RewardDTO(pydantic.BaseModel):
    Erc721Rewards: typing.List[Erc721RewardDTO]
    Erc1155Rewards: typing.List[Erc1155RewardDTO]


class Erc721CostDTO(pydantic.BaseModel):
    EntityName: str
    ItemId: str
    Amount: int
    Conditions: typing.List[str]


class Erc1155CostDTO(pydantic.BaseModel):
    ItemId: str
    Amount: int


class CostDTO(pydantic.BaseModel):
    Erc721Costs: typing.List[Erc721CostDTO]
    Erc1155Costs: typing.List[Erc1155CostDTO]


class CraftRulesDTO(pydantic.BaseModel):
    Name: str
    Cost: CostDTO
    Reward: RewardDTO


class DataClassFieldsDTO(pydantic.BaseModel):
    Fields: typing.List[DataClassFieldDTO]


class ProgressionSystemDTO(pydantic.BaseModel):
    EntityName: str
    IsExperienceBased: bool
    LevelField: typing.Optional[str] = 'Level'
    ExperienceField: typing.Optional[str] = 'Exp'
    LadderLevelData: typing.Optional[DataClassFieldsDTO]


class GenericLadderLevelDTO(pydantic.BaseModel):
    Exp: typing.Optional[int]
    Reward: typing.Optional[RewardDTO]
    Cost: typing.Optional[CostDTO]
    Conditions: typing.Optional[typing.List[str]]
    Data: typing.Optional[DataClassInstanceFieldsDTO]


class GenericLadderDTO(pydantic.BaseModel):
    Name: str
    ProgressionId: str
    Levels: typing.List[GenericLadderLevelDTO]


class BattlePassDTO(pydantic.BaseModel):
    Name: str
    LevelData: typing.Optional[DataClassFieldsDTO]
    Model: typing.Optional[DataClassFieldsDTO]
    Data: typing.Optional[DataClassFieldsDTO]


class QuestDTO(pydantic.BaseModel):
    Name: str
    AcceptConditions: typing.List[str]
    FinishConditions: typing.List[str]
    ModelUid: typing.Optional[str]
    Model: DataClassFieldsDTO
    DataUid: typing.Optional[str]
    Data: typing.Optional[DataClassFieldsDTO]


class TournamentDTO(pydantic.BaseModel):
    Name: str
    Model: DataClassFieldsDTO
    Data: DataClassFieldsDTO


class AppDefDTO(pydantic.BaseModel):
    Name: str
    DataClasses: typing.List[DataClassDTO]
    ModelClasses: typing.List[DataClassDTO]
    StructClasses: typing.List[DataClassDTO]
    DataClassInstances: typing.Dict[str, typing.List[DataClassInstanceDTO]]
    Inventories: typing.List[InventoryDefDTO]
    Quests: typing.List[QuestDTO]
    Tournaments: typing.List[TournamentDTO]
    BattlePasses: typing.List[BattlePassDTO]
    Progressions: typing.List[ProgressionSystemDTO]
    ProgressionLadders: typing.List[GenericLadderDTO]
    CraftRules: typing.List[CraftRulesDTO]


class ExportAppRequest(pydantic.BaseModel):
    AppId: str
    AppDef: AppDefDTO


class ExportAppResponse(pydantic.BaseModel):
    AppId: str


class GenCodeRequest(pydantic.BaseModel):
    Id: str


class GenCodeResponse(pydantic.BaseModel):
    ServerFilesArchiveId: str


class BuildServerRequest(pydantic.BaseModel):
    Id: str


class StartServerRequest(pydantic.BaseModel):
    Id: str


class HEClient(object):
    def __init__(self, url='localhost:9000'):
        self._api_key = os.environ.get('HE_API_KEY')
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

    def gen_code(self, uid: str):
        req = GenCodeRequest(Id=uid)
        resp = self._post_json(f'{self._misc_base_url}/GenCode', req.json())
        job_data = self.ws.wait_for_job(resp['JobId'])
        if not job_data.success:
            raise Exception()
        return GenCodeResponse(ServerFilesArchiveId=job_data.retval['ServerFilesArchiveId'])

    def build_server(self, uid):
        req = BuildServerRequest(Id=uid)
        resp = self._post_json(f"{self._misc_base_url}/BuildServer", req.json())
        job_data = self.ws.wait_for_job(resp['JobId'])
        if not job_data.success:
            raise Exception()
        return None

    def start_server(self, uid):
        req = StartServerRequest(Id=uid)
        resp = self._post_json(f"{self._misc_base_url}/server/start", req.json())
        job_data = self.ws.wait_for_job(resp['JobId'])
        if not job_data.success:
            raise Exception()
        return None

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
