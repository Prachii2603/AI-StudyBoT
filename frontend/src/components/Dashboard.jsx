import { useState, useEffect } from 'react'
import { getProgress, getLeaderboard, getAchievements } from '../services/api'

export default function Dashboard({ studentId }) {
  const [progress, setProgress] = useState(null)
  const [achievements, setAchievements] = useState(null)
  const [leaderboard, setLeaderboard] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [studentId])

  const loadData = async () => {
    try {
      setLoading(true)
      const [progressData, achievementsData, leaderboardData] = await Promise.all([
        getProgress(studentId),
        getAchievements(studentId),
        getLeaderboard()
      ])
      setProgress(progressData)
      setAchievements(achievementsData)
      setLeaderboard(leaderboardData)
    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
  )

  if (!progress || !achievements) return <div>Error loading data</div>

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Progress Overview */}
      <div className="lg:col-span-2 bg-white rounded-lg shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Your Learning Journey</h2>
        
        {/* Level and Points */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-4 text-white">
            <div className="text-3xl font-bold">Level {achievements.level}</div>
            <div className="text-indigo-100">Current Level</div>
          </div>
          <div className="bg-gradient-to-r from-green-500 to-teal-600 rounded-lg p-4 text-white">
            <div className="text-3xl font-bold">{achievements.points}</div>
            <div className="text-green-100">Total Points</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress to Next Level</span>
            <span>{achievements.next_level_points} points to go</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-indigo-600 h-3 rounded-full transition-all duration-300"
              style={{ 
                width: `${Math.max(10, 100 - (achievements.next_level_points / 100) * 100)}%` 
              }}
            ></div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{achievements.stats.questions_answered}</div>
            <div className="text-sm text-gray-600">Questions</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{achievements.stats.current_streak}</div>
            <div className="text-sm text-gray-600">Current Streak</div>
          </div>
          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{achievements.stats.topics_studied}</div>
            <div className="text-sm text-gray-600">Topics Studied</div>
          </div>
          <div className="text-center p-3 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">{achievements.stats.days_active}</div>
            <div className="text-sm text-gray-600">Days Active</div>
          </div>
        </div>

        {/* Badges */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Your Badges ({achievements.badges.length})</h3>
          <div className="flex flex-wrap gap-3">
            {achievements.badges.length > 0 ? (
              achievements.badges.map((badge, idx) => (
                <div key={idx} className="bg-yellow-100 border border-yellow-300 rounded-lg p-3 text-center min-w-[120px]">
                  <div className="text-2xl mb-1">🏆</div>
                  <div className="font-semibold text-yellow-800 text-sm">{badge.name}</div>
                  <div className="text-xs text-yellow-600">{badge.description}</div>
                </div>
              ))
            ) : (
              <div className="text-gray-500 italic">No badges earned yet. Keep learning to unlock achievements!</div>
            )}
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className="space-y-6">
        {/* Leaderboard */}
        <div className="bg-white rounded-lg shadow-xl p-6">
          <h3 className="text-xl font-bold mb-4 text-gray-800">🏆 Leaderboard</h3>
          <div className="space-y-3">
            {leaderboard.map((student, idx) => (
              <div
                key={idx}
                className={`flex justify-between items-center p-3 rounded-lg transition-all ${
                  student.student_id === studentId 
                    ? 'bg-indigo-50 border-2 border-indigo-600 shadow-md' 
                    : 'bg-gray-50 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                    idx === 0 ? 'bg-yellow-400 text-yellow-900' :
                    idx === 1 ? 'bg-gray-300 text-gray-700' :
                    idx === 2 ? 'bg-orange-400 text-orange-900' :
                    'bg-gray-200 text-gray-600'
                  }`}>
                    {idx + 1}
                  </div>
                  <div>
                    <div className="font-semibold">
                      {student.student_id === studentId ? 'You' : `Student ${idx + 1}`}
                    </div>
                    <div className="text-xs text-gray-500">
                      Level {student.level} • {student.badges} badges
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-indigo-600">{student.points}</div>
                  <div className="text-xs text-gray-500">points</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Available Badges */}
        <div className="bg-white rounded-lg shadow-xl p-6">
          <h3 className="text-xl font-bold mb-4 text-gray-800">🎯 Next Goals</h3>
          <div className="space-y-3">
            {achievements.available_badges.slice(0, 3).map((badge, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded-lg border-l-4 border-indigo-500">
                <div className="font-semibold text-sm text-gray-800">{badge.name}</div>
                <div className="text-xs text-gray-600 mb-1">{badge.description}</div>
                <div className="text-xs text-indigo-600 font-medium">+{badge.points} points</div>
              </div>
            ))}
            {achievements.available_badges.length === 0 && (
              <div className="text-gray-500 italic text-sm">All badges earned! You're amazing! 🌟</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
