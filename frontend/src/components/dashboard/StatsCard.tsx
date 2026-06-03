'use client'

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: ReactNode
  trend?: number | null
  trendLabel?: string
  className?: string
  valueClassName?: string
  loading?: boolean
}

export function StatsCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendLabel,
  className,
  valueClassName,
  loading = false,
}: StatsCardProps) {
  const trendPositive = trend !== null && trend !== undefined && trend > 0
  const trendNegative = trend !== null && trend !== undefined && trend < 0

  return (
    <div className={cn(
      'bg-card border border-border rounded-xl p-5 flex flex-col gap-3 hover:border-slate-600 transition-all duration-200',
      className
    )}>
      <div className="flex items-start justify-between">
        <p className="text-sm text-slate-400 font-medium">{title}</p>
        {icon && (
          <div className="w-9 h-9 bg-slate-800 rounded-lg flex items-center justify-center text-slate-400">
            {icon}
          </div>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">
          <div className="skeleton h-8 w-28" />
          <div className="skeleton h-4 w-20" />
        </div>
      ) : (
        <>
          <div>
            <p className={cn('text-2xl font-bold text-white', valueClassName)}>
              {value}
            </p>
            {subtitle && (
              <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>
            )}
          </div>

          {trend !== null && trend !== undefined && (
            <div className={cn(
              'flex items-center gap-1 text-xs font-medium',
              trendPositive && 'text-red-400',
              trendNegative && 'text-green-400',
              !trendPositive && !trendNegative && 'text-slate-400',
            )}>
              {trendPositive && <TrendingUp className="w-3 h-3" />}
              {trendNegative && <TrendingDown className="w-3 h-3" />}
              {!trendPositive && !trendNegative && <Minus className="w-3 h-3" />}
              <span>{trend > 0 ? '+' : ''}{trend.toFixed(1)}% {trendLabel || 'vs last week'}</span>
            </div>
          )}
        </>
      )}
    </div>
  )
}
