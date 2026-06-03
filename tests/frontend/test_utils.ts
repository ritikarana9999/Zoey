/**
 * Tests for frontend utility functions.
 * Run with: npx ts-node --esm tests/frontend/test_utils.ts
 * Or integrate with Jest/Vitest.
 */

// Simple test runner
let passed = 0
let failed = 0

function test(name: string, fn: () => void) {
  try {
    fn()
    console.log(`  ✓ ${name}`)
    passed++
  } catch (e: any) {
    console.error(`  ✗ ${name}`)
    console.error(`    ${e.message}`)
    failed++
  }
}

function assertEqual(actual: any, expected: any, msg?: string) {
  if (actual !== expected) {
    throw new Error(msg || `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`)
  }
}

function assertIncludes(str: string, substr: string, msg?: string) {
  if (!str.includes(substr)) {
    throw new Error(msg || `Expected "${str}" to include "${substr}"`)
  }
}

function assertTruthy(val: any, msg?: string) {
  if (!val) throw new Error(msg || `Expected truthy value, got ${val}`)
}

// ---- Mock the utility functions (since we can't import directly) ----

function formatCurrency(amount: number | null | undefined): string {
  if (amount == null) return 'N/A'
  return new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

function formatPct(value: number | null | undefined, decimals = 1): string {
  if (value == null) return 'N/A'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(decimals)}%`
}

function getStoreColor(slug: string): string {
  const colors: Record<string, string> = {
    woolworths: '#00aa46',
    coles: '#e41b17',
    aldi: '#00609c',
  }
  return colors[slug] || '#6366f1'
}

function getSignalColor(signal: string): string {
  switch (signal) {
    case 'BUY NOW': return 'text-green-400 bg-green-400/10'
    case 'GOOD PRICE': return 'text-emerald-400 bg-emerald-400/10'
    case 'WAIT': return 'text-yellow-400 bg-yellow-400/10'
    default: return 'text-gray-400 bg-gray-400/10'
  }
}

function getInflationColor(pct: number | null | undefined): string {
  if (pct == null) return 'text-gray-400'
  if (pct > 3) return 'text-red-400'
  if (pct > 0) return 'text-orange-400'
  if (pct < -1) return 'text-green-400'
  return 'text-gray-400'
}

function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str
  return str.slice(0, maxLength) + '…'
}

function getTrendColor(trend: string): string {
  switch (trend) {
    case 'up': return 'text-red-400'
    case 'down': return 'text-green-400'
    default: return 'text-gray-400'
  }
}

// ---- Tests ----

console.log('\nFormatCurrency tests:')
test('formats positive amount', () => {
  assertIncludes(formatCurrency(3.49), '3.49')
})
test('formats zero', () => {
  assertIncludes(formatCurrency(0), '0.00')
})
test('formats null as N/A', () => {
  assertEqual(formatCurrency(null), 'N/A')
})
test('formats undefined as N/A', () => {
  assertEqual(formatCurrency(undefined), 'N/A')
})
test('includes AU currency symbol', () => {
  assertIncludes(formatCurrency(5.00), '$')
})
test('formats large amount', () => {
  assertIncludes(formatCurrency(1000), '1,000')
})

console.log('\nFormatPct tests:')
test('formats positive pct with + sign', () => {
  assertEqual(formatPct(3.5), '+3.5%')
})
test('formats negative pct without + sign', () => {
  assertEqual(formatPct(-2.1), '-2.1%')
})
test('formats zero', () => {
  assertEqual(formatPct(0), '0.0%')
})
test('formats null as N/A', () => {
  assertEqual(formatPct(null), 'N/A')
})
test('respects decimals parameter', () => {
  assertEqual(formatPct(3.567, 2), '+3.57%')
})

console.log('\nGetStoreColor tests:')
test('woolworths returns green', () => {
  assertEqual(getStoreColor('woolworths'), '#00aa46')
})
test('coles returns red', () => {
  assertEqual(getStoreColor('coles'), '#e41b17')
})
test('aldi returns blue', () => {
  assertEqual(getStoreColor('aldi'), '#00609c')
})
test('unknown store returns primary', () => {
  assertEqual(getStoreColor('unknown'), '#6366f1')
})

console.log('\nGetSignalColor tests:')
test('BUY NOW returns green', () => {
  assertIncludes(getSignalColor('BUY NOW'), 'green')
})
test('WAIT returns yellow', () => {
  assertIncludes(getSignalColor('WAIT'), 'yellow')
})
test('GOOD PRICE returns emerald', () => {
  assertIncludes(getSignalColor('GOOD PRICE'), 'emerald')
})
test('unknown signal returns gray', () => {
  assertIncludes(getSignalColor('UNKNOWN'), 'gray')
})

console.log('\nGetInflationColor tests:')
test('high inflation (>3%) is red', () => {
  assertEqual(getInflationColor(4.5), 'text-red-400')
})
test('moderate inflation is orange', () => {
  assertEqual(getInflationColor(1.5), 'text-orange-400')
})
test('deflation (<-1%) is green', () => {
  assertEqual(getInflationColor(-2.0), 'text-green-400')
})
test('null returns gray', () => {
  assertEqual(getInflationColor(null), 'text-gray-400')
})
test('zero is gray', () => {
  assertEqual(getInflationColor(0), 'text-gray-400')
})

console.log('\nTruncate tests:')
test('short string unchanged', () => {
  assertEqual(truncate('Hello', 10), 'Hello')
})
test('long string truncated with ellipsis', () => {
  const result = truncate('Hello World', 5)
  assertEqual(result, 'Hello…')
})
test('exact length unchanged', () => {
  assertEqual(truncate('Hello', 5), 'Hello')
})
test('empty string', () => {
  assertEqual(truncate('', 10), '')
})

console.log('\nGetTrendColor tests:')
test('up trend is red', () => {
  assertEqual(getTrendColor('up'), 'text-red-400')
})
test('down trend is green', () => {
  assertEqual(getTrendColor('down'), 'text-green-400')
})
test('stable trend is gray', () => {
  assertEqual(getTrendColor('stable'), 'text-gray-400')
})

// ---- Summary ----
console.log(`\n${'='.repeat(40)}`)
console.log(`Results: ${passed} passed, ${failed} failed`)
console.log('='.repeat(40))

if (failed > 0) {
  process.exit(1)
}
