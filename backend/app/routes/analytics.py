from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from datetime import date, datetime, timedelta
import time
import logging

from ..database import get_db
from ..models import Sale, SaleItem, Customer, Product
from ..schemas import (
    DashboardKPI, SalesReport, CustomerReport, ProductReport,
    TrendAnalysis, CustomQuery, CustomQueryResponse, PeriodFilter,
)
from ..cache import cache_get, cache_set, cache_invalidate
from ..services.analytics_service import (
    compute_dashboard_kpis, compute_sales_report, compute_customer_report,
    compute_product_report, compute_trend_analysis,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = logging.getLogger(__name__)


@router.get("/dashboard", response_model=DashboardKPI)
async def get_dashboard(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    params = {"start_date": str(start_date), "end_date": str(end_date)}
    cached = await cache_get("dashboard", params)
    if cached:
        return cached

    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=(end_date - start_date).days)

    result = compute_dashboard_kpis(db, start_date, end_date, prev_start, prev_end)
    await cache_set("dashboard", result, params)
    return result


@router.get("/sales", response_model=SalesReport)
async def get_sales_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    period: Optional[str] = Query(None, regex="^(today|week|month|year|custom)$"),
    db: Session = Depends(get_db),
):
    params = {"start_date": str(start_date), "end_date": str(end_date), "period": period}
    cached = await cache_get("sales", params)
    if cached:
        return cached

    end_date = end_date or date.today()
    if period == "today":
        start_date = end_date
    elif period == "week":
        start_date = end_date - timedelta(days=7)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "year":
        start_date = end_date - timedelta(days=365)
    elif not start_date:
        start_date = end_date - timedelta(days=30)

    result = compute_sales_report(db, start_date, end_date)
    await cache_set("sales", result, params)
    return result


@router.get("/customers", response_model=CustomerReport)
async def get_customers_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    params = {"start_date": str(start_date), "end_date": str(end_date)}
    cached = await cache_get("customers", params)
    if cached:
        return cached

    end_date = end_date or date.today()
    start_date = start_date or (end_date - timedelta(days=30))

    result = compute_customer_report(db, start_date, end_date)
    await cache_set("customers", result, params)
    return result


@router.get("/products", response_model=ProductReport)
async def get_products_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    params = {"start_date": str(start_date), "end_date": str(end_date)}
    cached = await cache_get("products", params)
    if cached:
        return cached

    end_date = end_date or date.today()
    start_date = start_date or (end_date - timedelta(days=30))

    result = compute_product_report(db, start_date, end_date)
    await cache_set("products", result, params)
    return result


@router.get("/trends", response_model=TrendAnalysis)
async def get_trends(
    months: Optional[int] = Query(12, ge=1, le=36),
    db: Session = Depends(get_db),
):
    params = {"months": months}
    cached = await cache_get("trends", params)
    if cached:
        return cached

    end_date = date.today()
    start_date = end_date - timedelta(days=30 * months)

    result = compute_trend_analysis(db, start_date, end_date)
    await cache_set("trends", result, params)
    return result


@router.post("/custom-query", response_model=CustomQueryResponse)
async def custom_query(query_data: CustomQuery, db: Session = Depends(get_db)):
    start_time = time.time()
    try:
        result = db.execute(text(query_data.query), query_data.params or {})
        columns = list(result.keys())
        rows = [list(row) for row in result.fetchall()]
        execution_time = (time.time() - start_time) * 1000
        return CustomQueryResponse(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            execution_time_ms=round(execution_time, 2),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cache/invalidate")
async def invalidate_cache(pattern: str = "all"):
    await cache_invalidate(pattern)
    return {"message": f"Cache invalidated for pattern: {pattern}"}
