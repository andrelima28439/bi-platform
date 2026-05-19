import { TrendingUp, TrendingDown } from 'lucide-react'
import { formatCurrency, formatNumber, formatPercent } from '../utils/format'

interface KPICardProps {
  title: string
  value: number
  growth: number
  prefix?: string
  format?: 'currency' | 'number' | 'percent'
  icon?: React.ReactNode
}

export default function KPICard({ title, value, growth, format: fmt = 'number', icon }: KPICardProps) {
  const formattedValue = fmt === 'currency' ? formatCurrency(value) : fmt === 'percent' ? `${value.toFixed(2)}%` : formatNumber(value)
  const isPositive = growth >= 0

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</span>
        {icon && <span className="text-primary-500">{icon}</span>}
      </div>
      <div className="text-2xl font-bold text-slate-900 dark:text-white mb-1">{formattedValue}</div>
      <div className={`flex items-center gap-1 text-sm ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
        {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
        <span>{formatPercent(growth)}</span>
        <span className="text-slate-400 dark:text-slate-500 ml-1">vs período anterior</span>
      </div>
    </div>
  )
}
