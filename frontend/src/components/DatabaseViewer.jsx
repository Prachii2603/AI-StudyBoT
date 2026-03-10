import { useState, useEffect } from 'react'
import { getCurrentUser } from '../services/api'
import LoadingSpinner from './LoadingSpinner'

export default function DatabaseViewer() {
  const [users, setUsers] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [leaderboard, setLeaderboard] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('users')
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const fetchWithTimeout = (url, timeout = 3000) => {
        return Promise.race([
          fetch(url),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Request timeout')), timeout)
          )
        ])
      }

      // Fetch users (essential)
      try {
        const usersResponse = await fetchWithTimeout('http://localhost:8000/api/auth/users')
        if (usersResponse.ok) {
          const usersData = await usersResponse.json()
          setUsers(usersData.users || [])
        }
      } catch (error) {
        console.log('Users data not available')
        setUsers([])
      }
      
      // Fetch leaderboard (optional)
      try {
        const leaderboardResponse = await fetchWithTimeout('http://localhost:8000/api/auth/leaderboard')
        if (leaderboardResponse.ok) {
          const leaderboardData = await leaderboardResponse.json()
          setLeaderboard(leaderboardData.leaderboard || [])
        }
      } catch (error) {
        console.log('Leaderboard not available')
        setLeaderboard([])
      }
      
      // Get current user for analytics (optional)
      try {
        const currentUser = await getCurrentUser()
        if (currentUser.id) {
          const analyticsResponse = await fetchWithTimeout(`http://localhost:8000/api/auth/analytics/${currentUser.id}`)
          if (analyticsResponse.ok) {
            const analyticsData = await analyticsResponse.json()
            setAnalytics(analyticsData)
          }
        }
      } catch (error) {
        console.log('Analytics not available')
        setAnalytics(null)
      }
      
    } catch (error) {
      console.error('Error fetching data:', error)
      setError('Unable to load database information')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-xl p-6">
        <LoadingSpinner message="Loading database information..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-xl p-6">
        <div className="text-center">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-red-600 mb-2">Database Error</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">🗄️ Database Overview</h2>
        <button
          onClick={fetchData}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
        >
          Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 mb-6">
        {['users', 'analytics', 'leaderboard'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg capitalize ${
              activeTab === tab
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Registered Users ({users.length})</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-2 text-left">Name</th>
                  <th className="px-4 py-2 text-left">Email</th>
                  <th className="px-4 py-2 text-left">Grade</th>
                  <th className="px-4 py-2 text-left">Interests</th>
                  <th className="px-4 py-2 text-left">Sessions</th>
                  <th className="px-4 py-2 text-left">Joined</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user, index) => (
                  <tr key={user.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-4 py-2 font-medium">{user.name}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{user.email}</td>
                    <td className="px-4 py-2">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                        {user.grade || 'N/A'}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      <div className="flex flex-wrap gap-1">
                        {(user.interests || []).slice(0, 2).map((interest, i) => (
                          <span key={i} className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                            {interest}
                          </span>
                        ))}
                        {user.interests && user.interests.length > 2 && (
                          <span className="text-xs text-gray-500">+{user.interests.length - 2}</span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-2 text-center">{user.total_sessions || 0}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Your Learning Analytics</h3>
          {analytics ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* User Info */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">Profile Summary</h4>
                <div className="space-y-2 text-sm">
                  <p><strong>Total Sessions:</strong> {analytics.user_info.total_sessions}</p>
                  <p><strong>Average Score:</strong> {Math.round(analytics.user_info.average_score * 100)}%</p>
                  <p><strong>Preferred Difficulty:</strong> {analytics.user_info.preferred_difficulty}/3</p>
                  <p><strong>Member Since:</strong> {new Date(analytics.user_info.member_since).toLocaleDateString()}</p>
                </div>
              </div>

              {/* Quiz Stats */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-800 mb-2">Quiz Performance</h4>
                <div className="space-y-2 text-sm">
                  <p><strong>Total Quizzes:</strong> {analytics.quiz_stats.total_quizzes}</p>
                  <p><strong>Questions Answered:</strong> {analytics.quiz_stats.total_questions}</p>
                  <p><strong>Average Score:</strong> {Math.round(analytics.quiz_stats.average_score)}%</p>
                  <p><strong>Best Score:</strong> {Math.round(analytics.quiz_stats.best_score)}%</p>
                </div>
              </div>

              {/* Game Stats */}
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-semibold text-purple-800 mb-2">Game Performance</h4>
                <div className="space-y-2 text-sm">
                  <p><strong>Total Games:</strong> {analytics.game_stats.total_games}</p>
                  <p><strong>Favorite Game:</strong> {analytics.game_stats.favorite_game || 'None'}</p>
                  <div>
                    <strong>Best Scores:</strong>
                    <ul className="ml-4 mt-1">
                      {Object.entries(analytics.game_stats.best_scores).map(([game, score]) => (
                        <li key={game} className="text-xs">
                          {game}: {score}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Learning Progress */}
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h4 className="font-semibold text-yellow-800 mb-2">Learning Progress</h4>
                <div className="space-y-2 text-sm">
                  {Object.entries(analytics.learning_progress).slice(0, 3).map(([topic, progress]) => (
                    <div key={topic}>
                      <p className="font-medium">{topic}</p>
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-yellow-600 h-2 rounded-full"
                            style={{ width: `${Math.min(100, progress.mastery_level)}%` }}
                          ></div>
                        </div>
                        <span className="text-xs">{Math.round(progress.mastery_level)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-600">No analytics data available. Please log in to see your analytics.</p>
          )}
        </div>
      )}

      {/* Leaderboard Tab */}
      {activeTab === 'leaderboard' && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Top Performers</h3>
          <div className="space-y-3">
            {leaderboard.map((user, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${
                    index === 0 ? 'bg-yellow-500' :
                    index === 1 ? 'bg-gray-400' :
                    index === 2 ? 'bg-orange-600' : 'bg-blue-500'
                  }`}>
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium">{user.name}</p>
                    <p className="text-sm text-gray-600">{user.sessions} sessions</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg">{Math.round((user.score || 0) * 100)}%</p>
                  <p className="text-sm text-gray-600">avg score</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Database Stats */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-semibold text-gray-800 mb-2">Database Statistics</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-600">{users.length}</div>
            <div className="text-sm text-gray-600">Total Users</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">
              {users.reduce((sum, user) => sum + (user.total_sessions || 0), 0)}
            </div>
            <div className="text-sm text-gray-600">Total Sessions</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-600">{leaderboard.length}</div>
            <div className="text-sm text-gray-600">Active Learners</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-orange-600">
              {analytics ? Object.keys(analytics.learning_progress || {}).length : 0}
            </div>
            <div className="text-sm text-gray-600">Topics Covered</div>
          </div>
        </div>
      </div>
    </div>
  )
}