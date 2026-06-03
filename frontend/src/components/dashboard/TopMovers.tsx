'use client'

import { TrendingUp, TrendingDown } from 'lucide-react'
import { formatCurrency, formatPct } from '@/lib/utils'
import type { TopMover } from '@/types'

interface TopMoversProps {
  data: TopMover[]
  loading?: boolean
}

export function TopMovers({ data, loading = false }: TopMoversProps) {
  if (loading) {
    return (
      <div className="bg-card border border-border rounded-xl p-5">
        <div className="skeleton h-5 w-36 mb-4" />
        <div className="space-y-3">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="flex items-center justify-between">
              <div className="space-y-1">
                <div className="skeleton h-4 w-40" />
                <div className="skeleton h-3 w-20" />
              </div>
              <div className="skeleton h-5 w-16" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <h3 className="text-sm font-semibold text-white mb-4">Top Price Movers (7 days)</h3>
      <div className="space-y-2">
        {data.slice(0, 10).map((mover, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between py-2 border-t border-slate-800 first:border-0"
          >
            <div className="flex-1 min-w-0 pr-4">
              <p className="text-sm text-slate-200 truncate font-medium">{mover.product_name}</p>
              <p className="text-xs text-slate-500">{mover.category} · {mover.store_name}</p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-sm text-slate-300">{formatCurrency(mover.current_price)}</span>
              <span className={`flex items-center gap-0.5 text-xs font-semibold px-2 py-0.5 rounded-full ${
                mover.direction === 'up'
                  ? 'text-red-400 bg-red-400/10'
                  : 'text-green-400 bg-green-400/10'
              }`}>
                {mover.direction === 'up'
                  ? <TrendingUp className="w-3 h-3" />
                  : <TrendingDown className="w-3 h-3" />
                }
                {formatPct(mover.pct_change)}
              </span>
            </div>
          </div>
        ))}
        {data.length === 0 && (
          <p className="text-sm text-slate-500 text-center py-4">No price movements found</p>
        )}
      </div>
    </div>
  )
}
