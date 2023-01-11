from lobby_actions.logic.protocol_file_logic import KnessetProtocolsRetriever

if __name__ == "__main__":
    retriever = KnessetProtocolsRetriever()

    lines = retriever.get_events_from_last_x_days_ago_to_now()

    x = 1
