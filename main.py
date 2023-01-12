from lobby_actions.logic.protocol_file_logic import KnessetProtocolsETL

if __name__ == "__main__":
    retriever = KnessetProtocolsETL()

    lines = retriever.run_etl()

    x = 1
