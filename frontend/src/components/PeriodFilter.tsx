import { periodOptions, type PeriodKey } from '../utils/date'

interface PeriodFilterProps {
  period: PeriodKey
  onPeriodChange: (period: PeriodKey) => void
  startDate?: string
  endDate?: string
  onStartDateChange?: (date: string) => void
  onEndDateChange?: (date: string) => void
}

export default function PeriodFilter({
  period,
  onPeriodChange,
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
}: PeriodFilterProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="flex rounded-lg border border-slate-300 dark:border-slate-600 overflow-hidden">
        {periodOptions.map((opt) => (
          <button
            key={opt.value}
            onClick={() => onPeriodChange(opt.value)}
            className={`px-3 py-2 text-sm font-medium transition-colors ${
              period === opt.value
                ? 'bg-primary-600 text-white'
                : 'bg-white dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-600'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
      {period === 'custom' && (
        <div className="flex items-center gap-2">
          <input
            type="date"
            value={startDate || ''}
            onChange={(e) => onStartDateChange?.(e.target.value)}
            className="input-field text-sm w-40"
          />
          <span className="text-slate-400">até</span>
          <input
            type="date"
            value={endDate || ''}
            onChange={(e) => onEndDateChange?.(e.target.value)}
            className="input-field text-sm w-40"
          />
        </div>
      )}
    </div>
  )
}
