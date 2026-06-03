'use client'

import { useEffect, useState } from 'react'
import { Package, Store, Tag, TrendingUp, ShoppingBag, AlertCircle } from 'lucide-react'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { PriceChart } from '@/components/dashboard/PriceChart'
import { CategoryInflation } from '@/components/dashboard/CategoryInflation'
import { TopMovers } from '@/components/dashboard/TopMovers'
import { analyticsApi, pricesApi } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'
import type { DashboardSummary, CategoryBreakdown, TopMover } from '@/types'

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [priceTrends, setPriceTrends] = useState<any[]>([])
  const [categoryData, setCategoryData] = useState<CategoryBreakdown[]>([])
  const [topMovers, setTopMovers] = useState<TopMover[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const [sum, trends, cats, movers] = await Promise.allSettled([
          analyticsApi.getSummary(),
          analyticsApi.getPriceTrends(30),
          analyticsApi.getCategoryBreakdown(),
          pricesApi.getTopMovers(20),
        ])

        if (sum.status === 'fulfilled') setSummary(sum.value)
        if (trends.status === 'fulfilled') setPriceTrends(trends.value)
        if (cats.status === 'fulfilled') setCategoryData(cats.value)
        if (movers.status === 'fulfilled') setTopMovers(movers.value)
      } catch (e: any) {
        setError('Failed to load dashboard data. Make sure the backend is running.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">Price Intelligence Dashboard</h2>
        <p className="text-slate-400 mt-1">Real-time grocery price tracking across Woolworths, Coles, and Aldi</p>
      </div>

      {error && (
        <div className="flex items-center gap-3 bg-red-900/20 border border-red-800/40 rounded-xl p-4 text-red-300 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Products"
          value={loading ? '—' : (summary?.total_products?.toLocaleString() ?? '—')}
          subtitle="tracked products"
          icon={<Package className="w-4 h-4" />}
          loading={loading}
        />
        <StatsCard
          title="Stores Tracked"
          value={loading ? '—' : (summary?.total_stores ?? '—')}
          subtitle="Woolworths, Coles, Aldi"
          icon={<Store className="w-4 h-4" />}
          loading={loading}
        />
        <StatsCard
          title="Items On Sale"
          value={loading ? '—' : (summary?.items_on_sale?.toLocaleString() ?? '—')}
          subtitle="active discounts"
          icon={<Tag className="w-4 h-4" />}
          valueClassName="text-green-400"
          loading={loading}
        />
        <StatsCard
          title="Basket Inflation"
          value={loading ? '—' : `${summary?.wow_inflation_pct != null ? (summary.wow_inflation_pct > 0 ? '+' : '') + summary.wow_inflation_pct.toFixed(1) + '%' : '—'}`}
          subtitle="week-over-week"
          icon={<TrendingUp className="w-4 h-4" />}
          trend={summary?.wow_inflation_pct}
          loading={loading}
        />
      </div>

      {/* Price Trend Chart */}
      <PriceChart
        data={priceTrends}
        title="30-Day Average Price Trend"
        loading={loading}
      />

      {/* Bottom Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CategoryInflation data={categoryData} loading={loading} />
        <TopMovers data={topMovers} loading={loading} />
      </div>

      {/* Price Alerts Banner */}
      <div className="bg-gradient-to-r from-indigo-900/40 to-purple-900/40 border border-indigo-800/40 rounded-xl p-5">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 bg-indigo-600/20 rounded-lg flex items-center justify-center shrink-0">
            <ShoppingBag className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white mb-1">Optimize Your Shopping</h3>
            <p className="text-sm text-slate-400 mb-3">
              Add products to your basket and SmartCart AI will find the cheapest store combination for your weekly shop.
            </p>
            <a
              href="/basket"
              className="inline-flex items-center gap-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors font-medium"
            >
              Build Your Basket
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
