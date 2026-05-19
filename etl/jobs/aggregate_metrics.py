import pandas as pd
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import engine, get_session
from transform import DataTransformer
from logger import setup_logger

logger = setup_logger("aggregate_metrics")


def run():
    logger.info("Starting metrics aggregation job")

    transformer = DataTransformer()
    session = get_session()

    try:
        query = """
            SELECT
                s.id as sale_id,
                s.sale_date,
                s.final_amount,
                s.discount,
                s.tax,
                s.payment_method,
                s.status,
                c.id as customer_id,
                c.name as customer_name,
                c.city,
                c.state
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            WHERE s.sale_date >= NOW() - INTERVAL '30 days'
            ORDER BY s.sale_date
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            logger.info("No sales data to aggregate")
            return

        daily_sales = df.groupby(
            pd.Grouper(key="sale_date", freq="D")
        ).agg(
            total_revenue=("final_amount", "sum"),
            total_orders=("sale_id", "count"),
            avg_ticket=("final_amount", "mean"),
            total_discount=("discount", "sum"),
        ).reset_index()

        daily_sales.to_sql(
            "daily_metrics",
            engine,
            if_exists="replace",
            index=False,
        )
        logger.info(f"Aggregated {len(daily_sales)} daily metrics records")

        category_query = """
            SELECT
                p.category,
                SUM(si.quantity) as total_quantity,
                SUM(si.total_price) as total_revenue,
                COUNT(DISTINCT s.id) as order_count
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            JOIN sales s ON si.sale_id = s.id
            WHERE s.sale_date >= NOW() - INTERVAL '30 days'
            GROUP BY p.category
        """
        cat_df = pd.read_sql(category_query, engine)
        cat_df.to_sql("category_metrics", engine, if_exists="replace", index=False)
        logger.info(f"Aggregated {len(cat_df)} category metrics")

        logger.info("Metrics aggregation job completed")

    except Exception as e:
        logger.error(f"Aggregation job failed: {e}")
        raise
    finally:
        session.close()
