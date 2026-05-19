import { useState } from 'react'
import PeriodFilter from '../components/PeriodFilter'
import ExportButton from '../components/ExportButton'
import { LineChartComponent, BarChartComponent, PieChartComponent } from '../components/Charts'
import DataTable from '../components/DataTable'
import { useApi } from '../hooks/useApi'
import { fetchSalesReport } from '../services/api'
import { getPeriodDates, type PeriodKey } from '../utils/date'
import { formatCurrency } from '../utils/format'

export default function SalesReport() {
  const [period, setPeriod] = useState<PeriodKey>('month')
  const dates = getPeriodDates(period)
  const filter = { period, ...dates }

  const { data, loading } = useApi(() => fetchSalesReport(filter), [period])

  const summaryCards = data ? [
    { label: 'Total de Vendas', value: formatCurrency(data.total_sales) },
    { label: 'Total de Pedidos', value: String(data.total_orders) },
    { label: 'Ticket Médio', value: formatCurrency(data.total_sales / data.total_orders) },
  ] : []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Relatório de Vendas</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Análise detalhada de vendas e faturamento</p>
        </div>
        <div className="flex items-center gap-3">
          <ExportButton reportType="sales" filter={filter} />
          <PeriodFilter period={period} onPeriodChange={setPeriod} />
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card animate-pulse h-24" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {summaryCards.map((card) => (
            <div key={card.label} className="card">
              <p className="text-sm text-slate-500 dark:text-slate-400">{card.label}</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{card.value}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Vendas ao Longo do Tempo</h3>
          {data?.sales_by_day && (
            <LineChartComponent
              data={data.sales_by_day}
              xKey="date"
              lines={[{ key: 'amount', color: '#6366f1', name: 'Receita' }]}
              height={300}
            />
          )}
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Vendas por Categoria</h3>
          {data?.sales_by_category && (
            <PieChartComponent
              data={data.sales_by_category.map((c) => ({ name: c.category, value: c.total }))}
              height={300}
            />
          )}
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Método de Pagamento</h3>
          {data?.sales_by_payment_method && (
            <PieChartComponent
              data={data.sales_by_payment_method.map((p) => ({ name: p.payment, value: p.amount }))}
              height={300}
            />
          )}
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Top Produtos</h3>
          {data?.top_products && (
            <BarChartComponent
              data={data.top_products}
              xKey="name"
              bars={[
                { key: 'revenue', color: '#6366f1', name: 'Receita' },
                { key: 'quantity', color: '#10b981', name: 'Quantidade' },
              ]}
              height={300}
            />
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Top Produtos - Detalhado</h3>
        {data?.top_products && (
          <DataTable
            columns={[
              { key: 'name', header: 'Produto', sortable: true },
              { key: 'quantity', header: 'Quantidade', sortable: true },
              {
                key: 'revenue',
                header: 'Receita',
                sortable: true,
                render: (row: Record<string, unknown>) => formatCurrency(row.revenue as number),
              },
            ]}
            data={data.top_products as unknown as Record<string, unknown>[]}
            pageSize={5}
            searchable
            searchKeys={['name']}
          />
        )}
      </div>
    </div>
  )
}
