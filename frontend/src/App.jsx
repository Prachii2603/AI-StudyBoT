import { useState } from 'react'
import Chat from './components/Chat'
import Quiz from './components/Quiz'
import Dashboard from './components/Dashboard'
import Games from './components/Games'
import ConnectionTest from './components/ConnectionTest'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [studentId] = useState('student_' + Math.random().toString(36).substr(2, 9))

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-indigo-600">🤖 AI Learning Platform</h1>
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('test')}
                className={`px-3 py-2 rounded-lg text-sm ${activeTab === 'test' ? 'bg-green-600 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
              >
                🔗 Connection
              </button>
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-3 py-2 rounded-lg text-sm ${activeTab === 'chat' ? 'bg-indigo-600 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
              >
                💬 Chat
              </button>
              <button
                onClick={() => setActiveTab('quiz')}
                className={`px-3 py-2 rounded-lg text-sm ${activeTab === 'quiz' ? 'bg-indigo-600 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
              >
                📝 Quiz
              </button>
              <button
                onClick={() => setActiveTab('games')}
                className={`px-3 py-2 rounded-lg text-sm ${activeTab === 'games' ? 'bg-indigo-600 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
              >
                🎮 Games
              </button>
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-3 py-2 rounded-lg text-sm ${activeTab === 'dashboard' ? 'bg-indigo-600 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
              >
                📊 Dashboard
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'test' && <ConnectionTest />}
        {activeTab === 'chat' && <Chat studentId={studentId} />}
        {activeTab === 'quiz' && <Quiz studentId={studentId} />}
        {activeTab === 'games' && <Games studentId={studentId} />}
        {activeTab === 'dashboard' && <Dashboard studentId={studentId} />}
      </main>
    </div>
  )
}

export default App
