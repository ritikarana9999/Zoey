'use client'

import { useEffect, useState } from 'react'
import { ChatInterface } from '@/components/assistant/ChatInterface'
import { assistantApi } from '@/lib/api'

export default function AssistantPage() {
  const [suggestions, setSuggestions] = useState<string[]>([])

  useEffect(() => {
    assistantApi.getSuggestions()
      .then((data) => setSuggestions(data.suggestions || []))
      .catch(() => {})
  }, [])

  return (
    <div className="space-y-4 animate-fade-in h-full">
      <div>
        <h2 className="text-2xl font-bold text-white">AI Assistant</h2>
        <p className="text-slate-400 mt-1">
          Ask me anything about grocery prices, deals, and savings
        </p>
      </div>

      <div style={{ height: 'calc(100vh - 200px)' }}>
        <ChatInterface initialSuggestions={suggestions} />
      </div>
    </div>
  )
}
