'use client'

import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { formatCurrency, getStoreColor } from '@/lib/utils'
import type { ForecastSeries } from '@/types'

interface ForecastChartProps {
  series: ForecastSeries
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-card border border-border rounded-lg p-3 shadow-xl text-sm">
        <p className="text-slate-400 text-xs mb-2">{label}</p>
        {payload.map((entry: any) => (
          <div key={entry.name} className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-slate-300 capitalize">{entry.name}:</span>
            <span className="text-white font-medium">{formatCurrency(entry.value)}</span>
          </div>
        ))}
      </div>
    )
  }
  return null
}

export function ForecastChart({ series }: ForecastChartProps) {
  const color = getStoreColor(series.store_name?.toLowerCase() || '')

  const chartData = series.forecast.map((p) => ({
    date: new Date(p.date).toLocaleDateString('en-AU', { month: 'short', day: 'numeric' }),
    predicted: p.predicted_price,
    lower: p.lower_bound,
    upper: p.upper_bound,
    band: p.lower_bound != null && p.upper_bound != null
      ? [p.lower_bound, p.upper_bound]
      : undefined,
  }))

  const TrendIcon = series.trend === 'up' ? TrendingUp : series.trend === 'down' ? TrendingDown : Minus
  const trendColor = series.trend === 'up' ? 'text-red-400' : series.trend === 'down' ? 'text-green-400' : 'text-slate-400'

  return (
    <div className="bg-card border border-border rounded-xl p-5">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            <h3 className="text-sm font-semibold text-white">{series.store_name}</h3>
          </div>
          {series.current_price != null && (
            <p className="text-xs text-slate-400 mt-0.5">
              Current: <span className="text-white font-medium">{formatCurrency(series.current_price)}</span>
            </p>
          )}
        </div>
        <div className="text-right">
          <div className={`flex items-center gap-1 text-xs font-medium ${trendColor}`}>
            <TrendIcon className="w-3.5 h-3.5" />
            <span>
              {series.predicted_change_pct > 0 ? '+' : ''}{series.predicted_change_pct.toFixed(1)}% over 30 days
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">{series.model_name}</p>
        </div>
      </div>

      {/* Recommendation badge */}
      <div className={`inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full mb-4 font-medium ${
        series.trend === 'down'
          ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
          : series.trend === 'up'
          ? 'bg-red-500/10 text-red-400 border border-red-500/20'
          : 'bg-slate-700 text-slate-300 border border-slate-600'
      }`}>
        {series.recommendation}
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#64748b', fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: '#64748b', fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => `$${v.toFixed(2)}`}
            width={55}
          />
          <Tooltip content={<CustomTooltip />} />
          {/* Confidence band */}
          <Area
            dataKey="band"
            fill={color}
            fillOpacity={0.08}
            stroke="none"
          />
          <Line
            type="monotone"
            dataKey="predicted"
            name="Predicted"
            stroke={color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
            strokeDasharray="5 3"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
