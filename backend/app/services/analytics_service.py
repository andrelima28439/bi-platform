from sqlalchemy.orm import Session
from sqlalchemy import func, extract, cast, Date
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import logging

from ..models import Sale, SaleItem, Customer, Product
from ..schemas import (
    DashboardKPI, SalesReport, CustomerReport, ProductReport, TrendAnalysis,
)

logger = logging.getLogger(__name__)


def _safe_div(a: float, b: float) -> float:
    return round((a / b - 1) * 100, 2) if b else 0.0


def compute_dashboard_kpis(
    db: Session, start: date, end: date, prev_start: date, prev_end: date
) -> dict:
    current = db.query(
        func.coalesce(func.sum(Sale.final_amount), 0).label("revenue"),
        func.count(Sale.id).label("orders"),
        func.count(func.distinct(Sale.customer_id)).label("customers"),
    ).filter(
        cast(Sale.sale_date, Date) >= start,
        cast(Sale.sale_date, Date) <= end,
        Sale.status == "completed",
    ).first()

    previous = db.query(
        func.coalesce(func.sum(Sale.final_amount), 0).label("revenue"),
        func.count(Sale.id).label("orders"),
        func.count(func.distinct(Sale.customer_id)).label("customers"),
    ).filter(
        cast(Sale.sale_date, Date) >= prev_start,
        cast(Sale.sale_date, Date) <= prev_end,
        Sale.status == "completed",
    ).first()

    total_revenue = float(current.revenue)
    prev_revenue = float(previous.revenue)
    total_orders = int(current.orders)
    prev_orders = int(previous.orders)
    active_customers = int(current.customers)
    prev_customers = int(previous.customers)

    avg_order_value = _safe_div(total_revenue, total_orders) if total_orders else 0
    prev_aov = _safe_div(prev_revenue, prev_orders) if prev_orders else 0
    aov_growth = _safe_div(avg_order_value, prev_aov) if prev_aov else 0

    total_visitors = db.query(func.count(func.distinct(Sale.customer_id))).filter(
        cast(Sale.sale_date, Date) >= start,
        cast(Sale.sale_date, Date) <= end,
    ).scalar() or 1

    conversion_rate = round((active_customers / total_visitors) * 100, 2)
    prev_visitors = db.query(func.count(func.distinct(Sale.customer_id))).filter(
        cast(Sale.sale_date, Date) >= prev_start,
        cast(Sale.sale_date, Date) <= prev_end,
    ).scalar() or 1
    prev_conversion = round((prev_customers / prev_visitors) * 100, 2) if prev_visitors else 0
    conversion_growth = _safe_div(conversion_rate, prev_conversion) if prev_conversion else 0

    return DashboardKPI(
        total_revenue=round(total_revenue, 2),
        revenue_growth=_safe_div(total_revenue, prev_revenue),
        total_orders=total_orders,
        orders_growth=_safe_div(total_orders, prev_orders),
        active_customers=active_customers,
        customers_growth=_safe_div(active_customers, prev_customers),
        avg_order_value=round(avg_order_value, 2),
        aov_growth=round(aov_growth, 2),
        conversion_rate=conversion_rate,
        conversion_growth=round(conversion_growth, 2),
    )


