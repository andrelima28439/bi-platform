import { useState } from 'react'
import ExportButton from '../components/ExportButton'
import { LineChartComponent, BarChartComponent } from '../components/Charts'
import { useApi } from '../hooks/useApi'
import { fetchTrends } from '../services/api'
import { formatCurrency } from '../utils/format'

export default function TrendsAnalysis() {
  const [months, setMonths] = useState(12)
  const { data, loading } = useApi(() => fetchTrends(months), [months])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Análise de Tendências</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Padrões sazonais e projeções futuras</p>
        </div>
        <div className="flex items-center gap-3">
          <ExportButton reportType="trends" />
          <select
            value={months}
            onChange={(e) => setMonths(Number(e.target.value))}
            className="input-field text-sm w-32"
          >
            <option value={3}>3 meses</option>
            <option value={6}>6 meses</option>
            <option value={12}>12 meses</option>
            <option value={24}>24 meses</option>
            <option value={36}>36 meses</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="space-y-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card animate-pulse h-64" />
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card lg:col-span-2">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Tendência de Receita</h3>
              {data?.revenue_trend && (
                <LineChartComponent
                  data={data.revenue_trend}
                  xKey="month"
                  lines={[
                    { key: 'revenue', color: '#6366f1', name: 'Receita' },
                    { key: 'orders', color: '#10b981', name: 'Pedidos' },
                  ]}
                  height={350}
                />
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Crescimento de Clientes</h3>
              {data?.customer_growth_trend && (
                <BarChartComponent
                  data={data.customer_growth_trend}
                  xKey="month"
                  bars={[{ key: 'new', color: '#8b5cf6', name: 'Novos Clientes' }]}
                  height={300}
                />
              )}
            </div>
            <div className="card">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Padrão Sazonal</h3>
              {data?.seasonal_patterns && (
                <LineChartComponent
                  data={data.seasonal_patterns.map((s) => ({
                    month: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][s.month - 1],
                    avg_revenue: s.avg_revenue,
                  }))}
                  xKey="month"
                  lines={[{ key: 'avg_revenue', color: '#f59e0b', name: 'Receita Média' }]}
                  height={300}
                />
              )}
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Projeção de Receita (Próximos 6 Meses)</h3>
            {data?.forecast && data.forecast.length > 0 && (
              <div className="grid grid-cols-6 gap-4">
                {data.forecast.map((f) => (
                  <div key={f.period} className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4 text-center">
                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">{f.period.replace('_', ' ')}</p>
                    <p className="text-lg font-bold text-primary-600 dark:text-primary-400">
                      {formatCurrency(f.predicted_revenue)}
                    </p>
                  </div>
                ))}
              </div>
            )}
            {(!data?.forecast || data.forecast.length === 0) && (
              <p className="text-slate-400 text-center py-8">Dados insuficientes para gerar projeções</p>
            )}
          </div>
        </>
      )}
    </div>
  )
}
