'use client'

import { useState } from 'react'
import { Plus, Minus, X, ShoppingCart } from 'lucide-react'
import { ProductSearch } from '@/components/products/ProductSearch'
import { formatCurrency } from '@/lib/utils'
import type { BasketItem, Product } from '@/types'

interface BasketBuilderProps {
  items: BasketItem[]
  onItemsChange: (items: BasketItem[]) => void
  onOptimize: () => void
  optimizing: boolean
}

export function BasketBuilder({ items, onItemsChange, onOptimize, optimizing }: BasketBuilderProps) {
  const handleAddProduct = (product: Product) => {
    const existing = items.find((i) => i.product_id === product.id)
    if (existing) {
      onItemsChange(
        items.map((i) =>
          i.product_id === product.id ? { ...i, quantity: i.quantity + 1 } : i
        )
      )
    } else {
      onItemsChange([
        ...items,
        {
          product_id: product.id,
          product_name: product.name,
          quantity: 1,
        },
      ])
    }
  }

  const updateQty = (productId: string, delta: number) => {
    onItemsChange(
      items
        .map((i) => i.product_id === productId ? { ...i, quantity: i.quantity + delta } : i)
        .filter((i) => i.quantity > 0)
    )
  }

  const remove = (productId: string) => {
    onItemsChange(items.filter((i) => i.product_id !== productId))
  }

  return (
    <div className="bg-card border border-border rounded-xl p-5 flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <ShoppingCart className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-semibold text-white">Build Your Basket</h3>
      </div>

      <ProductSearch
        onSelect={handleAddProduct}
        placeholder="Add products to your basket..."
        showResults={true}
      />

      {items.length > 0 ? (
        <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
          {items.map((item) => (
            <div
              key={item.product_id}
              className="flex items-center gap-3 bg-slate-800/60 rounded-lg px-3 py-2.5"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white truncate font-medium">{item.product_name}</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => updateQty(item.product_id, -1)}
                  className="w-6 h-6 rounded-md bg-slate-700 hover:bg-slate-600 flex items-center justify-center text-white transition-colors"
                >
                  <Minus className="w-3 h-3" />
                </button>
                <span className="text-sm text-white w-5 text-center font-medium">{item.quantity}</span>
                <button
                  onClick={() => updateQty(item.product_id, 1)}
                  className="w-6 h-6 rounded-md bg-slate-700 hover:bg-slate-600 flex items-center justify-center text-white transition-colors"
                >
                  <Plus className="w-3 h-3" />
                </button>
                <button
                  onClick={() => remove(item.product_id)}
                  className="w-6 h-6 rounded-md text-slate-500 hover:text-red-400 flex items-center justify-center transition-colors ml-1"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-6 border border-dashed border-slate-700 rounded-lg">
          <p className="text-2xl mb-2">🛒</p>
          <p className="text-sm text-slate-500">Search and add products above</p>
        </div>
      )}

      <button
        onClick={onOptimize}
        disabled={items.length === 0 || optimizing}
        className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {optimizing ? (
          <>
            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Optimizing...
          </>
        ) : (
          <>
            <ShoppingCart className="w-4 h-4" />
            Find Best Store ({items.length} item{items.length !== 1 ? 's' : ''})
          </>
        )}
      </button>
    </div>
  )
}
