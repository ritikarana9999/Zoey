'use client'

import { useState } from 'react'
import { X, Plus, Trash2 } from 'lucide-react'

const CATEGORIES = [
  { label: 'Dairy', slug: 'dairy' },
  { label: 'Bakery', slug: 'bakery' },
  { label: 'Produce', slug: 'produce' },
  { label: 'Meat', slug: 'meat' },
  { label: 'Pantry', slug: 'pantry' },
  { label: 'Beverages', slug: 'beverages' },
  { label: 'Frozen', slug: 'frozen' },
  { label: 'Snacks', slug: 'snacks' },
]

const STORES = [
  { label: 'Woolworths', slug: 'woolworths' },
  { label: 'Coles', slug: 'coles' },
  { label: 'Aldi', slug: 'aldi' },
]

interface StorePrice {
  store_slug: string
  price: string
}

interface Props {
  onClose: () => void
  onSuccess: () => void
}

export function AddProductModal({ onClose, onSuccess }: Props) {
  const [name, setName] = useState('')
  const [brand, setBrand] = useState('')
  const [categorySlug, setCategorySlug] = useState('pantry')
  const [weightVolume, setWeightVolume] = useState('')
  const [storePrices, setStorePrices] = useState<StorePrice[]>([
    { store_slug: 'woolworths', price: '' },
  ])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  function addStore() {
    const used = storePrices.map((s) => s.store_slug)
    const next = STORES.find((s) => !used.includes(s.slug))
    if (next) setStorePrices([...storePrices, { store_slug: next.slug, price: '' }])
  }

  function removeStore(i: number) {
    setStorePrices(storePrices.filter((_, idx) => idx !== i))
  }

  function updateStore(i: number, field: keyof StorePrice, val: string) {
    setStorePrices(storePrices.map((s, idx) => (idx === i ? { ...s, [field]: val } : s)))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return setError('Product name is required')
    const validPrices = storePrices.filter((s) => s.price && parseFloat(s.price) > 0)
    if (validPrices.length === 0) return setError('Add at least one store price')

    setSubmitting(true)
    setError('')
    try {
      const res = await fetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          brand: brand.trim(),
          category_slug: categorySlug,
          weight_volume: weightVolume.trim(),
          store_prices: validPrices.map((s) => ({
            store_slug: s.store_slug,
            price: parseFloat(s.price),
          })),
        }),
      })
      if (!res.ok) throw new Error('Failed to save product')
      onSuccess()
      onClose()
    } catch (err: any) {
      setError(err.message || 'Something went wrong')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg shadow-2xl animate-fade-in">
        <div className="flex items-center justify-between p-6 border-b border-slate-800">
          <div>
            <h2 className="text-lg font-semibold text-white">Add Product</h2>
            <p className="text-sm text-slate-400 mt-0.5">Track a new grocery item across stores</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-900/30 border border-red-700/40 text-red-300 text-sm rounded-lg px-4 py-3">
              {error}
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              Product Name <span className="text-red-400">*</span>
            </label>
            <input
              className="input"
              placeholder="e.g. Full Cream Milk 2L"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Brand</label>
              <input
                className="input"
                placeholder="e.g. Pauls"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Weight / Volume</label>
              <input
                className="input"
                placeholder="e.g. 2L"
                value={weightVolume}
                onChange={(e) => setWeightVolume(e.target.value)}
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Category</label>
            <select
              className="input"
              value={categorySlug}
              onChange={(e) => setCategorySlug(e.target.value)}
            >
              {CATEGORIES.map((c) => (
                <option key={c.slug} value={c.slug}>{c.label}</option>
              ))}
            </select>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-slate-300">
                Store Prices <span className="text-red-400">*</span>
              </label>
              {storePrices.length < 3 && (
                <button
                  type="button"
                  onClick={addStore}
                  className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                >
                  <Plus className="w-3 h-3" /> Add store
                </button>
              )}
            </div>
            <div className="space-y-2">
              {storePrices.map((sp, i) => (
                <div key={i} className="flex gap-2">
                  <select
                    className="input flex-1"
                    value={sp.store_slug}
                    onChange={(e) => updateStore(i, 'store_slug', e.target.value)}
                  >
                    {STORES.map((s) => (
                      <option key={s.slug} value={s.slug}>{s.label}</option>
                    ))}
                  </select>
                  <div className="relative flex-1">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">$</span>
                    <input
                      className="input pl-7"
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="0.00"
                      value={sp.price}
                      onChange={(e) => updateStore(i, 'price', e.target.value)}
                    />
                  </div>
                  {storePrices.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeStore(i)}
                      className="text-slate-500 hover:text-red-400 transition-colors px-2"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={submitting} className="btn-primary flex-1">
              {submitting ? 'Saving...' : 'Add Product'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
