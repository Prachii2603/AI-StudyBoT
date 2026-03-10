import { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../services/api'

export default function Chat({ studentId }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [difficulty, setDifficulty] = useState(1)
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(scrollToBottom, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input, timestamp: new Date().toISOString() }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await sendMessage(input, studentId, difficulty)
      setMessages(prev => [...prev, response])
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleVoice = () => {
    setIsRecording(!isRecording)
    // Implement voice recording logic
  }

  const renderMessage = (msg, idx) => {
    const isUser = msg.role === 'user'
    
    return (
      <div key={idx} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
          <div
            className={`rounded-lg px-4 py-3 ${
              isUser
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            <div className="whitespace-pre-wrap">{msg.content}</div>
            
            {/* Display images if available */}
            {msg.images && msg.images.length > 0 && (
              <div className="mt-3 space-y-2">
                {msg.images.map((image, imgIdx) => (
                  <div key={imgIdx} className="border rounded-lg overflow-hidden">
                    <img
                      src={image.url}
                      alt={image.alt_text}
                      className="w-full h-48 object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none'
                      }}
                    />
                    <div className="p-2 bg-white">
                      <p className="text-sm text-gray-600">{image.description}</p>
                      <p className="text-xs text-gray-400">{image.credit}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Display learning resources if available */}
            {msg.learning_resources && msg.learning_resources.length > 0 && (
              <div className="mt-3 space-y-2">
                <div className="text-sm font-semibold text-gray-700 bg-blue-50 px-2 py-1 rounded">
                  📚 Learning Resources:
                </div>
                {msg.learning_resources.map((resource, resIdx) => (
                  <div key={resIdx} className="bg-white border rounded-lg p-3">
                    <div className="flex justify-between items-start mb-1">
                      <h4 className="font-medium text-blue-600 text-sm">{resource.title}</h4>
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded">{resource.type}</span>
                    </div>
                    <p className="text-xs text-gray-600 mb-2">{resource.description}</p>
                    <a
                      href={resource.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-xs text-blue-600 hover:text-blue-800"
                    >
                      Visit Resource →
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {msg.timestamp && (
            <div className={`text-xs text-gray-400 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-6 h-[700px] flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">🤖 AI Tutor Chat</h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Difficulty:</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(Number(e.target.value))}
              className="border rounded px-2 py-1 text-sm"
            >
              <option value={1}>Beginner</option>
              <option value={2}>Intermediate</option>
              <option value={3}>Advanced</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto mb-4 space-y-2">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <div className="text-4xl mb-2">👋</div>
            <p>Hi! I'm your AI learning tutor. Ask me anything!</p>
            <div className="mt-4 text-sm">
              <p className="mb-2">Try asking about:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">Neural Networks</span>
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">Machine Learning</span>
                <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">Programming</span>
                <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded text-xs">Mathematics</span>
              </div>
            </div>
          </div>
        )}
        
        {messages.map(renderMessage)}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3 max-w-[70%]">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                <span className="text-gray-600">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="Ask me anything about learning..."
          className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-600"
          disabled={loading}
        />
        <button
          onClick={handleVoice}
          className={`px-4 py-2 rounded-lg transition-colors ${
            isRecording ? 'bg-red-500 hover:bg-red-600' : 'bg-gray-300 hover:bg-gray-400'
          } text-white`}
          disabled={loading}
        >
          🎤
        </button>
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </div>
  )
}
