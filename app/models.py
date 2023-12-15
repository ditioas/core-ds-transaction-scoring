import datetime

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    UserId: str
    ProjectCompanyId: str
    ProjId: str
    ActivityId: str
    MachineId: str
    TransactionId: str = Field(alias="_id")
    CreatedDateTime: datetime.datetime
