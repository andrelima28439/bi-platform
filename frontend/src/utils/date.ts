import { format, subDays, subWeeks, subMonths, subYears, startOfDay, endOfDay } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export type PeriodKey = 'today' | 'week' | 'month' | 'year' | 'custom'

export function getPeriodDates(period: PeriodKey): { start: string; end: string } {
  const now = new Date()
  const end = endOfDay(now).toISOString()
  let start: Date

  switch (period) {
    case 'today':
      start = startOfDay(now)
      break
    case 'week':
      start = subWeeks(now, 1)
      break
    case 'month':
      start = subMonths(now, 1)
      break
    case 'year':
      start = subYears(now, 1)
      break
    default:
      start = subMonths(now, 1)
  }

  return {
    start: start.toISOString().split('T')[0],
    end: now.toISOString().split('T')[0],
  }
}

export function formatDateBR(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return format(d, "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
}

export function formatDateShort(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return format(d, 'dd/MM/yyyy')
}

export const periodOptions = [
  { value: 'today' as PeriodKey, label: 'Hoje' },
  { value: 'week' as PeriodKey, label: 'Últimos 7 dias' },
  { value: 'month' as PeriodKey, label: 'Último mês' },
  { value: 'year' as PeriodKey, label: 'Último ano' },
  { value: 'custom' as PeriodKey, label: 'Personalizado' },
]
