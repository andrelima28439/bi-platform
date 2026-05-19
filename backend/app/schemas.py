from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime, date


class ProductBase(BaseModel):
    name: str
    sku: str
    category: str
    description: Optional[str] = None
    unit_price: float
    cost_price: Optional[float] = None
    stock_quantity: int = 0


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "Brazil"


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    tier: str
    total_purchases: int
    total_spent: float
    first_purchase_date: Optional[datetime] = None
    last_purchase_date: Optional[datetime] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SaleItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    total_price: float


class SaleCreate(BaseModel):
    invoice_number: str
    customer_id: int
    sale_date: datetime
    total_amount: float
    discount: float = 0.0
    tax: float = 0.0
    final_amount: float
    payment_method: Optional[str] = None
    status: str = "completed"
    items: List[SaleItemBase]


class SaleItemResponse(SaleItemBase):
    id: int
    sale_id: int
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    customer: Optional[CustomerResponse] = None
    sale_date: datetime
    total_amount: float
    discount: float
    tax: float
    final_amount: float
    payment_method: Optional[str] = None
    status: str
    items: List[SaleItemResponse] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DashboardKPI(BaseModel):
    total_revenue: float
    revenue_growth: float
    total_orders: int
    orders_growth: float
    active_customers: int
    customers_growth: float
    avg_order_value: float
    aov_growth: float
    conversion_rate: float
    conversion_growth: float


class SalesReport(BaseModel):
    period: str
    start_date: date
    end_date: date
    total_sales: float
    total_orders: int
    sales_by_day: List[dict]
    sales_by_category: List[dict]
    sales_by_payment_method: List[dict]
    top_products: List[dict]


class CustomerReport(BaseModel):
    total_customers: int
    new_customers: int
    customers_by_tier: List[dict]
    customers_by_region: List[dict]
    top_customers: List[dict]
    retention_rate: float


class ProductReport(BaseModel):
    total_products: int
    top_selling: List[dict]
    products_by_category: List[dict]
    low_stock_products: List[dict]


class TrendAnalysis(BaseModel):
    revenue_trend: List[dict]
    customer_growth_trend: List[dict]
    seasonal_patterns: List[dict]
    forecast: List[dict]


class CustomQuery(BaseModel):
    query: str
    params: Optional[dict] = None


class CustomQueryResponse(BaseModel):
    columns: List[str]
    rows: List[list]
    row_count: int
    execution_time_ms: float


class ExportRequest(BaseModel):
    report_type: str
    format: str
    filters: Optional[dict] = None


class PeriodFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    period: Optional[str] = None
