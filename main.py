import logging.config

from lobby_actions.config.logging_config import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)


from lobby_actions.logic.protocol_file_logic import KnessetProtocolsETL


if __name__ == "__main__":

    retriever = KnessetProtocolsETL()

    lines = retriever.run_etl()

    x = 1
