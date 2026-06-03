'use client'

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { formatPct, getInflationColor } from '@/lib/utils'
import type { CategoryBreakdown } from '@/types'

interface CategoryInflationProps {
  data: CategoryBreakdown[]
  loading?: boolean
}

const CATEGORY_ICONS: Record<string, string> = {
  dairy: '🥛',
  bakery: '🍞',
  produce: '🥬',
  meat: '🥩',
  pantry: '🥫',
  beverages: '🥤',
  frozen: '🧊',
  snacks: '🍿',
}

export function CategoryInflation({ data, loading = false }: CategoryInflationProps) {
  if (loading) {
    return (
      <div className="bg-card border border-border rounded-xl p-5">
        <div className="skeleton h-5 w-40 mb-4" />
        <div className="space-y-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="flex items-center justify-between">
              <div className="skeleton h-4 w-28" />
              <div className="skeleton h-4 w-16" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <h3 className="text-sm font-semibold text-white mb-4">Category Inflation (MoM)</h3>
      <div className="space-y-3">
        {data.map((cat) => {
          const pct = cat.mom_change_pct
          const colorClass = getInflationColor(pct)
          const icon = CATEGORY_ICONS[cat.slug] || '📦'

          return (
            <div key={cat.category_id} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-base">{icon}</span>
                <span className="text-sm text-slate-300">{cat.category}</span>
              </div>
              <div className={`flex items-center gap-1 text-xs font-semibold ${colorClass}`}>
                {pct != null && pct > 0.5 && <TrendingUp className="w-3 h-3" />}
                {pct != null && pct < -0.5 && <TrendingDown className="w-3 h-3" />}
                {(pct == null || Math.abs(pct) <= 0.5) && <Minus className="w-3 h-3" />}
                <span>{formatPct(pct)}</span>
              </div>
            </div>
          )
        })}
        {data.length === 0 && (
          <p className="text-sm text-slate-500 text-center py-4">No category data available</p>
        )}
      </div>
    </div>
  )
}
