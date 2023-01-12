from datetime import datetime

from pydantic import BaseModel, validator


class ProtocolLineDto(BaseModel):
    committee_session_id: str
    number: int
    knesset_num: int
    type_id: str
    type_description: str
    committee_id: str
    location: str
    session_url: str
    broadcast_url: str
    start_date: datetime
    finish_date: datetime
    note: str
    last_updated_date: datetime
    item_ids: list[str]
    item_type_ids: list[str]
    topics: list[str]
    committee_name: str
    bill_names: list[str]
    bill_types: list[str]
    related_to_legislation: bool
    mks: list[str]
    invitees: list[str]
    legal_advisors: list[str]
    manager: str
    financial_advisors: list[str]
    attended_mk_individual_ids: list[str]

    @validator("start_date", pre=True)
    def parse_birthdate(cls, value):
        return datetime.strptime(
            value,
            "%d/%m/%Y"
        ).date()