from apscheduler.schedulers.background import BlockingScheduler

from lobby_actions.logic.protocol_file_logic import KnessetProtocolsETL, KnessetProtocolTransformer
from lobby_actions.logic.lobbyist_logic import get_lobbyists_from_etl

scheduler = BlockingScheduler()


@scheduler.scheduled_job('cron', day_of_week='sun', hour=7)
def notify_lobbyists_actions_by_mail():
    try:
        lobbyists = get_lobbyists_from_etl()
        transformer = KnessetProtocolTransformer(lobbyists_to_check=lobbyists or [])
        KnessetProtocolsETL(transformer=transformer).run_etl()
    except Exception as e:
        pass


if __name__ == '__main__':
    scheduler.start()
