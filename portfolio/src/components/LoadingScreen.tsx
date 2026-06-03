'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

const BOOT_LINES = [
  '> Initializing RITIKA.RANA OS...',
  '> Loading data pipelines........OK',
  '> Mounting creative modules.....OK',
  '> Connecting to Brisbane.........OK',
  '> Brewing oat flat white..........OK',
  '> Portfolio ready. Launching...',
]

export default function LoadingScreen() {
  const [visibleLines, setVisibleLines] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const lineInterval = setInterval(() => {
      setVisibleLines((v) => Math.min(v + 1, BOOT_LINES.length))
    }, 380)

    const progressInterval = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) { clearInterval(progressInterval); return 100 }
        return p + 2
      })
    }, 55)

    return () => {
      clearInterval(lineInterval)
      clearInterval(progressInterval)
    }
  }, [])

  return (
    <motion.div
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-center"
      style={{ background: '#020205' }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.7, ease: 'easeInOut' }}
    >
      {/* Scan line */}
      <div
        className="absolute left-0 right-0 h-px pointer-events-none"
        style={{
          background: 'rgba(192,132,252,0.3)',
          animation: 'scan 4s linear infinite',
          position: 'absolute',
        }}
      />

      <div className="w-full max-w-md px-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <h1
              className="font-pixel text-4xl md:text-5xl tracking-widest mb-1"
              style={{
                background: 'linear-gradient(135deg, #c084fc, #93c5fd, #f9a8d4)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              RITIKA.RANA
            </h1>
            <p className="font-pixel text-electric-cyan/60 text-sm tracking-[0.3em]">
              PORTFOLIO.OS v2025
            </p>
          </motion.div>
        </div>

        {/* Terminal output */}
        <div
          className="rounded-lg p-5 mb-6 font-pixel text-sm"
          style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(192,132,252,0.15)',
            minHeight: '180px',
          }}
        >
          {BOOT_LINES.slice(0, visibleLines).map((line, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              className="mb-1 text-slate-400"
            >
              <span style={{ color: i === visibleLines - 1 ? '#22d3ee' : '#94a3b8' }}>
                {line}
              </span>
              {i === visibleLines - 1 && (
                <span className="inline-block w-2 h-4 bg-electric-cyan ml-1 animate-blink" />
              )}
            </motion.div>
          ))}
        </div>

        {/* Progress bar */}
        <div className="mb-3">
          <div className="flex justify-between text-xs font-pixel text-slate-500 mb-2">
            <span>LOADING</span>
            <span className="text-electric-cyan">{progress}%</span>
          </div>
          <div
            className="h-1.5 w-full rounded-full overflow-hidden"
            style={{ background: 'rgba(255,255,255,0.06)' }}
          >
            <motion.div
              className="h-full rounded-full"
              style={{
                background: 'linear-gradient(90deg, #c084fc, #93c5fd, #22d3ee)',
                boxShadow: '0 0 10px rgba(192,132,252,0.6)',
              }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.1 }}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="text-center">
          <span className="font-pixel text-xs text-slate-600 tracking-widest">
            ✦ BRISBANE · AUSTRALIA ✦
          </span>
        </div>
      </div>
    </motion.div>
  )
}
