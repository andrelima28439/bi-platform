import csv
import io
import logging
from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from ..models import Sale, SaleItem, Customer, Product
from .analytics_service import (
    compute_dashboard_kpis, compute_sales_report, compute_customer_report,
    compute_product_report, compute_trend_analysis,
)
from ..config import settings

logger = logging.getLogger(__name__)


def generate_csv(db: Session, report_type: str, start_date: date, end_date: date) -> str:
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == "sales":
        writer.writerow(["Invoice", "Date", "Customer", "Amount", "Discount", "Tax", "Final", "Payment", "Status"])
        sales = db.query(Sale).filter(
            cast(Sale.sale_date, Date) >= start_date,
            cast(Sale.sale_date, Date) <= end_date,
        ).all()
        for s in sales:
            writer.writerow([
                s.invoice_number, s.sale_date, s.customer_id,
                s.total_amount, s.discount, s.tax, s.final_amount,
                s.payment_method, s.status,
            ])

    elif report_type == "customers":
        writer.writerow(["Name", "Email", "City", "State", "Tier", "Purchases", "Spent", "Active"])
        customers = db.query(Customer).all()
        for c in customers:
            writer.writerow([c.name, c.email, c.city, c.state, c.tier, c.total_purchases, c.total_spent, c.is_active])

    elif report_type == "products":
        writer.writerow(["Name", "SKU", "Category", "Price", "Cost", "Stock"])
        products = db.query(Product).all()
        for p in products:
            writer.writerow([p.name, p.sku, p.category, p.unit_price, p.cost_price, p.stock_quantity])

    elif report_type == "trends":
        writer.writerow(["Date", "Revenue", "Orders"])
        data = db.query(
            cast(Sale.sale_date, Date).label("day"),
            func.sum(Sale.final_amount).label("revenue"),
            func.count(Sale.id).label("orders"),
        ).filter(
            cast(Sale.sale_date, Date) >= start_date,
            cast(Sale.sale_date, Date) <= end_date,
            Sale.status == "completed",
        ).group_by(cast(Sale.sale_date, Date)).order_by("day").all()
        for d in data:
            writer.writerow([d.day, float(d.revenue), int(d.orders)])

    return output.getvalue()


def _float_or_zero(v) -> float:
    try:
        return float(v or 0)
    except (ValueError, TypeError):
        return 0.0


def generate_pdf_report(db: Session, report_type: str, start_date: date, end_date: date) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.units import mm

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, spaceAfter=12)
    heading_style = ParagraphStyle("Heading2", parent=styles["Heading2"], fontSize=14, spaceAfter=8)
    normal_style = styles["Normal"]

    elements.append(Paragraph(f"{report_type.title()} Report", title_style))
    elements.append(Paragraph(f"Period: {start_date} to {end_date}", normal_style))
    elements.append(Spacer(1, 12))

    if report_type == "dashboard":
        kpi_data = compute_dashboard_kpis(
            db, start_date, end_date,
            start_date - (end_date - start_date),
            start_date,
        )
        kpi_table = [
            ["Metric", "Value", "Growth"],
            ["Total Revenue", f"R$ {kpi_data.total_revenue:,.2f}", f"{kpi_data.revenue_growth:+.2f}%"],
            ["Total Orders", str(kpi_data.total_orders), f"{kpi_data.orders_growth:+.2f}%"],
            ["Active Customers", str(kpi_data.active_customers), f"{kpi_data.customers_growth:+.2f}%"],
            ["Avg Order Value", f"R$ {kpi_data.avg_order_value:,.2f}", f"{kpi_data.aov_growth:+.2f}%"],
            ["Conversion Rate", f"{kpi_data.conversion_rate:.2f}%", f"{kpi_data.conversion_growth:+.2f}%"],
        ]
        t = Table(kpi_table, colWidths=[150, 150, 100])
        t.setStyle(_table_style())
        elements.append(t)

    elif report_type == "sales":
        report = compute_sales_report(db, start_date, end_date)
        data = [["Product", "Quantity", "Revenue"]]
        for p in report.top_products:
            data.append([p["name"], str(p["quantity"]), f"R$ {p['revenue']:,.2f}"])
        t = Table(data, colWidths=[200, 100, 150])
        t.setStyle(_table_style())
        elements.append(Paragraph("Top Products", heading_style))
        elements.append(t)
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Total Sales: R$ {report.total_sales:,.2f}", normal_style))
        elements.append(Paragraph(f"Total Orders: {report.total_orders}", normal_style))

    elif report_type == "customers":
        report = compute_customer_report(db, start_date, end_date)
        data = [["Name", "Spent", "Purchases", "Tier"]]
        for c in report.top_customers:
            data.append([c["name"], f"R$ {c['total_spent']:,.2f}", str(c["total_purchases"]), c["tier"]])
        t = Table(data, colWidths=[150, 120, 80, 80])
        t.setStyle(_table_style())
        elements.append(Paragraph("Top Customers", heading_style))
        elements.append(t)
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Total Customers: {report.total_customers}", normal_style))
        elements.append(Paragraph(f"Retention Rate: {report.retention_rate:.2f}%", normal_style))

    elif report_type == "products":
        report = compute_product_report(db, start_date, end_date)
        data = [["Product", "Category", "Sold", "Revenue", "Stock"]]
        for p in report.top_selling:
            data.append([
                p["name"], p["category"], str(p["quantity_sold"]),
                f"R$ {p['revenue']:,.2f}", str(p["stock"]),
            ])
        t = Table(data, colWidths=[120, 80, 60, 100, 60])
        t.setStyle(_table_style())
        elements.append(Paragraph("Top Selling Products", heading_style))
        elements.append(t)
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Total Products: {report.total_products}", normal_style))
        if report.low_stock_products:
            elements.append(Spacer(1, 10))
            ls_data = [["Product", "SKU", "Stock"]]
            for p in report.low_stock_products:
                ls_data.append([p["name"], p["sku"], str(p["stock"])])
            ls_t = Table(ls_data, colWidths=[150, 100, 70])
            ls_t.setStyle(_table_style())
            elements.append(Paragraph("Low Stock Alert", heading_style))
            elements.append(ls_t)

    doc.build(elements)
    return buffer.getvalue()


def _table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f5f5f5")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
    ])
