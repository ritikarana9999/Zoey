'use client'

import { useState } from 'react'
import { BasketBuilder } from '@/components/basket/BasketBuilder'
import { BasketComparison } from '@/components/basket/BasketComparison'
import { basketApi } from '@/lib/api'
import type { BasketItem, BasketOptimizeResult } from '@/types'

export default function BasketPage() {
  const [items, setItems] = useState<BasketItem[]>([])
  const [result, setResult] = useState<BasketOptimizeResult | null>(null)
  const [optimizing, setOptimizing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleOptimize = async () => {
    if (items.length === 0) return
    setOptimizing(true)
    setError(null)
    try {
      const data = await basketApi.optimize(items)
      setResult(data)
    } catch (e: any) {
      setError('Failed to optimize basket. Please try again.')
    } finally {
      setOptimizing(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-white">Basket Optimizer</h2>
        <p className="text-slate-400 mt-1">
          Add your grocery items and find the cheapest store for your weekly shop
        </p>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-800/40 rounded-xl p-4 text-red-300 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Basket Builder */}
        <div className="lg:col-span-2">
          <BasketBuilder
            items={items}
            onItemsChange={setItems}
            onOptimize={handleOptimize}
            optimizing={optimizing}
          />
        </div>

        {/* Results */}
        <div className="lg:col-span-3">
          {result ? (
            <BasketComparison result={result} />
          ) : (
            <div className="bg-card border border-dashed border-slate-700 rounded-xl p-10 text-center">
              <p className="text-4xl mb-4">🛍️</p>
              <p className="text-slate-300 font-medium mb-2">Ready to optimize</p>
              <p className="text-sm text-slate-500">
                Add products to your basket, then click "Find Best Store" to see which supermarket saves you the most money.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* How it works */}
      <div className="bg-card border border-border rounded-xl p-5">
        <h3 className="text-sm font-semibold text-white mb-3">How the Basket Optimizer works</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { step: '1', title: 'Add items', desc: 'Search and add products from your regular shopping list.' },
            { step: '2', title: 'Compare stores', desc: 'SmartCart AI fetches current prices from all 3 stores.' },
            { step: '3', title: 'Save money', desc: 'See which store gives you the best total price for your basket.' },
          ].map((s) => (
            <div key={s.step} className="flex gap-3">
              <div className="w-7 h-7 rounded-full bg-indigo-600/20 text-indigo-400 text-xs font-bold flex items-center justify-center shrink-0">
                {s.step}
              </div>
              <div>
                <p className="text-sm text-white font-medium">{s.title}</p>
                <p className="text-xs text-slate-400 mt-0.5">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
