import pandas as pd
from sqlalchemy import Table, MetaData, inspect
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from typing import Optional
from database import engine, get_session
from logger import setup_logger

logger = setup_logger("load")


class DataLoader:
    def __init__(self):
        self.metadata = MetaData()
        self.metadata.reflect(bind=engine)

    def table_exists(self, table_name: str) -> bool:
        return inspect(engine).has_table(table_name)

    def load_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = "append",
        schema: Optional[str] = None,
        batch_size: int = 1000,
    ) -> dict:
        initial_count = len(df)

        if df.empty:
            logger.warning(f"No data to load into {table_name}")
            return {"status": "skipped", "rows_loaded": 0}

        try:
            df.to_sql(
                name=table_name,
                con=engine,
                schema=schema,
                if_exists=if_exists,
                index=False,
                method="multi",
                chunksize=batch_size,
            )
            logger.info(f"Loaded {initial_count} rows into {table_name}")
            return {"status": "success", "rows_loaded": initial_count}

        except Exception as e:
            logger.error(f"Failed to load data into {table_name}: {e}")
            raise

    def upsert_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        conflict_columns: list[str],
        schema: Optional[str] = None,
        batch_size: int = 1000,
    ) -> dict:
        if df.empty:
            return {"status": "skipped", "rows_loaded": 0}

        table = Table(
            table_name,
            self.metadata,
            schema=schema,
            autoload_with=engine,
        )

        conn = engine.connect()
        try:
            total = 0
            for start in range(0, len(df), batch_size):
                batch = df.iloc[start : start + batch_size]
                stmt = insert(table).values(batch.to_dict(orient="records"))
                stmt = stmt.on_conflict_do_update(
                    index_elements=conflict_columns,
                    set_={c.name: stmt.excluded[c.name] for c in table.columns if c.name not in conflict_columns},
                )
                conn.execute(stmt)
                total += len(batch)

            conn.commit()
            logger.info(f"Upserted {total} rows into {table_name}")
            return {"status": "success", "rows_loaded": total}

        except Exception as e:
            conn.rollback()
            logger.error(f"Upsert failed for {table_name}: {e}")
            raise
        finally:
            conn.close()

    def incremental_load(
        self,
        df: pd.DataFrame,
        table_name: str,
        key_column: str,
        date_column: str,
        schema: Optional[str] = None,
    ) -> dict:
        if not self.table_exists(table_name):
            return self.load_dataframe(df, table_name, schema=schema)

        with engine.connect() as conn:
            latest = conn.execute(
                f'SELECT MAX("{date_column}") FROM {f"{schema}." if schema else ""}"{table_name}"'
            ).scalar()

        if latest:
            df = df[df[date_column] > pd.Timestamp(latest)]
            logger.info(f"Incremental load: {len(df)} new records since {latest}")
        else:
            logger.info(f"Incremental load: no previous data, loading all {len(df)} records")

        return self.load_dataframe(df, table_name, if_exists="append", schema=schema)