def compute_sales_report(db: Session, start: date, end: date) -> dict:
    sales = db.query(Sale).filter(
        cast(Sale.sale_date, Date) >= start,
        cast(Sale.sale_date, Date) <= end,
    ).all()

    df = pd.DataFrame([{
        "date": s.sale_date.date() if hasattr(s.sale_date, "date") else s.sale_date,
        "amount": s.final_amount,
        "payment": s.payment_method or "unknown",
        "status": s.status,
    } for s in sales])

    sales_by_day = []
    sales_by_category = []
    sales_by_payment = []
    top_products = []

    if not df.empty:
        daily = df.groupby("date")["amount"].sum().reset_index()
        sales_by_day = daily.to_dict("records")

        items = db.query(
            Product.category,
            func.sum(SaleItem.total_price).label("total"),
            func.count(SaleItem.id).label("count"),
        ).join(SaleItem, Product.id == SaleItem.product_id)\
         .join(Sale, SaleItem.sale_id == Sale.id)\
         .filter(
            cast(Sale.sale_date, Date) >= start,
            cast(Sale.sale_date, Date) <= end,
        ).group_by(Product.category).all()

        sales_by_category = [{"category": i.category, "total": round(float(i.total), 2), "count": int(i.count)} for i in items]

        if "payment" in df.columns:
            pmt = df.groupby("payment")["amount"].sum().reset_index()
            sales_by_payment = pmt.to_dict("records")

        top = db.query(
            Product.name,
            func.sum(SaleItem.quantity).label("qty"),
            func.sum(SaleItem.total_price).label("revenue"),
        ).join(SaleItem, Product.id == SaleItem.product_id)\
         .join(Sale, SaleItem.sale_id == Sale.id)\
         .filter(
            cast(Sale.sale_date, Date) >= start,
            cast(Sale.sale_date, Date) <= end,
            Sale.status == "completed",
        ).group_by(Product.name)\
         .order_by(func.sum(SaleItem.total_price).desc())\
         .limit(10).all()

        top_products = [{
            "name": t.name,
            "quantity": int(t.qty),
            "revenue": round(float(t.revenue), 2),
        } for t in top]

    total_sales = float(df["amount"].sum()) if not df.empty else 0

    return SalesReport(
        period=f"{start} to {end}",
        start_date=start,
        end_date=end,
        total_sales=round(total_sales, 2),
        total_orders=len(sales),
        sales_by_day=sales_by_day,
        sales_by_category=sales_by_category,
        sales_by_payment_method=sales_by_payment,
        top_products=top_products,
    )


def compute_customer_report(db: Session, start: date, end: date) -> dict:
    total = db.query(func.count(Customer.id)).scalar() or 0
    new_customers = db.query(func.count(Customer.id)).filter(
        cast(Customer.created_at, Date) >= start,
        cast(Customer.created_at, Date) <= end,
    ).scalar() or 0

    by_tier = db.query(
        Customer.tier,
        func.count(Customer.id).label("count"),
        func.sum(Customer.total_spent).label("revenue"),
    ).group_by(Customer.tier).all()

    customers_by_tier = [{
        "tier": t.tier,
        "count": int(t.count),
        "revenue": round(float(t.revenue or 0), 2),
    } for t in by_tier]

    by_region = db.query(
        Customer.state,
        func.count(Customer.id).label("count"),
    ).filter(Customer.state.isnot(None))\
     .group_by(Customer.state).all()

    customers_by_region = [{"state": r.state, "count": int(r.count)} for r in by_region]

    top = db.query(
        Customer.name,
        Customer.email,
        Customer.total_spent,
        Customer.total_purchases,
        Customer.tier,
    ).order_by(Customer.total_spent.desc()).limit(10).all()

    top_customers = [{
        "name": t.name,
        "email": t.email,
        "total_spent": round(float(t.total_spent or 0), 2),
        "total_purchases": int(t.total_purchases or 0),
        "tier": t.tier,
    } for t in top]

    total_customers_period = db.query(func.count(func.distinct(Sale.customer_id))).filter(
        cast(Sale.sale_date, Date) >= start,
        cast(Sale.sale_date, Date) <= end,
    ).scalar() or 0

    retention_rate = round((total_customers_period / max(total, 1)) * 100, 2)

    return CustomerReport(
        total_customers=int(total),
        new_customers=int(new_customers),
        customers_by_tier=customers_by_tier,
        customers_by_region=customers_by_region,
        top_customers=top_customers,
        retention_rate=retention_rate,
    )


