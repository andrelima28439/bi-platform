import sys
import os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

sys.path.insert(0, os.path.dirname(__file__))
from logger import setup_logger
from jobs.import_daily_sales import run as run_import_sales
from jobs.aggregate_metrics import run as run_aggregate_metrics
from jobs.cleanup_old_data import run as run_cleanup

logger = setup_logger("etl_runner")


def run_import_job():
    logger.info("=" * 50)
    logger.info("Starting scheduled ETL: Import Daily Sales")
    try:
        run_import_sales()
        logger.info("Import Daily Sales completed successfully")
    except Exception as e:
        logger.error(f"Import Daily Sales failed: {e}")
    logger.info("=" * 50)


def run_aggregation_job():
    logger.info("=" * 50)
    logger.info("Starting scheduled ETL: Aggregate Metrics")
    try:
        run_aggregate_metrics()
        logger.info("Aggregate Metrics completed successfully")
    except Exception as e:
        logger.error(f"Aggregate Metrics failed: {e}")
    logger.info("=" * 50)


def run_cleanup_job():
    logger.info("=" * 50)
    logger.info("Starting scheduled ETL: Cleanup Old Data")
    try:
        run_cleanup(retention_days=365)
        logger.info("Cleanup completed successfully")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
    logger.info("=" * 50)


def run_once():
    logger.info("Running ETL jobs sequentially (one-time)")
    run_import_job()
    run_aggregation_job()
    run_cleanup_job()
    logger.info("All ETL jobs completed")


def start_scheduler():
    scheduler = BlockingScheduler()

    scheduler.add_job(
        run_import_job,
        CronTrigger(hour=2, minute=0),
        id="daily_sales_import",
        name="Import daily sales data",
    )

    scheduler.add_job(
        run_aggregation_job,
        CronTrigger(hour=3, minute=0),
        id="daily_aggregation",
        name="Aggregate daily metrics",
    )

    scheduler.add_job(
        run_cleanup_job,
        CronTrigger(hour=4, minute=0, day_of_week="sun"),
        id="weekly_cleanup",
        name="Weekly old data cleanup",
    )

    logger.info("ETL Scheduler started. Jobs will run at configured times.")
    logger.info("  - Daily Sales Import: 02:00")
    logger.info("  - Daily Aggregation: 03:00")
    logger.info("  - Weekly Cleanup: Sunday 04:00")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "once":
            run_once()
        elif sys.argv[1] == "schedule":
            start_scheduler()
        elif sys.argv[1] == "import":
            run_import_job()
        elif sys.argv[1] == "aggregate":
            run_aggregation_job()
        elif sys.argv[1] == "cleanup":
            run_cleanup_job()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python runner.py [once|schedule|import|aggregate|cleanup]")
    else:
        run_once()
