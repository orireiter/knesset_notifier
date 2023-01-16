import json
from datetime import datetime

from dateutil.parser import parse
from pydantic import BaseModel, validator


class ProtocolLineDto(BaseModel):
    committee_session_id: str
    number: int = None
    knesset_num: int
    type_id: str
    type_description: str
    committee_id: str
    location: str
    session_url: str
    broadcast_url: str
    start_date: datetime
    finish_date: datetime = None
    note: str
    last_updated_date: datetime = None
    item_ids: list[str]
    item_type_ids: list[str]
    topics: list[str]
    committee_name: str
    bill_names: list[str]
    bill_types: list[str]
    related_to_legislation: bool
    mks: list[str]
    invitees: list[dict]
    legal_advisors: list[str]
    manager: str
    financial_advisors: list[str]
    attended_mk_individual_ids: list[str]

    @validator("start_date", "finish_date", "last_updated_date", pre=True)
    def parse_dates(cls, value, values, config, field):
        return parse(value) if value else None

    @validator("number", "knesset_num", pre=True)
    def parse_ints(cls, value):
        return int(value) if value else None

    @validator("related_to_legislation", pre=True)
    def parse_bools(cls, value):
        return value.lower().strip() == "true"

    @validator(
        "item_ids",
        "item_type_ids",
        "topics",
        "bill_names",
        "bill_types",
        "mks",
        "legal_advisors",
        "financial_advisors",
        "attended_mk_individual_ids",
        pre=True,
    )
    def parse_list_of_str(cls, value, values, config, field):
        the_list = [str(after) for after in json.loads(value)]
        return the_list

    @validator(
        "invitees",
        pre=True,
    )
    def parse_list_of_dict(cls, value, values, config, field):
        the_list = json.loads(value)
        return the_list
