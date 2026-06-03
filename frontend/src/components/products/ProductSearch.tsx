'use client'

import { useState, useEffect, useRef } from 'react'
import { Search, X } from 'lucide-react'
import { productsApi } from '@/lib/api'
import type { Product } from '@/types'

interface ProductSearchProps {
  onSelect?: (product: Product) => void
  placeholder?: string
  showResults?: boolean
}

export function ProductSearch({
  onSelect,
  placeholder = 'Search products...',
  showResults = true,
}: ProductSearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const debounceRef = useRef<NodeJS.Timeout>()
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    clearTimeout(debounceRef.current)
    if (query.length < 2) {
      setResults([])
      setOpen(false)
      return
    }

    debounceRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const data = await productsApi.search(query, 8)
        setResults(data)
        setOpen(true)
      } catch {
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 300)
  }, [query])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div ref={containerRef} className="relative w-full">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
        <input
          className="input pl-10 pr-10"
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
        />
        {query && (
          <button
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
            onClick={() => { setQuery(''); setResults([]); setOpen(false) }}
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {showResults && open && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-xl shadow-2xl z-50 max-h-80 overflow-y-auto">
          {loading && (
            <div className="p-3 text-center text-sm text-slate-400">Searching...</div>
          )}
          {!loading && results.length === 0 && query.length >= 2 && (
            <div className="p-3 text-center text-sm text-slate-500">No products found</div>
          )}
          {!loading && results.map((product) => (
            <button
              key={product.id}
              className="w-full text-left px-4 py-3 hover:bg-slate-700 transition-colors border-b border-slate-800 last:border-0"
              onClick={() => {
                if (onSelect) onSelect(product)
                setQuery(product.name)
                setOpen(false)
              }}
            >
              <p className="text-sm text-white font-medium truncate">{product.name}</p>
              <p className="text-xs text-slate-400">
                {product.category_name}
                {product.brand ? ` · ${product.brand}` : ''}
                {product.min_price != null ? ` · from $${product.min_price?.toFixed(2)}` : ''}
              </p>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
