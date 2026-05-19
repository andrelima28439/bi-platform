from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_dashboard():
    response = client.get("/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "total_orders" in data


def test_sales_report():
    response = client.get("/analytics/sales?period=month")
    assert response.status_code == 200
    data = response.json()
    assert "total_sales" in data
    assert "total_orders" in data


def test_customers_report():
    response = client.get("/analytics/customers")
    assert response.status_code == 200
    data = response.json()
    assert "total_customers" in data
    assert "new_customers" in data


def test_products_report():
    response = client.get("/analytics/products")
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "top_selling" in data


def test_trends():
    response = client.get("/analytics/trends?months=6")
    assert response.status_code == 200
    data = response.json()
    assert "revenue_trend" in data
    assert "customer_growth_trend" in data


def test_custom_query():
    response = client.post(
        "/analytics/custom-query",
        json={"query": "SELECT 1 as test"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "columns" in data
    assert "rows" in data


def test_export_csv():
    response = client.get("/export/csv?report_type=sales")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"


def test_export_pdf():
    response = client.get("/export/pdf?report_type=dashboard")
    assert response.status_code == 200
    assert "application/pdf" in response.headers["content-type"]
