'use client'

import Link from 'next/link'
import { Tag, Store } from 'lucide-react'
import { formatCurrency, getStoreColor } from '@/lib/utils'
import type { Product } from '@/types'

interface ProductCardProps {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
  const hasMultiplePrices = product.store_prices && product.store_prices.length > 1

  return (
    <Link href={`/products/${product.id}`}>
      <div className="bg-card border border-border rounded-xl p-4 hover:border-indigo-600/50 hover:bg-slate-800/50 transition-all duration-200 cursor-pointer group h-full flex flex-col">
        {/* Image placeholder */}
        <div className="w-full h-28 bg-slate-800 rounded-lg mb-3 flex items-center justify-center overflow-hidden">
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-contain p-2"
            />
          ) : (
            <span className="text-4xl">🛒</span>
          )}
        </div>

        <div className="flex-1 flex flex-col">
          <p className="text-xs text-indigo-400 font-medium mb-1">{product.category_name}</p>
          <h3 className="text-sm font-semibold text-white leading-tight mb-1 group-hover:text-indigo-300 transition-colors line-clamp-2">
            {product.name}
          </h3>
          {product.brand && (
            <p className="text-xs text-slate-500 mb-2">{product.brand}</p>
          )}
          {product.weight_volume && (
            <p className="text-xs text-slate-600 mb-2">{product.weight_volume}</p>
          )}

          <div className="mt-auto">
            {product.min_price != null ? (
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-lg font-bold text-white">
                    {formatCurrency(product.min_price)}
                  </p>
                  {hasMultiplePrices && product.max_price && product.max_price !== product.min_price && (
                    <p className="text-xs text-slate-500">
                      up to {formatCurrency(product.max_price)}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-1 text-xs text-slate-500">
                  <Store className="w-3 h-3" />
                  <span>{product.store_count || 1} store{(product.store_count || 1) > 1 ? 's' : ''}</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-500">Price unavailable</p>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}
