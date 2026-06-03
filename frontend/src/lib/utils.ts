import { clsx, type ClassValue } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatCurrency(amount: number | null | undefined): string {
  if (amount == null) return 'N/A'
  return new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

export function formatPct(value: number | null | undefined, decimals = 1): string {
  if (value == null) return 'N/A'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(decimals)}%`
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return 'N/A'
  try {
    return new Date(dateStr).toLocaleDateString('en-AU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    })
  } catch {
    return dateStr
  }
}

export function getStoreColor(slug: string): string {
  const colors: Record<string, string> = {
    woolworths: '#00aa46',
    coles: '#e41b17',
    aldi: '#00609c',
  }
  return colors[slug] || '#6366f1'
}

export function getSignalColor(signal: string): string {
  switch (signal) {
    case 'BUY NOW':
      return 'text-green-400 bg-green-400/10'
    case 'GOOD PRICE':
      return 'text-emerald-400 bg-emerald-400/10'
    case 'WAIT':
      return 'text-yellow-400 bg-yellow-400/10'
    default:
      return 'text-gray-400 bg-gray-400/10'
  }
}

export function getTrendColor(trend: string): string {
  switch (trend) {
    case 'up':
      return 'text-red-400'
    case 'down':
      return 'text-green-400'
    default:
      return 'text-gray-400'
  }
}

export function getInflationColor(pct: number | null | undefined): string {
  if (pct == null) return 'text-gray-400'
  if (pct > 3) return 'text-red-400'
  if (pct > 0) return 'text-orange-400'
  if (pct < -1) return 'text-green-400'
  return 'text-gray-400'
}

export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str
  return str.slice(0, maxLength) + '…'
}

export function generateChartColors(count: number): string[] {
  const base = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316']
  return Array.from({ length: count }, (_, i) => base[i % base.length])
}
