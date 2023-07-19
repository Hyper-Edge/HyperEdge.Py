import pydantic


class EnergySystem(pydantic.BaseModel):
    Name: str
    InitialValue: int
    RegenValue: int
    RegenRate: int
    MaxCapacity: int
