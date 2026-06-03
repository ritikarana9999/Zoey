'use client'
import { useEffect, useState } from 'react'
import { motion, useMotionValue, useSpring } from 'framer-motion'

export default function CustomCursor() {
  const [isHovering, setIsHovering] = useState(false)
  const [isVisible, setIsVisible] = useState(false)

  const rawX = useMotionValue(-100)
  const rawY = useMotionValue(-100)

  const springCfg = { stiffness: 200, damping: 22, mass: 0.4 }
  const ringX = useSpring(rawX, springCfg)
  const ringY = useSpring(rawY, springCfg)

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      rawX.set(e.clientX)
      rawY.set(e.clientY)
      setIsVisible(true)
    }

    const onEnter = () => setIsHovering(true)
    const onLeave = () => setIsHovering(false)

    window.addEventListener('mousemove', onMove)

    const addListeners = () => {
      document.querySelectorAll('a, button, [data-hover]').forEach((el) => {
        el.addEventListener('mouseenter', onEnter)
        el.addEventListener('mouseleave', onLeave)
      })
    }

    addListeners()
    const observer = new MutationObserver(addListeners)
    observer.observe(document.body, { childList: true, subtree: true })

    return () => {
      window.removeEventListener('mousemove', onMove)
      observer.disconnect()
    }
  }, [rawX, rawY])

  if (!isVisible) return null

  return (
    <>
      {/* Outer ring — lagged spring */}
      <motion.div
        className="fixed top-0 left-0 pointer-events-none z-[9999] rounded-full"
        style={{
          x: ringX,
          y: ringY,
          translateX: '-50%',
          translateY: '-50%',
          border: isHovering
            ? '1.5px solid rgba(192,132,252,0.9)'
            : '1.5px solid rgba(192,132,252,0.5)',
          width: isHovering ? 52 : 36,
          height: isHovering ? 52 : 36,
          boxShadow: isHovering
            ? '0 0 20px rgba(192,132,252,0.4), inset 0 0 10px rgba(192,132,252,0.1)'
            : 'none',
          transition: 'width 0.25s ease, height 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease',
          mixBlendMode: 'normal',
        }}
      />
      {/* Inner dot — exact position */}
      <motion.div
        className="fixed top-0 left-0 pointer-events-none z-[9999] rounded-full"
        style={{
          x: rawX,
          y: rawY,
          translateX: '-50%',
          translateY: '-50%',
          width: isHovering ? 6 : 5,
          height: isHovering ? 6 : 5,
          background: '#22d3ee',
          boxShadow: '0 0 8px #22d3ee',
          transition: 'width 0.2s ease, height 0.2s ease',
        }}
      />
    </>
  )
}
