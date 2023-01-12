import io
import csv
from datetime import datetime, timedelta

import requests

from lobby_actions.data import models


class KnessetProtocolExtractor:
    PROTOCOL_FILE_URL = "https://storage.googleapis.com/knesset-data-pipelines/data/people/committees/meeting-attendees/kns_committeesession.csv"

    def extract(self):
        return requests.get(self.PROTOCOL_FILE_URL, stream=True)


class KnessetProtocolTransformer:
    RAW_FIELD_NAMES_TO_TRANSFORMED_DATA = {
        "CommitteeSessionID": "committee_session_id",
        "Number": "number",
        "KnessetNum": "knesset_num",
        "TypeID": "type_id",
        "TypeDesc": "type_description",
        "CommitteeID": "committee_id",
        "Location": "location",
        "SessionUrl": "session_url",
        "BroadcastUrl": "broadcast_url",
        "StartDate": "start_date",
        "FinishDate": "finish_date",
        "Note": "note",
        "LastUpdatedDate": "last_updated_date",
        "item_ids": "item_ids",
        "item_type_ids": "item_type_ids",
        "topics": "topics",
        "committee_name": "committee_name",
        "bill_names": "bill_names",
        "bill_types": "bill_types",
        "related_to_legislation": "related_to_legislation",
        "mks": "mks",
        "invitees": "invitees",
        "legal_advisors": "legal_advisors",
        "manager": "manager",
        "financial_advisors": "financial_advisors",
        "attended_mk_individual_ids": "attended_mk_individual_ids",
    }

    def __init__(self, x_days_ago_as_datetime: datetime):
        self._x_days_ago_as_datetime = x_days_ago_as_datetime
        self._field_names = []

    def transform(self, response: requests.Response):
        self._field_names = self._get_key_names_of_file(response=response)

        relevant_lines = []
        for line in response.iter_lines():
            as_dto = self._transform_line_to_dto(line=line)

            if self._is_line_valid(as_dto):
                relevant_lines.append(as_dto)

        return relevant_lines

    def _get_key_names_of_file(self, response: requests.Response) -> list:
        field_names_as_str: str = response.iter_lines().__next__().decode()

        return field_names_as_str.split(",")

    def _transform_line_to_dto(self, line: bytes) -> models.ProtocolLineDto:
        try:
            as_str = line.decode()
            as_string_io = io.StringIO(as_str)
            as_list = list(csv.reader(as_string_io))[0]

            as_dict_with_field_names = {
                self.RAW_FIELD_NAMES_TO_TRANSFORMED_DATA[key]: value
                for key, value in zip(self._field_names, as_list) if key in self.RAW_FIELD_NAMES_TO_TRANSFORMED_DATA.get(key)
            }

            return models.ProtocolLineDto(**as_dict_with_field_names)
        except Exception as e:
            pass

    def _is_line_valid(self, protocol_line: models.ProtocolLineDto) -> bool:
        return all(
            [
                protocol_line,
                self._is_event_date_new_enough(protocol_line),
                self._is_containing_lobbyist(protocol_line),
            ]
        )

    def _is_event_date_new_enough(self, protocol_line: models.ProtocolLineDto) -> bool:
        return self._x_days_ago_as_datetime < protocol_line.StartDate

    def _is_containing_lobbyist(self, protocol_line: models.ProtocolLineDto) -> bool:
        pass


class KnessetProtocolLoader:
    def load(self, transformed_data):
        pass


class KnessetProtocolsETL:
    PROTOCOL_FILE_URL = "https://storage.googleapis.com/knesset-data-pipelines/data/people/committees/meeting-attendees/kns_committeesession.csv"

    def __init__(
        self,
        extractor: KnessetProtocolExtractor = KnessetProtocolExtractor(),
        transformer: KnessetProtocolTransformer = KnessetProtocolTransformer(
            x_days_ago_as_datetime=datetime.utcnow() - timedelta(days=14)
        ),
        loader: KnessetProtocolLoader = KnessetProtocolLoader(),
    ):
        self._field_names = []
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run_etl(self):
        raw_response = self.extractor.extract()
        transformed_data = self.transformer.transform(response=raw_response)
        self.loader.load(transformed_data=transformed_data)
