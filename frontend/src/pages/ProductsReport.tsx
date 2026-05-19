import { useState } from 'react'
import PeriodFilter from '../components/PeriodFilter'
import ExportButton from '../components/ExportButton'
import { BarChartComponent, PieChartComponent } from '../components/Charts'
import DataTable from '../components/DataTable'
import { useApi } from '../hooks/useApi'
import { fetchProductsReport } from '../services/api'
import { getPeriodDates, type PeriodKey } from '../utils/date'
import { formatCurrency } from '../utils/format'

export default function ProductsReport() {
  const [period, setPeriod] = useState<PeriodKey>('month')
  const dates = getPeriodDates(period)
  const filter = { period, ...dates }

  const { data, loading } = useApi(() => fetchProductsReport(filter), [period])

  const summaryCards = data ? [
    { label: 'Total de Produtos', value: String(data.total_products) },
    { label: 'Com Baixo Estoque', value: String(data.low_stock_products.length) },
  ] : []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Relatório de Produtos</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Análise de performance de produtos</p>
        </div>
        <div className="flex items-center gap-3">
          <ExportButton reportType="products" filter={filter} />
          <PeriodFilter period={period} onPeriodChange={setPeriod} />
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 gap-4">
          {[...Array(2)].map((_, i) => <div key={i} className="card animate-pulse h-24" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
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
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Top Produtos por Receita</h3>
          {data?.top_selling && (
            <BarChartComponent
              data={data.top_selling.slice(0, 10)}
              xKey="name"
              bars={[{ key: 'revenue', color: '#6366f1', name: 'Receita' }]}
              height={300}
            />
          )}
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Produtos por Categoria</h3>
          {data?.products_by_category && (
            <PieChartComponent
              data={data.products_by_category.map((c) => ({ name: c.category, value: c.count }))}
              height={300}
            />
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Top Produtos Vendidos</h3>
        {data?.top_selling && (
          <DataTable
            columns={[
              { key: 'name', header: 'Produto', sortable: true },
              { key: 'sku', header: 'SKU', sortable: true },
              { key: 'category', header: 'Categoria', sortable: true },
              { key: 'quantity_sold', header: 'Vendidos', sortable: true },
              {
                key: 'revenue',
                header: 'Receita',
                sortable: true,
                render: (row: Record<string, unknown>) => formatCurrency(row.revenue as number),
              },
              { key: 'stock', header: 'Estoque', sortable: true },
            ]}
            data={data.top_selling as unknown as Record<string, unknown>[]}
            searchable
            searchKeys={['name', 'sku', 'category']}
          />
        )}
      </div>

      {data?.low_stock_products && data.low_stock_products.length > 0 && (
        <div className="card border-red-200 dark:border-red-800">
          <h3 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-4">
            Alerta de Estoque Baixo ({data.low_stock_products.length})
          </h3>
          <DataTable
            columns={[
              { key: 'name', header: 'Produto', sortable: true },
              { key: 'sku', header: 'SKU' },
              { key: 'category', header: 'Categoria', sortable: true },
              { key: 'stock', header: 'Estoque Atual', sortable: true },
            ]}
            data={data.low_stock_products as unknown as Record<string, unknown>[]}
          />
        </div>
      )}
    </div>
  )
}
