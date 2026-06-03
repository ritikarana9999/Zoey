import axios from 'axios'
import type {
  Product,
  PriceHistoryPoint,
  TopMover,
  PriceAlert,
  ForecastSeries,
  BasketItem,
  BasketOptimizeResult,
  DashboardSummary,
  CategoryBreakdown,
  InflationData,
  StoreComparison,
  Category,
  Store,
} from '@/types'

// Use relative URL so Next.js rewrites proxy to backend — works in Codespaces and local
const api = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use((config) => {
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// ---- Products ----
export const productsApi = {
  list: (params?: { category?: string; search?: string; limit?: number; offset?: number }) =>
    api.get<Product[]>('/api/products', { params }).then((r) => r.data),

  search: (q: string, limit?: number) =>
    api.get<Product[]>('/api/products/search', { params: { q, limit } }).then((r) => r.data),

  getById: (id: string) =>
    api.get<Product>(`/api/products/${id}`).then((r) => r.data),

  getPriceHistory: (id: string, days?: number, storeId?: string) =>
    api.get<PriceHistoryPoint[]>(`/api/products/${id}/price-history`, {
      params: { days, store_id: storeId },
    }).then((r) => r.data),

  getCategories: () =>
    api.get<Category[]>('/api/products/categories').then((r) => r.data),
}

// ---- Prices ----
export const pricesApi = {
  getCurrent: (params?: { category?: string; store?: string; limit?: number }) =>
    api.get('/api/prices/current', { params }).then((r) => r.data),

  getTopMovers: (limit?: number) =>
    api.get<TopMover[]>('/api/prices/top-movers', { params: { limit } }).then((r) => r.data),

  getAlerts: () =>
    api.get<PriceAlert[]>('/api/prices/alerts').then((r) => r.data),

  getStores: () =>
    api.get<Store[]>('/api/prices/stores').then((r) => r.data),
}

// ---- Forecasts ----
export const forecastsApi = {
  getForProduct: (productId: string, storeId?: string) =>
    api.get<ForecastSeries[]>(`/api/forecasts/${productId}`, {
      params: { store_id: storeId },
    }).then((r) => r.data),

  getForCategory: (categorySlug: string) =>
    api.get(`/api/forecasts/category/${categorySlug}`).then((r) => r.data),

  triggerGeneration: (productId: string) =>
    api.post(`/api/forecasts/generate/${productId}`).then((r) => r.data),
}

// ---- Basket ----
export const basketApi = {
  optimize: (items: BasketItem[]) =>
    api.post<BasketOptimizeResult>('/api/basket/optimize', { items }).then((r) => r.data),

  compare: (items: BasketItem[]) =>
    api.post('/api/basket/compare', { items }).then((r) => r.data),

  save: (name: string, items: BasketItem[]) =>
    api.post('/api/basket', { name, items }).then((r) => r.data),

  getById: (id: string) =>
    api.get(`/api/basket/${id}`).then((r) => r.data),
}

// ---- Analytics ----
export const analyticsApi = {
  getSummary: () =>
    api.get<DashboardSummary>('/api/analytics/summary').then((r) => r.data),

  getInflation: (period?: 'weekly' | 'monthly') =>
    api.get<InflationData[]>('/api/analytics/inflation', { params: { period } }).then((r) => r.data),

  getStoreComparison: () =>
    api.get<StoreComparison[]>('/api/analytics/store-comparison').then((r) => r.data),

  getPriceTrends: (days?: number) =>
    api.get('/api/analytics/price-trends', { params: { days } }).then((r) => r.data),

  getCategoryBreakdown: () =>
    api.get<CategoryBreakdown[]>('/api/analytics/category-breakdown').then((r) => r.data),
}

// ---- AI Assistant ----
export const assistantApi = {
  chat: (message: string, history: { role: string; content: string }[]) =>
    api.post('/api/assistant/chat', { message, history }).then((r) => r.data),

  getSuggestions: () =>
    api.get('/api/assistant/suggestions').then((r) => r.data),
}

export default api
