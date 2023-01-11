from typing import Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ProtocolLineDto:
    CommitteeSessionID: Optional[str] = None
    Number: Optional[str] = None
    KnessetNum: Optional[str] = None
    TypeID: Optional[str] = None
    TypeDesc: Optional[str] = None
    CommitteeID: Optional[str] = None
    Location: Optional[str] = None
    SessionUrl: Optional[str] = None
    BroadcastUrl: Optional[str] = None
    StartDate: Optional[str] = None
    FinishDate: Optional[str] = None
    Note: Optional[str] = None
    LastUpdatedDate: Optional[str] = None
    download_crc32c: Optional[str] = None
    download_filename: Optional[str] = None
    download_filesize: Optional[str] = None
    parts_crc32c: Optional[str] = None
    parts_filesize: Optional[str] = None
    parts_parsed_filename: Optional[str] = None
    text_crc32c: Optional[str] = None
    text_filesize: Optional[str] = None
    text_parsed_filename: Optional[str] = None
    item_ids: Optional[str] = None
    item_type_ids: Optional[str] = None
    topics: Optional[str] = None
    committee_name: Optional[str] = None
    bill_names: Optional[str] = None
    bill_types: Optional[str] = None
    related_to_legislation: Optional[str] = None
    mks: Optional[str] = None
    invitees: Optional[str] = None
    legal_advisors: Optional[str] = None
    manager: Optional[str] = None
    financial_advisors: Optional[str] = None
    attended_mk_individual_ids: Optional[str] = None
