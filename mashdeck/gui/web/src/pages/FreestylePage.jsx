import { useState, useEffect, useRef } from 'react'
import { Send, Mic, Loader } from 'lucide-react'
import axios from 'axios'

export default function FreestylePage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [generating, setGenerating] = useState(false)
  const [started, setStarted] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(scrollToBottom, [messages])

  const handleStart = async () => {
    try {
      await axios.post('/api/freestyle/start')
      setStarted(true)
      setMessages([{ type: 'system', text: '🎤 Freestyle mode activated! Type messages and hit "Freestyle" to generate.' }])
    } catch (error) {
      alert('Error starting freestyle: ' + error.message)
    }
  }

  const handleSendMessage = async () => {
    if (!input.trim()) return

    const newMessage = { type: 'user', text: input }
    setMessages([...messages, newMessage])

    try {
      await axios.post(`/api/freestyle/chat?message=${encodeURIComponent(input)}`)
    } catch (error) {
      console.error('Error sending chat:', error)
    }

    setInput('')
  }

  const handleGenerate = async () => {
    setGenerating(true)

    try {
      const response = await axios.post('/api/freestyle/generate', {
        bars: 4,
        style: 'aggressive'
      })

      setMessages([...messages, {
        type: 'ai',
        text: '🔥 Freestyle generated!',
        audio: response.data.audio_path
      }])

    } catch (error) {
      alert('Error generating freestyle: ' + error.message)
    } finally {
      setGenerating(false)
    }
  }

  if (!started) {
    return (
      <div className="max-w-4xl mx-auto text-center py-20">
        <div className="w-32 h-32 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-full flex items-center justify-center mx-auto mb-8">
          <Mic className="w-16 h-16" />
        </div>
        <h1 className="text-5xl font-bold mb-4">Live Freestyle Mode</h1>
        <p className="text-xl text-gray-400 mb-8">
          Chat-reactive freestyle rap generation in real-time
        </p>
        <button onClick={handleStart} className="button-primary text-lg px-8 py-4">
          Start Freestyle Session
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-8">Live Freestyle</h1>

      <div className="card h-[600px] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] rounded-lg px-4 py-2 ${
                  msg.type === 'user'
                    ? 'bg-accent text-white'
                    : msg.type === 'ai'
                    ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white'
                    : 'bg-gray-700 text-gray-300'
                }`}
              >
                {msg.text}
                {msg.audio && (
                  <div className="mt-2">
                    <audio controls className="w-full">
                      <source src={msg.audio} type="audio/wav" />
                    </audio>
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-700 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type a message (topic, vibe, etc.)"
              className="flex-1 bg-tertiary border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-accent"
            />
            <button
              onClick={handleSendMessage}
              className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="px-6 py-2 bg-accent hover:bg-accent-hover rounded-lg transition-colors disabled:opacity-50"
            >
              {generating ? (
                <Loader className="w-5 h-5 animate-spin" />
              ) : (
                <Mic className="w-5 h-5" />
              )}
            </button>
          </div>
          <div className="text-xs text-gray-500 mt-2">
            Type messages to feed the AI, then click the mic to generate a freestyle
          </div>
        </div>
      </div>
    </div>
  )
}
