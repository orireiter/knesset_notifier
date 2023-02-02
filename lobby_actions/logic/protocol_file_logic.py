import io
import csv
import logging
from collections import defaultdict
from datetime import datetime, timedelta

import requests

from lobby_actions.data import models
from lobby_actions.third_parties.gmail import GmailSmtp
from lobby_actions.config.lobby99_config import Lobby99Config

logger = logging.getLogger(__name__)


class KnessetProtocolExtractor:
    PROTOCOL_FILE_URL = "https://storage.googleapis.com/knesset-data-pipelines/data/people/committees/meeting-attendees/kns_committeesession.csv"

    def extract(self):
        logger.info(
            f"{self.__class__.__name__} - opening http stream to get file from url - {self.PROTOCOL_FILE_URL}"
        )
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

    def __init__(
        self,
        x_days_ago_as_datetime: datetime = datetime.utcnow() - timedelta(days=14),
        lobbyists_to_check: list[str] = None,
    ):
        self._x_days_ago_as_datetime = x_days_ago_as_datetime
        self._field_names = []
        self.lobbyists_to_check = lobbyists_to_check or []
        self.lobbyists_activity_summary = defaultdict(list)

    def transform(self, response: requests.Response):
        self._field_names = self._get_key_names_of_file(response=response)

        for line in response.iter_lines():
            try:
                as_dto = self._transform_line_to_dto(line=line)

                if self._is_line_valid(as_dto):
                    self._append_line_to_relevant_lobbyists_summary(
                        protocol_line=as_dto
                    )
            except Exception as e:
                continue

        return self.lobbyists_activity_summary

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
                for key, value in zip(self._field_names, as_list)
                if self.RAW_FIELD_NAMES_TO_TRANSFORMED_DATA.get(key)
            }

            logger.info(f"transforming {as_dict_with_field_names=}")
            return models.ProtocolLineDto(**as_dict_with_field_names)
        except Exception as e:
            logger.exception(f"failed to transfrom line to dto {line.decode()}")
            raise e

    def _is_line_valid(self, protocol_line: models.ProtocolLineDto) -> bool:
        return all(
            [
                protocol_line,
                self._is_event_date_new_enough(protocol_line),
            ]
        )

    def _is_event_date_new_enough(self, protocol_line: models.ProtocolLineDto) -> bool:
        return self._x_days_ago_as_datetime < protocol_line.start_date

    def _append_line_to_relevant_lobbyists_summary(
        self, protocol_line: models.ProtocolLineDto
    ):
        invitees_names = {
            invitee_dict.get("name") for invitee_dict in protocol_line.invitees
        }
        for lobbyist_name in self.lobbyists_to_check:
            for invitee_name in invitees_names:
                if lobbyist_name in invitee_name:
                    self.lobbyists_activity_summary[lobbyist_name].append(protocol_line)


class KnessetProtocolLoader:
    def load(self, transformed_data: dict):
        if not transformed_data:
            return

        try:
            mail_content = self._transform_data_to_mail_content(transformed_data)
            GmailSmtp().send_mail(
                receivers=Lobby99Config.Email.LOBBY_ACTION_EMAILS_TO_REPORT_TO,
                subject="דו״ח פעילות לוביסטים שבועית",
                content=mail_content,
                is_rtl=True,
            )
        except Exception as e:
            pass

    def _transform_data_to_mail_content(self, data: dict) -> str:
        mail_content = "דו״ח פעילות לוביסטים שבועית:" + "\n\n"

        for lobbyist_name, attended_events in data.items():
            mail_content += f"{lobbyist_name}:\n"

            for event in attended_events:
                mail_content += (
                    f"{event.start_date} - {event.committee_name} - {event.topics}\n"
                )

            mail_content += "\n"

        return mail_content


class KnessetProtocolsETL:
    def __init__(
        self,
        extractor: KnessetProtocolExtractor = KnessetProtocolExtractor(),
        transformer: KnessetProtocolTransformer = KnessetProtocolTransformer(
            x_days_ago_as_datetime=datetime.utcnow() - timedelta(days=7)
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
