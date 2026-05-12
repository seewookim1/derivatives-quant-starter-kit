"""APScheduler 스케줄러 - EOD 배치 및 장중 주기 태스크"""

from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


def build_scheduler() -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone="Asia/Seoul")

    # EOD VaR 계산: 매 영업일 16:30 KST
    from hdesk.workers.tasks.eod_var import run_eod_var
    scheduler.add_job(
        run_eod_var,
        CronTrigger(hour=16, minute=30, day_of_week="mon-fri"),
        id="eod_var",
        misfire_grace_time=300,
        replace_existing=True,
    )

    # 변동성 서피스 재보정: 장중 5분마다 (09:00-15:30 KST)
    from hdesk.workers.tasks.vol_surface_fit import refresh_vol_surface
    scheduler.add_job(
        refresh_vol_surface,
        IntervalTrigger(minutes=5),
        id="vol_surface_refresh",
        replace_existing=True,
    )

    # EOD P&L 보고서: 매 영업일 17:00 KST
    from hdesk.workers.tasks.pnl_report import generate_pnl_report
    scheduler.add_job(
        generate_pnl_report,
        CronTrigger(hour=17, minute=0, day_of_week="mon-fri"),
        id="pnl_report",
        misfire_grace_time=600,
        replace_existing=True,
    )

    # 틱 데이터 정리: 매일 자정
    from hdesk.workers.tasks.data_cleanup import cleanup_old_data
    scheduler.add_job(
        cleanup_old_data,
        CronTrigger(hour=0, minute=0),
        id="data_cleanup",
        replace_existing=True,
    )

    return scheduler


def run() -> None:
    from hdesk.utils.logging import setup_logging
    from hdesk.utils.config import get_settings

    settings = get_settings()
    setup_logging(settings.log_level, settings.log_format)

    scheduler = build_scheduler()
    logger.info("스케줄러 시작: %d 잡 등록", len(scheduler.get_jobs()))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("스케줄러 종료")
        scheduler.shutdown()


if __name__ == "__main__":
    run()
