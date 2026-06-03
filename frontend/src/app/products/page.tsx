'use client'

import { useEffect, useState } from 'react'
import { Search, Plus } from 'lucide-react'
import { ProductCard } from '@/components/products/ProductCard'
import { AddProductModal } from '@/components/products/AddProductModal'
import { productsApi } from '@/lib/api'
import type { Product, Category } from '@/types'

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [showAdd, setShowAdd] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    productsApi.getCategories().then(setCategories).catch(() => {})
  }, [])

  useEffect(() => {
    async function loadProducts() {
      setLoading(true)
      try {
        const data = await productsApi.list({
          search: search || undefined,
          category: selectedCategory || undefined,
          limit: 100,
        })
        setProducts(data)
      } catch {
        setProducts([])
      } finally {
        setLoading(false)
      }
    }
    const timer = setTimeout(loadProducts, 300)
    return () => clearTimeout(timer)
  }, [search, selectedCategory, refreshKey])

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Products</h2>
          <p className="text-slate-400 mt-1">{products.length} products tracked across 3 stores</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add Product
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            className="input pl-10"
            placeholder="Search products by name or brand..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          className="input sm:w-48"
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.slug}>{cat.name}</option>
          ))}
        </select>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedCategory('')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
            !selectedCategory
              ? 'bg-indigo-600 text-white'
              : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
          }`}
        >
          All
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.slug)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
              selectedCategory === cat.slug
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            {cat.name}
            {cat.product_count ? ` (${cat.product_count})` : ''}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {[...Array(20)].map((_, i) => (
            <div key={i} className="skeleton h-64 rounded-xl" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-5xl mb-4">🛒</p>
          <p className="text-xl font-semibold text-white mb-2">No products yet</p>
          <p className="text-slate-400 mb-6">Start by adding a grocery product to track its price across stores.</p>
          <button onClick={() => setShowAdd(true)} className="btn-primary inline-flex items-center gap-2">
            <Plus className="w-4 h-4" /> Add Your First Product
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}

      {showAdd && (
        <AddProductModal
          onClose={() => setShowAdd(false)}
          onSuccess={() => {
            setRefreshKey(k => k + 1)
          }}
        />
      )}
    </div>
  )
}
