import { useState, useEffect, Suspense, lazy } from 'react'
import Login from './components/Login'
import LoadingSpinner from './components/LoadingSpinner'
import { getCurrentUser, logout } from './services/api'

// Lazy load components to improve initial loading time
const Chat = lazy(() => import('./components/Chat'))
const Quiz = lazy(() => import('./components/Quiz'))
const Dashboard = lazy(() => import('./components/Dashboard'))
const Games = lazy(() => import('./components/Games'))
const UserProfile = lazy(() => import('./components/UserProfile'))
const ProgressTracker = lazy(() => import('./components/ProgressTracker'))
const ConnectionTest = lazy(() => import('./components/ConnectionTest'))

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Check for existing authentication on app load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token')
        const savedUser = localStorage.getItem('user')
        
        if (token && savedUser) {
          // Use saved user data immediately for faster loading
          const userData = JSON.parse(savedUser)
          setUser(userData)
          
          // Optionally validate token in background (don't block UI)
          setTimeout(async () => {
            try {
              const currentUser = await getCurrentUser()
              if (currentUser && currentUser.id !== userData.id) {
                setUser(currentUser)
              }
            } catch (error) {
              console.log('Token validation failed, using cached user data')
            }
          }, 1000)
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      setActiveTab('chat')
    }
  }

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-cyan-100 flex items-center justify-center">
        <LoadingSpinner message="Initializing AI StudyBot..." />
      </div>
    )
  }

  // Show login page if user is not authenticated
  if (!user) {
    return <Login onLogin={handleLogin} />
  }

  const tabs = [
    { id: 'chat', name: '💬 Chat', icon: '🤖' },
    { id: 'quiz', name: '📝 Quiz', icon: '❓' },
    { id: 'games', name: '🎮 Games', icon: '🎯' },
    { id: 'progress', name: '📊 Progress', icon: '📈' },
    { id: 'dashboard', name: '🏆 Dashboard', icon: '📊' },
    { id: 'onboarding', name: '👤 Profile', icon: '🎯' },
    { id: 'test', name: '🔗 Connection', icon: '🔧' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-cyan-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="text-2xl font-bold text-indigo-600">🤖 AI StudyBot</div>
              <div className="ml-4 text-sm text-gray-500">
                Personalized Learning Platform
              </div>
            </div>
            
            {/* User Info */}
            <div className="flex items-center space-x-4">
              <div className="text-sm">
                <span className="text-gray-600">Welcome, </span>
                <span className="font-medium text-gray-900">{user.name}</span>
                {user.grade && (
                  <span className="ml-2 text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded">
                    {user.grade}
                  </span>
                )}
              </div>
              <button
                onClick={handleLogout}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg text-sm transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <Suspense fallback={<LoadingSpinner message="Loading component..." />}>
          {activeTab === 'chat' && <Chat studentId={user.id} />}
          {activeTab === 'quiz' && <Quiz studentId={user.id} />}
          {activeTab === 'games' && <Games studentId={user.id} />}
          {activeTab === 'progress' && <ProgressTracker studentId={user.id} />}
          {activeTab === 'dashboard' && <Dashboard studentId={user.id} />}
          {activeTab === 'onboarding' && <UserProfile user={user} />}
          {activeTab === 'test' && <ConnectionTest />}
        </Suspense>
      </main>
    </div>
  )
}

export default App