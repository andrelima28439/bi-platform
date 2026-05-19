import pandas as pd
import requests
import csv
import json
import os
from typing import Optional, Generator
from datetime import datetime
from logger import setup_logger

logger = setup_logger("extract")


class DataExtractor:
    def __init__(self):
        self.session = requests.Session()

    def extract_from_api(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        pagination: bool = False,
        page_size: int = 100,
    ) -> list[dict]:
        all_data = []
        page = 1

        try:
            while True:
                req_params = {**(params or {})}
                if pagination:
                    req_params["page"] = page
                    req_params["per_page"] = page_size

                resp = self.session.get(url, params=req_params, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()

                if isinstance(data, list):
                    all_data.extend(data)
                    if not pagination or len(data) < page_size:
                        break
                elif isinstance(data, dict):
                    items = data.get("results", data.get("data", data.get("items", [data])))
                    all_data.extend(items if isinstance(items, list) else [items])
                    if not pagination:
                        break

                page += 1

            logger.info(f"Extracted {len(all_data)} records from API: {url}")
            return all_data

        except requests.RequestException as e:
            logger.error(f"API extraction failed for {url}: {e}")
            raise

    def extract_from_csv(
        self,
        filepath: str,
        delimiter: str = ",",
        encoding: str = "utf-8",
        chunk_size: Optional[int] = None,
    ) -> Generator[pd.DataFrame, None, None]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        logger.info(f"Extracting from CSV: {filepath}")

        if chunk_size:
            for chunk in pd.read_csv(
                filepath,
                delimiter=delimiter,
                encoding=encoding,
                chunksize=chunk_size,
            ):
                logger.info(f"Extracted chunk with {len(chunk)} rows")
                yield chunk
        else:
            df = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding)
            logger.info(f"Extracted {len(df)} rows from CSV")
            yield df

    def extract_from_json(self, filepath: str) -> list[dict]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"JSON file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = data if isinstance(data, list) else data.get("records", data.get("data", []))
        logger.info(f"Extracted {len(records)} records from JSON: {filepath}")
        return records

    def extract_from_excel(self, filepath: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Excel file not found: {filepath}")

        df = pd.read_excel(filepath, sheet_name=sheet_name)
        logger.info(f"Extracted {len(df)} rows from Excel: {filepath}")
        return df

    def validate_data(self, data: list[dict], required_fields: list[str]) -> list[dict]:
        valid = []
        errors = 0
        for i, record in enumerate(data):
            missing = [f for f in required_fields if f not in record]
            if missing:
                errors += 1
                logger.warning(f"Record {i} missing fields: {missing}")
            else:
                valid.append(record)

        logger.info(f"Validation: {len(valid)} valid, {errors} invalid records")
        return valid
