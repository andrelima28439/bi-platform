from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import engine, get_session
from logger import setup_logger
from sqlalchemy import text

logger = setup_logger("cleanup_old_data")

RETENTION_DAYS = 365
ARCHIVE_BATCH_SIZE = 5000


def run(retention_days: int = RETENTION_DAYS):
    logger.info(f"Starting old data cleanup (retention: {retention_days} days)")

    session = get_session()
    try:
        cutoff = datetime.now() - timedelta(days=retention_days)
        cutoff_str = cutoff.strftime("%Y-%m-%d")

        tables_to_clean = [
            {
                "table": "sale_items",
                "condition": "sale_id IN (SELECT id FROM sales WHERE sale_date < :cutoff)",
            },
            {
                "table": "sales",
                "condition": "sale_date < :cutoff AND status IN ('cancelled', 'refunded')",
            },
        ]

        total_deleted = 0
        for entry in tables_to_clean:
            count_query = text(
                f"SELECT COUNT(*) FROM {entry['table']} WHERE {entry['condition']}"
            )
            count = session.execute(count_query, {"cutoff": cutoff_str}).scalar() or 0

            if count > 0:
                delete_query = text(
                    f"DELETE FROM {entry['table']} WHERE {entry['condition']}"
                )
                result = session.execute(delete_query, {"cutoff": cutoff_str})
                session.commit()
                deleted = result.rowcount
                total_deleted += deleted
                logger.info(f"Cleaned {deleted} records from {entry['table']}")
            else:
                logger.info(f"No records to clean from {entry['table']}")

        cleanup_log = text("""
            INSERT INTO etl_job_logs (job_name, status, started_at, finished_at, rows_processed)
            VALUES ('cleanup_old_data', 'completed', NOW(), NOW(), :rows)
        """)
        session.execute(cleanup_log, {"rows": total_deleted})
        session.commit()

        logger.info(f"Cleanup complete. Total deleted: {total_deleted}")

    except Exception as e:
        session.rollback()
        logger.error(f"Cleanup job failed: {e}")
        raise
    finally:
        session.close()
