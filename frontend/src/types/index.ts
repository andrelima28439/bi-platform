export interface DashboardKPI {
  total_revenue: number
  revenue_growth: number
  total_orders: number
  orders_growth: number
  active_customers: number
  customers_growth: number
  avg_order_value: number
  aov_growth: number
  conversion_rate: number
  conversion_growth: number
}

export interface SalesReport {
  period: string
  start_date: string
  end_date: string
  total_sales: number
  total_orders: number
  sales_by_day: { date: string; amount: number }[]
  sales_by_category: { category: string; total: number; count: number }[]
  sales_by_payment_method: { payment: string; amount: number }[]
  top_products: { name: string; quantity: number; revenue: number }[]
}

export interface CustomerReport {
  total_customers: number
  new_customers: number
  customers_by_tier: { tier: string; count: number; revenue: number }[]
  customers_by_region: { state: string; count: number }[]
  top_customers: {
    name: string
    email: string
    total_spent: number
    total_purchases: number
    tier: string
  }[]
  retention_rate: number
}

export interface ProductReport {
  total_products: number
  top_selling: {
    id: number
    name: string
    sku: string
    category: string
    quantity_sold: number
    revenue: number
    stock: number
  }[]
  products_by_category: { category: string; count: number; total_stock: number }[]
  low_stock_products: { id: number; name: string; sku: string; stock: number; category: string }[]
}

export interface TrendAnalysis {
  revenue_trend: { month: string; revenue: number; orders: number }[]
  customer_growth_trend: { month: string; new: number }[]
  seasonal_patterns: { month: number; avg_revenue: number; std: number }[]
  forecast: { period: string; predicted_revenue: number }[]
}

export interface PeriodFilter {
  start_date?: string
  end_date?: string
  period?: 'today' | 'week' | 'month' | 'year' | 'custom'
}
