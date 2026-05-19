import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Callable
from logger import setup_logger

logger = setup_logger("transform")


class DataTransformer:
    def __init__(self):
        self.transformations_log = []

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        initial_count = len(df)
        df = df.copy()

        df = df.drop_duplicates()
        dups_removed = initial_count - len(df)

        df = df.replace([np.inf, -np.inf], np.nan)

        str_cols = df.select_dtypes(include=["object"]).columns
        for col in str_cols:
            df[col] = df[col].fillna("").astype(str).str.strip()

        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)

        self.transformations_log.append(f"Cleaned: {dups_removed} dups removed, NaNs handled")
        logger.info(f"Data cleaning complete. {len(df)} rows remaining")
        return df

    def normalize_dates(
        self,
        df: pd.DataFrame,
        columns: list[str],
        format: Optional[str] = None,
    ) -> pd.DataFrame:
        df = df.copy()
        for col in columns:
            if col in df.columns:
                try:
                    if format:
                        df[col] = pd.to_datetime(df[col], format=format, errors="coerce")
                    else:
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                    self.transformations_log.append(f"Normalized date column: {col}")
                except Exception as e:
                    logger.warning(f"Failed to normalize date column {col}: {e}")
        return df

    def normalize_currency(
        self,
        df: pd.DataFrame,
        columns: list[str],
    ) -> pd.DataFrame:
        df = df.copy()
        for col in columns:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace("R\$", "", regex=True)
                    .str.replace(" ", "")
                    .str.replace(".", "")
                    .str.replace(",", ".")
                    .str.replace("$", "")
                    .astype(float)
                )
                self.transformations_log.append(f"Normalized currency column: {col}")
        return df

    def apply_mapping(
        self,
        df: pd.DataFrame,
        column: str,
        mapping: dict,
        default: Optional[str] = None,
    ) -> pd.DataFrame:
        df = df.copy()
        if column in df.columns:
            df[column] = df[column].map(mapping).fillna(default or df[column])
            self.transformations_log.append(f"Mapped column: {column}")
        return df

    def aggregate_sales(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        group_col: Optional[str] = None,
    ) -> pd.DataFrame:
        group_by = [pd.Grouper(key=date_col, freq="D")]
        if group_col:
            group_by.append(group_col)

        agg = df.groupby(group_by)[value_col].sum().reset_index()
        logger.info(f"Aggregated sales data into {len(agg)} rows")
        return agg

    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if all(c in df.columns for c in ["quantity", "unit_price"]):
            df["total_price"] = df["quantity"] * df["unit_price"]

        if all(c in df.columns for c in ["total_amount", "discount", "tax"]):
            df["final_amount"] = df["total_amount"] - df["discount"] + df["tax"]

        if "sale_date" in df.columns and "customer_id" in df.columns:
            df["purchase_month"] = pd.to_datetime(df["sale_date"]).dt.to_period("M")

        self.transformations_log.append("Calculated derived metrics")
        return df

    def pipeline(self, df: pd.DataFrame, steps: list[Callable]) -> pd.DataFrame:
        logger.info(f"Starting transformation pipeline with {len(steps)} steps")
        for step in steps:
            try:
                df = step(df)
                logger.info(f"Step {step.__name__} completed")
            except Exception as e:
                logger.error(f"Step {step.__name__} failed: {e}")
                raise
        logger.info(f"Transformation pipeline complete. {len(df)} rows output")
        return df
