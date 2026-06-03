'use client'

import { CheckCircle, XCircle, TrendingDown } from 'lucide-react'
import { formatCurrency, formatPct, getStoreColor } from '@/lib/utils'
import type { BasketOptimizeResult, StoreBasketTotal } from '@/types'

interface BasketComparisonProps {
  result: BasketOptimizeResult
}

function StoreCard({ store, isBest }: { store: StoreBasketTotal; isBest: boolean }) {
  const color = getStoreColor(store.store_slug)

  return (
    <div className={`bg-slate-800/60 border rounded-xl p-4 transition-all ${
      isBest ? 'border-green-500/50 ring-1 ring-green-500/20' : 'border-slate-700'
    }`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: color }}
          />
          <span className="text-sm font-semibold text-white capitalize">{store.store_name}</span>
          {isBest && (
            <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full font-medium">
              Best
            </span>
          )}
        </div>
        <span className="text-lg font-bold text-white">{formatCurrency(store.total)}</span>
      </div>

      <div className="text-xs text-slate-400 mb-3">
        {store.items_found} of {store.items_found + store.items_missing.length} items found
        {store.items_missing.length > 0 && (
          <span className="text-orange-400 ml-1">({store.items_missing.length} missing)</span>
        )}
      </div>

      {store.breakdown.length > 0 && (
        <div className="space-y-1 border-t border-slate-700 pt-3">
          {store.breakdown.map((item, i) => (
            <div key={i} className="flex items-center justify-between text-xs">
              <span className="text-slate-400 truncate pr-2">
                {item.product}
                {item.qty > 1 ? ` ×${item.qty}` : ''}
                {item.is_on_sale && <span className="text-green-400 ml-1">SALE</span>}
              </span>
              <span className="text-slate-300 shrink-0">{formatCurrency(item.line_total)}</span>
            </div>
          ))}
        </div>
      )}

      {store.items_missing.length > 0 && (
        <div className="mt-2 pt-2 border-t border-slate-700">
          {store.items_missing.map((item, i) => (
            <div key={i} className="flex items-center gap-1 text-xs text-slate-500">
              <XCircle className="w-3 h-3 text-slate-600" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function BasketComparison({ result }: BasketComparisonProps) {
  const bestSlug = result.best_single_store?.store_slug

  return (
    <div className="space-y-5">
      {/* Savings banner */}
      {result.potential_savings > 0 && (
        <div className="flex items-center gap-3 bg-green-900/20 border border-green-800/40 rounded-xl p-4">
          <TrendingDown className="w-5 h-5 text-green-400 shrink-0" />
          <div>
            <p className="text-sm font-semibold text-green-300">
              Save {formatCurrency(result.potential_savings)} ({result.savings_pct.toFixed(1)}%)
            </p>
            <p className="text-xs text-green-500/80">{result.recommendation}</p>
          </div>
        </div>
      )}

      {/* Store cards */}
      <div className="grid grid-cols-1 gap-4">
        {result.all_stores?.map((store) => (
          <StoreCard
            key={store.store_slug}
            store={store}
            isBest={store.store_slug === bestSlug}
          />
        ))}
      </div>
    </div>
  )
}
