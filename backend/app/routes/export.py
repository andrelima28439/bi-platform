from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import date, timedelta
import csv
import io
import logging

from ..database import get_db
from ..services.export_service import generate_csv, generate_pdf_report

router = APIRouter(prefix="/export", tags=["Export"])
logger = logging.getLogger(__name__)


@router.get("/csv")
async def export_csv(
    report_type: str = Query(..., regex="^(sales|customers|products|trends)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    end_date = end_date or date.today()
    start_date = start_date or (end_date - timedelta(days=30))

    csv_data = generate_csv(db, report_type, start_date, end_date)
    filename = f"{report_type}_{start_date}_{end_date}.csv"

    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/pdf")
async def export_pdf(
    report_type: str = Query(..., regex="^(sales|customers|products|dashboard)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    end_date = end_date or date.today()
    start_date = start_date or (end_date - timedelta(days=30))

    pdf_buffer = generate_pdf_report(db, report_type, start_date, end_date)
    filename = f"{report_type}_{start_date}_{end_date}.pdf"

    return StreamingResponse(
        iter([pdf_buffer]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
