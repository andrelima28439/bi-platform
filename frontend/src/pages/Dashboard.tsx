import { useState } from 'react'
import { DollarSign, ShoppingCart, Users, TrendingUp } from 'lucide-react'
import KPICard from '../components/KPICard'
import PeriodFilter from '../components/PeriodFilter'
import ExportButton from '../components/ExportButton'
import { LineChartComponent, BarChartComponent } from '../components/Charts'
import { useApi } from '../hooks/useApi'
import { fetchDashboard, fetchSalesReport } from '../services/api'
import { getPeriodDates, type PeriodKey } from '../utils/date'

export default function Dashboard() {
  const [period, setPeriod] = useState<PeriodKey>('month')
  const dates = getPeriodDates(period)
  const filter = { period, ...dates }

  const { data: kpi, loading: kpiLoading } = useApi(() => fetchDashboard(filter), [period])
  const { data: sales } = useApi(() => fetchSalesReport(filter), [period])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Dashboard</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Visão geral dos indicadores de performance</p>
        </div>
        <div className="flex items-center gap-3">
          <ExportButton reportType="dashboard" filter={filter} />
          <PeriodFilter period={period} onPeriodChange={setPeriod} />
        </div>
      </div>

      {kpiLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-24 mb-3" />
              <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded w-32 mb-2" />
              <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-28" />
            </div>
          ))}
        </div>
      ) : kpi ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <KPICard title="Receita Total" value={kpi.total_revenue} growth={kpi.revenue_growth} format="currency" icon={<DollarSign className="w-5 h-5" />} />
          <KPICard title="Pedidos" value={kpi.total_orders} growth={kpi.orders_growth} icon={<ShoppingCart className="w-5 h-5" />} />
          <KPICard title="Clientes Ativos" value={kpi.active_customers} growth={kpi.customers_growth} icon={<Users className="w-5 h-5" />} />
          <KPICard title="Ticket Médio" value={kpi.avg_order_value} growth={kpi.aov_growth} format="currency" icon={<DollarSign className="w-5 h-5" />} />
          <KPICard title="Taxa Conversão" value={kpi.conversion_rate} growth={kpi.conversion_growth} format="percent" icon={<TrendingUp className="w-5 h-5" />} />
        </div>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Vendas por Dia</h3>
          {sales?.sales_by_day && (
            <LineChartComponent
              data={sales.sales_by_day}
              xKey="date"
              lines={[{ key: 'amount', color: '#6366f1', name: 'Receita' }]}
              height={280}
            />
          )}
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Vendas por Categoria</h3>
          {sales?.sales_by_category && (
            <BarChartComponent
              data={sales.sales_by_category}
              xKey="category"
              bars={[{ key: 'total', color: '#8b5cf6', name: 'Receita' }]}
              height={280}
            />
          )}
        </div>
      </div>
    </div>
  )
}
