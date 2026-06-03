const { fontFamily } = require('tailwindcss/defaultTheme')

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx,js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        lavender: '#c084fc',
        'baby-blue': '#93c5fd',
        'soft-pink': '#f9a8d4',
        'electric-cyan': '#22d3ee',
        chrome: '#94a3b8',
        pearl: '#e2e8f0',
        'neon-green': '#4ade80',
        'warm-amber': '#fbbf24',
        'deep-bg': '#050508',
        'surface': 'rgba(255,255,255,0.04)',
      },
      fontFamily: {
        display: ['var(--font-display)', ...fontFamily.sans],
        body: ['var(--font-body)', ...fontFamily.sans],
        pixel: ['var(--font-pixel)', 'ui-monospace', 'monospace'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'float-alt': 'floatAlt 8s ease-in-out infinite',
        'float-slow': 'float 12s ease-in-out infinite',
        'sparkle': 'sparkle 3s ease-in-out infinite',
        'shimmer': 'shimmer 4s linear infinite',
        'holographic': 'holographic 6s ease infinite',
        'pulse-glow': 'pulseGlow 3s ease-in-out infinite',
        'blink': 'blink 1.2s step-end infinite',
        'loading-progress': 'loadingProgress 2.5s ease-in-out forwards',
        'spin-slow': 'spinSlow 30s linear infinite',
        'spin-reverse': 'spinReverse 20s linear infinite',
        'spin-fast': 'spinSlow 8s linear infinite',
        'scan': 'scan 4s linear infinite',
        'slide-up': 'slideUp 0.7s ease forwards',
        'fade-in': 'fadeIn 0.6s ease forwards',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-18px)' },
        },
        floatAlt: {
          '0%, 100%': { transform: 'translateY(-8px) rotate(2deg)' },
          '50%': { transform: 'translateY(8px) rotate(-2deg)' },
        },
        sparkle: {
          '0%, 100%': { opacity: '0.9', transform: 'scale(1) rotate(0deg)' },
          '33%': { opacity: '0.2', transform: 'scale(0.4) rotate(120deg)' },
          '66%': { opacity: '1', transform: 'scale(1.3) rotate(240deg)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% center' },
          '100%': { backgroundPosition: '200% center' },
        },
        holographic: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 15px rgba(192,132,252,0.3)' },
          '50%': { boxShadow: '0 0 45px rgba(192,132,252,0.7), 0 0 70px rgba(147,197,253,0.3)' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
        loadingProgress: {
          '0%': { width: '0%' },
          '15%': { width: '12%' },
          '35%': { width: '30%' },
          '55%': { width: '52%' },
          '75%': { width: '74%' },
          '90%': { width: '88%' },
          '100%': { width: '100%' },
        },
        spinSlow: {
          from: { transform: 'rotate(0deg)' },
          to: { transform: 'rotate(360deg)' },
        },
        spinReverse: {
          from: { transform: 'rotate(360deg)' },
          to: { transform: 'rotate(0deg)' },
        },
        scan: {
          '0%': { top: '-2px', opacity: '0.8' },
          '100%': { top: '100%', opacity: '0.2' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      backgroundSize: {
        '200%': '200%',
        '400%': '400%',
      },
    },
  },
  plugins: [],
}
