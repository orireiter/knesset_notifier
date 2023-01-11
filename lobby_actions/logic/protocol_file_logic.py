import io
import csv
from datetime import datetime, timedelta

import requests

from lobby_actions.data import models


class KnessetProtocolsRetriever:
    PROTOCOL_FILE_URL = "https://storage.googleapis.com/knesset-data-pipelines/data/people/committees/meeting-attendees/kns_committeesession.csv"

    def __init__(self, x_days_ago: int = 14):
        self.x_days_ago_as_datetime = datetime.utcnow() - timedelta(days=x_days_ago)
        self._field_names = []

    def get_events_from_last_x_days_ago_to_now(self):
        with requests.get(self.PROTOCOL_FILE_URL, stream=True) as response:
            self._field_names = self._get_key_names_of_file(response=response)
            relevant_lines = self._get_only_relevant_lines(response=response)

        return relevant_lines

    def _get_key_names_of_file(self, response: requests.Response) -> list:
        field_names_as_str: str = response.iter_lines().__next__().decode()

        return field_names_as_str.split(",")

    def _get_only_relevant_lines(
        self, response: requests.Response
    ) -> list[models.ProtocolLineDto]:
        relevant_lines = []
        for line in response.iter_lines():
            as_dto = self._transform_line_to_dto(line=line)

            if self._is_line_valid(as_dto):
                relevant_lines.append(as_dto)

        return relevant_lines

    def _transform_line_to_dto(self, line: bytes) -> models.ProtocolLineDto:
        try:
            as_str = line.decode()
            as_string_io = io.StringIO(as_str)
            as_list = list(csv.reader(as_string_io))[0]

            as_dict_with_field_names = {
                key: value for key, value in zip(self._field_names, as_list)
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
        return self.x_days_ago_as_datetime < protocol_line.StartDate

    def _is_containing_lobbyist(self, protocol_line: models.ProtocolLineDto) -> bool:
        pass
