'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    router.replace('/dashboard')
  }, [router])

  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-slate-400 animate-pulse">Loading SmartCart AI...</div>
    </div>
  )
}
