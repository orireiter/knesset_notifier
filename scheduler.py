import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BlockingScheduler

from lobby_actions.logic.lobbyist_logic import get_lobbyists_from_etl
from lobby_actions.logic.protocol_file_logic import (
    KnessetProtocolsETL,
    KnessetProtocolTransformer,
)

logger = logging.getLogger(__name__)

scheduler = BlockingScheduler()


@scheduler.scheduled_job("cron", day_of_week="sun", hour=7)
def notify_lobbyists_actions_by_mail():
    logger.info(f"{notify_lobbyists_actions_by_mail.__name__} - starting run")

    try:
        lobbyists = get_lobbyists_from_etl()
        transformer = KnessetProtocolTransformer(
            x_days_ago_as_datetime=datetime.utcnow() - timedelta(days=7),
            lobbyists_to_check=lobbyists or [],
        )
        KnessetProtocolsETL(transformer=transformer).run_etl()
    except Exception as e:
        logger.exception(f"{notify_lobbyists_actions_by_mail.__name__} - failed to run")

    logger.info(f"{notify_lobbyists_actions_by_mail.__name__} ending run")


if __name__ == "__main__":
    scheduler.start()
