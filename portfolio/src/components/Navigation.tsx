'use client'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const NAV_LINKS = [
  { label: 'About', href: '#about' },
  { label: 'Skills', href: '#skills' },
  { label: 'Projects', href: '#projects' },
  { label: 'Contact', href: '#contact' },
]

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false)
  const [active, setActive] = useState('')
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 50)
      const sections = ['about', 'skills', 'projects', 'contact']
      for (const id of sections) {
        const el = document.getElementById(id)
        if (el) {
          const top = el.getBoundingClientRect().top
          if (top <= 120) setActive(id)
        }
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <motion.header
      className="fixed top-0 left-0 right-0 z-[100] flex justify-center pt-5 px-6"
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 3.2, duration: 0.7, ease: 'easeOut' }}
    >
      <nav
        className="flex items-center justify-between w-full max-w-5xl px-5 py-3 rounded-full transition-all duration-500"
        style={{
          background: scrolled
            ? 'rgba(5,5,8,0.75)'
            : 'rgba(5,5,8,0.3)',
          backdropFilter: scrolled ? 'blur(20px)' : 'blur(10px)',
          WebkitBackdropFilter: scrolled ? 'blur(20px)' : 'blur(10px)',
          border: scrolled
            ? '1px solid rgba(192,132,252,0.2)'
            : '1px solid rgba(255,255,255,0.06)',
          boxShadow: scrolled ? '0 4px 30px rgba(0,0,0,0.4)' : 'none',
        }}
      >
        {/* Logo */}
        <a
          href="#home"
          className="font-pixel text-lg tracking-widest"
          style={{
            background: 'linear-gradient(135deg, #c084fc, #93c5fd)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          RR
        </a>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-1">
          {NAV_LINKS.map((link) => {
            const isActive = active === link.href.slice(1)
            return (
              <a
                key={link.href}
                href={link.href}
                className="relative px-4 py-1.5 rounded-full text-sm font-display font-medium transition-all duration-300"
                style={{
                  color: isActive ? '#c084fc' : 'rgba(226,232,240,0.7)',
                }}
              >
                {isActive && (
                  <motion.span
                    layoutId="nav-pill"
                    className="absolute inset-0 rounded-full"
                    style={{ background: 'rgba(192,132,252,0.12)' }}
                    transition={{ type: 'spring', stiffness: 350, damping: 30 }}
                  />
                )}
                <span className="relative">{link.label}</span>
              </a>
            )
          })}
          <a
            href="/2cbe0a08-RitikaRanaResume.docx"
            download
            className="ml-3 btn-ghost text-xs py-2 px-5 rounded-full"
          >
            Resume ↓
          </a>
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden flex flex-col gap-1.5 p-1"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="block h-px w-5 bg-lavender transition-all duration-300"
              style={{
                transform:
                  mobileOpen
                    ? i === 0
                      ? 'rotate(45deg) translate(4px, 4px)'
                      : i === 1
                      ? 'scaleX(0)'
                      : 'rotate(-45deg) translate(4px, -4px)'
                    : 'none',
              }}
            />
          ))}
        </button>
      </nav>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.97 }}
            transition={{ duration: 0.2 }}
            className="absolute top-20 left-6 right-6 rounded-2xl p-4 md:hidden"
            style={{
              background: 'rgba(5,5,8,0.95)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(192,132,252,0.2)',
            }}
          >
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className="block px-4 py-3 font-display text-slate-300 hover:text-lavender transition-colors"
              >
                {link.label}
              </a>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  )
}
