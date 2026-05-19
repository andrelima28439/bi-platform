import axios from 'axios'
import type {
  DashboardKPI,
  SalesReport,
  CustomerReport,
  ProductReport,
  TrendAnalysis,
  PeriodFilter,
} from '../types'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

export async function fetchDashboard(filter?: PeriodFilter): Promise<DashboardKPI> {
  const { data } = await api.get('/analytics/dashboard', { params: filter })
  return data
}

export async function fetchSalesReport(filter?: PeriodFilter): Promise<SalesReport> {
  const { data } = await api.get('/analytics/sales', { params: filter })
  return data
}

export async function fetchCustomersReport(filter?: PeriodFilter): Promise<CustomerReport> {
  const { data } = await api.get('/analytics/customers', { params: filter })
  return data
}

export async function fetchProductsReport(filter?: PeriodFilter): Promise<ProductReport> {
  const { data } = await api.get('/analytics/products', { params: filter })
  return data
}

export async function fetchTrends(months?: number): Promise<TrendAnalysis> {
  const { data } = await api.get('/analytics/trends', { params: { months: months || 12 } })
  return data
}

export async function customQuery(query: string, params?: Record<string, unknown>) {
  const { data } = await api.post('/analytics/custom-query', { query, params })
  return data
}

export function getExportUrl(reportType: string, format: 'csv' | 'pdf', filter?: PeriodFilter): string {
  const params = new URLSearchParams()
  params.set('report_type', reportType)
  if (filter?.start_date) params.set('start_date', filter.start_date)
  if (filter?.end_date) params.set('end_date', filter.end_date)
  return `http://localhost:8000/export/${format}?${params.toString()}`
}

export default api
