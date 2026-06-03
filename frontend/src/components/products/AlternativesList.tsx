'use client'

import { formatCurrency } from '@/lib/utils'

interface Alternative {
  recommended_id: string
  recommended_name: string
  recommended_brand?: string
  weight_volume?: string
  avg_price?: number
  savings?: number
  reason?: string
}

interface AlternativesListProps {
  alternatives: Alternative[]
  loading?: boolean
}

export function AlternativesList({ alternatives, loading = false }: AlternativesListProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="skeleton h-16 rounded-lg" />
        ))}
      </div>
    )
  }

  if (alternatives.length === 0) {
    return <p className="text-sm text-slate-500 py-4">No cheaper alternatives found in this category.</p>
  }

  return (
    <div className="space-y-3">
      {alternatives.map((alt, idx) => (
        <div
          key={alt.recommended_id || idx}
          className="flex items-center justify-between bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-3 hover:border-green-600/40 transition-all"
        >
          <div className="flex-1 min-w-0 pr-4">
            <p className="text-sm text-white font-medium truncate">{alt.recommended_name}</p>
            <p className="text-xs text-slate-400">
              {alt.recommended_brand ? alt.recommended_brand : ''}
              {alt.weight_volume ? ` · ${alt.weight_volume}` : ''}
            </p>
            {alt.reason && <p className="text-xs text-slate-500 mt-0.5">{alt.reason}</p>}
          </div>
          <div className="shrink-0 text-right">
            {alt.avg_price != null && (
              <p className="text-sm font-bold text-white">{formatCurrency(alt.avg_price)}</p>
            )}
            {alt.savings != null && alt.savings > 0 && (
              <p className="text-xs text-green-400 font-medium">
                Save {formatCurrency(alt.savings)}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
