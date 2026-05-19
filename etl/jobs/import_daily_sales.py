import pandas as pd
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from extract import DataExtractor
from transform import DataTransformer
from load import DataLoader
from logger import setup_logger

logger = setup_logger("import_daily_sales")


def run():
    logger.info("Starting daily sales import job")

    extractor = DataExtractor()
    transformer = DataTransformer()
    loader = DataLoader()

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "daily_sales.csv")
    if os.path.exists(csv_path):
        for chunk in extractor.extract_from_csv(csv_path, chunk_size=1000):
            df = transformer.pipeline(chunk, [
                transformer.clean_data,
                lambda d: transformer.normalize_dates(d, ["sale_date"]),
                lambda d: transformer.normalize_currency(d, ["total_amount", "discount", "tax"]),
                transformer.calculate_derived_metrics,
            ])
            loader.upsert_dataframe(
                df,
                "sales",
                conflict_columns=["invoice_number"],
                batch_size=500,
            )
    else:
        logger.warning(f"CSV not found: {csv_path}")
        logger.info("Generating sample data for demo purposes")
        generate_sample_data(csv_path)

    logger.info("Daily sales import job completed")


def generate_sample_data(path: str):
    import random
    import csv
    from datetime import datetime, timedelta

    products = [
        ("PROD-001", "Notebook Pro", 150.00, 4500.00),
        ("PROD-002", "Mouse Wireless", 30.00, 89.90),
        ("PROD-003", "Teclado Mecânico", 80.00, 249.90),
        ("PROD-004", "Monitor 27\"", 200.00, 1899.00),
        ("PROD-005", "Webcam HD", 50.00, 199.90),
        ("PROD-006", "Headset Gamer", 70.00, 299.90),
        ("PROD-007", "SSD 1TB", 120.00, 499.90),
        ("PROD-008", "Memória RAM 16GB", 90.00, 349.90),
    ]
    customers = [
        ("João Silva", "joao@email.com"),
        ("Maria Santos", "maria@email.com"),
        ("Pedro Alves", "pedro@email.com"),
        ("Ana Costa", "ana@email.com"),
        ("Lucas Oliveira", "lucas@email.com"),
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "invoice_number", "customer_name", "customer_email", "sale_date",
            "product_name", "product_sku", "quantity", "unit_price", "total_amount",
            "discount", "tax", "payment_method", "status",
        ])
        for day in range(90):
            date = datetime.now() - timedelta(days=day)
            num_sales = random.randint(5, 20)
            for _ in range(num_sales):
                prod = random.choice(products)
                cust = random.choice(customers)
                qty = random.randint(1, 5)
                unit_price = prod[3]
                total = round(qty * unit_price, 2)
                discount = round(total * random.uniform(0, 0.1), 2)
                tax = round((total - discount) * 0.18, 2)
                writer.writerow([
                    f"INV-{date.strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                    cust[0], cust[1],
                    date.strftime("%Y-%m-%d"),
                    prod[1], prod[0],
                    qty, unit_price, total,
                    discount, tax,
                    random.choice(["credit_card", "boleto", "pix", "debit_card"]),
                    random.choice(["completed", "completed", "completed", "refunded"]),
                ])

    logger.info(f"Sample data generated: {path}")
