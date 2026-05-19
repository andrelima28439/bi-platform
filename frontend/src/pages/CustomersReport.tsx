import { useState } from 'react'
import PeriodFilter from '../components/PeriodFilter'
import ExportButton from '../components/ExportButton'
import { PieChartComponent, BarChartComponent } from '../components/Charts'
import DataTable from '../components/DataTable'
import { useApi } from '../hooks/useApi'
import { fetchCustomersReport } from '../services/api'
import { getPeriodDates, type PeriodKey } from '../utils/date'
import { formatCurrency } from '../utils/format'

export default function CustomersReport() {
  const [period, setPeriod] = useState<PeriodKey>('month')
  const dates = getPeriodDates(period)
  const filter = { period, ...dates }

  const { data, loading } = useApi(() => fetchCustomersReport(filter), [period])

  const summaryCards = data ? [
    { label: 'Total de Clientes', value: String(data.total_customers) },
    { label: 'Novos Clientes', value: String(data.new_customers) },
    { label: 'Taxa de Retenção', value: `${data.retention_rate}%` },
  ] : []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Relatório de Clientes</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Análise da base de clientes</p>
        </div>
        <div className="flex items-center gap-3">
          <ExportButton reportType="customers" filter={filter} />
          <PeriodFilter period={period} onPeriodChange={setPeriod} />
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <div key={i} className="card animate-pulse h-24" />)}
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
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Clientes por Tier</h3>
          {data?.customers_by_tier && (
            <PieChartComponent
              data={data.customers_by_tier.map((t) => ({ name: t.tier, value: t.count }))}
              height={280}
            />
          )}
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Clientes por Região</h3>
          {data?.customers_by_region && (
            <BarChartComponent
              data={data.customers_by_region}
              xKey="state"
              bars={[{ key: 'count', color: '#6366f1', name: 'Clientes' }]}
              height={280}
            />
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Top Clientes</h3>
        {data?.top_customers && (
          <DataTable
            columns={[
              { key: 'name', header: 'Nome', sortable: true },
              { key: 'email', header: 'Email', sortable: true },
              { key: 'tier', header: 'Tier', sortable: true },
              {
                key: 'total_purchases',
                header: 'Compras',
                sortable: true,
              },
              {
                key: 'total_spent',
                header: 'Total Gasto',
                sortable: true,
                render: (row: Record<string, unknown>) => formatCurrency(row.total_spent as number),
              },
            ]}
            data={data.top_customers as unknown as Record<string, unknown>[]}
            searchable
            searchKeys={['name', 'email']}
          />
        )}
      </div>
    </div>
  )
}
