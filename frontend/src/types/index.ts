// SmartCart AI — TypeScript Type Definitions

export interface Category {
  id: string
  name: string
  slug: string
  icon?: string
  product_count?: number
}

export interface Store {
  id: string
  name: string
  slug: string
  logo_url?: string
  website?: string
}

export interface StorePrice {
  store_id: string
  store_name: string
  store_slug: string
  current_price: number | null
  is_on_sale: boolean
  original_price?: number | null
  date_captured?: string | null
}

export interface Product {
  id: string
  name: string
  brand?: string
  description?: string
  weight_volume?: string
  image_url?: string
  category_name?: string
  category_slug?: string
  min_price?: number
  max_price?: number
  avg_price?: number
  store_count?: number
  store_prices?: StorePrice[]
}

export interface PriceHistoryPoint {
  date: string
  price: number
  is_on_sale: boolean
  original_price?: number
  store_name: string
  store_slug: string
}

export interface TopMover {
  product_id?: string
  product_name: string
  category: string
  store_name: string
  current_price: number
  old_price: number
  price_delta: number
  pct_change: number
  direction: 'up' | 'down'
}

export interface PriceAlert {
  product_id: string
  product_name: string
  category: string
  store_name: string
  store_slug: string
  current_price: number
  min_90d: number
  avg_90d: number
  pct_above_low: number
  signal: 'BUY NOW' | 'GOOD PRICE' | 'WAIT'
}

export interface ForecastPoint {
  date: string
  predicted_price: number
  lower_bound?: number
  upper_bound?: number
}

export interface ForecastSeries {
  store_id: string
  store_name: string
  product_id: string
  product_name: string
  current_price?: number
  forecast: ForecastPoint[]
  trend: 'up' | 'down' | 'stable'
  predicted_change_pct: number
  model_name: string
  recommendation: string
}

export interface BasketItem {
  product_id: string
  product_name: string
  quantity: number
  preferred_store?: string
}

export interface StoreBasketTotal {
  store_name: string
  store_slug: string
  total: number
  items_found: number
  items_missing: string[]
  breakdown: BasketBreakdownItem[]
}

export interface BasketBreakdownItem {
  product: string
  price: number
  qty: number
  line_total: number
  is_on_sale: boolean
}

export interface BasketOptimizeResult {
  best_single_store: StoreBasketTotal
  all_stores: StoreBasketTotal[]
  potential_savings: number
  savings_pct: number
  recommendation: string
}

export interface DashboardSummary {
  total_products: number
  total_stores: number
  total_categories: number
  total_price_records: number
  avg_price_today?: number
  items_on_sale: number
  wow_inflation_pct: number
}

export interface CategoryBreakdown {
  category_id: string
  category: string
  slug: string
  icon?: string
  current_avg_price: number
  product_count: number
  avg_price_30d_ago?: number
  mom_change_pct?: number
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
  suggestions?: string[]
}

export interface InflationData {
  category: string
  slug: string
  period: string
  avg_price: number
  change_pct?: number
}

export interface StoreComparison {
  store_name: string
  slug: string
  products_tracked: number
  avg_price: number
  cheapest_count: number
  pct_cheapest: number
}
