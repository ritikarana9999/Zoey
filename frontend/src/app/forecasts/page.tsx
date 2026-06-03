'use client'

import { useState } from 'react'
import { Search, TrendingUp } from 'lucide-react'
import { ForecastChart } from '@/components/forecasts/ForecastChart'
import { ProductSearch } from '@/components/products/ProductSearch'
import { forecastsApi } from '@/lib/api'
import type { Product, ForecastSeries } from '@/types'

export default function ForecastsPage() {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [forecasts, setForecasts] = useState<ForecastSeries[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleProductSelect = async (product: Product) => {
    setSelectedProduct(product)
    setLoading(true)
    setError(null)
    try {
      const data = await forecastsApi.getForProduct(product.id)
      setForecasts(Array.isArray(data) ? data : [])
    } catch (e) {
      setError('Failed to load forecast. The product may not have enough price history.')
      setForecasts([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-white">Price Forecasts</h2>
        <p className="text-slate-400 mt-1">30-day price predictions powered by XGBoost machine learning</p>
      </div>

      {/* Search */}
      <div className="max-w-lg">
        <ProductSearch
          onSelect={handleProductSelect}
          placeholder="Search a product to see its price forecast..."
        />
      </div>

      {/* Info cards */}
      {!selectedProduct && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { icon: '🤖', title: 'XGBoost ML', desc: 'Trained on 180 days of price history with seasonal features' },
            { icon: '📅', title: '30-Day Horizon', desc: 'See predicted prices for the next 30 days with confidence intervals' },
            { icon: '💡', title: 'Buy Signal', desc: 'Get "Buy now" or "Wait" recommendations based on trend direction' },
          ].map((card) => (
            <div key={card.title} className="bg-card border border-border rounded-xl p-4">
              <span className="text-2xl">{card.icon}</span>
              <h3 className="text-sm font-semibold text-white mt-2 mb-1">{card.title}</h3>
              <p className="text-xs text-slate-400">{card.desc}</p>
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="bg-orange-900/20 border border-orange-800/40 rounded-xl p-4 text-orange-300 text-sm">
          {error}
        </div>
      )}

      {loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton h-72 rounded-xl" />
          ))}
        </div>
      )}

      {!loading && selectedProduct && forecasts.length > 0 && (
        <>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-semibold text-white">{selectedProduct.name}</h3>
            <span className="text-sm text-slate-400">— Price forecast per store</span>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {forecasts.map((series, i) => (
              <ForecastChart key={i} series={series} />
            ))}
          </div>
        </>
      )}

      {!loading && selectedProduct && forecasts.length === 0 && !error && (
        <div className="text-center py-16 bg-card border border-border rounded-xl">
          <p className="text-3xl mb-3">📊</p>
          <p className="text-slate-300 font-medium mb-1">No forecast available</p>
          <p className="text-sm text-slate-500">
            This product doesn&apos;t have enough price history to generate a forecast yet.
          </p>
        </div>
      )}
    </div>
  )
}