def compute_product_report(db: Session, start: date, end: date) -> dict:
    total_products = db.query(func.count(Product.id)).scalar() or 0

    top = db.query(
        Product.id,
        Product.name,
        Product.sku,
        Product.category,
        func.sum(SaleItem.quantity).label("qty_sold"),
        func.sum(SaleItem.total_price).label("revenue"),
        Product.stock_quantity,
    ).join(SaleItem, Product.id == SaleItem.product_id)\
     .join(Sale, SaleItem.sale_id == Sale.id)\
     .filter(
        cast(Sale.sale_date, Date) >= start,
        cast(Sale.sale_date, Date) <= end,
        Sale.status == "completed",
    ).group_by(Product.id, Product.name, Product.sku, Product.category, Product.stock_quantity)\
     .order_by(func.sum(SaleItem.quantity).desc())\
     .limit(20).all()

    top_selling = [{
        "id": t.id,
        "name": t.name,
        "sku": t.sku,
        "category": t.category,
        "quantity_sold": int(t.qty_sold),
        "revenue": round(float(t.revenue), 2),
        "stock": int(t.stock_quantity),
    } for t in top]

    by_cat = db.query(
        Product.category,
        func.count(Product.id).label("count"),
        func.sum(Product.stock_quantity).label("total_stock"),
    ).group_by(Product.category).all()

    products_by_category = [{
        "category": c.category,
        "count": int(c.count),
        "total_stock": int(c.total_stock or 0),
    } for c in by_cat]

    low_stock = db.query(
        Product.id, Product.name, Product.sku, Product.stock_quantity, Product.category
    ).filter(Product.stock_quantity < 10).order_by(Product.stock_quantity.asc()).limit(20).all()

    low_stock_products = [{
        "id": p.id,
        "name": p.name,
        "sku": p.sku,
        "stock": int(p.stock_quantity),
        "category": p.category,
    } for p in low_stock]

    return ProductReport(
        total_products=int(total_products),
        top_selling=top_selling,
        products_by_category=products_by_category,
        low_stock_products=low_stock_products,
    )


def compute_trend_analysis(db: Session, start: date, end: date, granularity: str = "month") -> dict:
    sales_data = db.query(
        cast(Sale.sale_date, Date).label("day"),
        func.sum(Sale.final_amount).label("revenue"),
        func.count(Sale.id).label("orders"),
    ).filter(
        cast(Sale.sale_date, Date) >= start,
        cast(Sale.sale_date, Date) <= end,
        Sale.status == "completed",
    ).group_by(cast(Sale.sale_date, Date)).order_by("day").all()

    df = pd.DataFrame([{
        "date": pd.Timestamp(s.day),
        "revenue": float(s.revenue),
        "orders": int(s.orders),
    } for s in sales_data])

    revenue_trend = []
    customer_growth = []
    seasonal = []

    if not df.empty:
        df["month"] = df["date"].dt.to_period("M").astype(str)
        monthly = df.groupby("month")[["revenue", "orders"]].sum().reset_index()
        revenue_trend = monthly.to_dict("records")

        customer_data = db.query(
            cast(Customer.created_at, Date).label("day"),
            func.count(Customer.id).label("new"),
        ).filter(
            cast(Customer.created_at, Date) >= start,
            cast(Customer.created_at, Date) <= end,
        ).group_by(cast(Customer.created_at, Date)).order_by("day").all()

        cdf = pd.DataFrame([{"date": pd.Timestamp(c.day), "new": int(c.new)} for c in customer_data])
        if not cdf.empty:
            cdf["month"] = cdf["date"].dt.to_period("M").astype(str)
            cg = cdf.groupby("month")["new"].sum().reset_index()
            customer_growth = cg.to_dict("records")

        df["month_num"] = df["date"].dt.month
        seas = df.groupby("month_num")["revenue"].agg(["mean", "std"]).reset_index()
        seasonal = [
            {"month": int(r.month_num), "avg_revenue": round(float(r["mean"]), 2), "std": round(float(r["std"]), 2)}
            for _, r in seas.iterrows()
        ]

    forecast = []
    if len(df) > 2:
        ts = df.set_index("date")["revenue"]
        if len(ts) >= 3:
            last_val = float(ts.iloc[-1])
            growth_rate = 0.05
            for i in range(1, 7):
                forecast.append({
                    "period": f"forecast_{i}",
                    "predicted_revenue": round(last_val * (1 + growth_rate) ** i, 2),
                })

    return TrendAnalysis(
        revenue_trend=revenue_trend,
        customer_growth_trend=customer_growth,
        seasonal_patterns=seasonal,
        forecast=forecast,
    )
