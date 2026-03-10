import { useState, useEffect } from 'react'
import LoadingSpinner from './LoadingSpinner'

export default function ProgressTracker({ studentId }) {
  const [analytics, setAnalytics] = useState(null)
  const [insights, setInsights] = useState(null)
  const [studyPlan, setStudyPlan] = useState(null)
  const [leaderboard, setLeaderboard] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [error, setError] = useState(null)

  useEffect(() => {
    if (studentId) {
      fetchProgressData()
    }
  }, [studentId])

  const fetchProgressData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch data with timeout and error handling
      const fetchWithTimeout = (url, timeout = 5000) => {
        return Promise.race([
          fetch(url),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Request timeout')), timeout)
          )
        ])
      }

      // Try to fetch analytics (optional)
      try {
        const analyticsResponse = await fetchWithTimeout(`http://localhost:8000/api/quiz/analytics/${studentId}`)
        if (analyticsResponse.ok) {
          const analyticsData = await analyticsResponse.json()
          setAnalytics(analyticsData)
        }
      } catch (error) {
        console.log('Analytics not available:', error.message)
        // Set default analytics
        setAnalytics({
          level: 1,
          total_points: 0,
          accuracy: 0,
          questions_answered: 0,
          correct_answers: 0,
          quizzes_completed: 0,
          current_streak: 0,
          study_streak: 0,
          badges: [],
          badges_earned: 0
        })
      }
      
      // Try to fetch leaderboard (optional)
      try {
        const leaderboardResponse = await fetchWithTimeout('http://localhost:8000/api/quiz/leaderboard')
        if (leaderboardResponse.ok) {
          const leaderboardData = await leaderboardResponse.json()
          setLeaderboard(leaderboardData.leaderboard || [])
        }
      } catch (error) {
        console.log('Leaderboard not available:', error.message)
        setLeaderboard([])
      }

      // Set default insights and study plan
      setInsights({
        motivation_message: "Welcome to your learning journey! 🌟",
        strengths: [],
        areas_for_improvement: [],
        recommendations: [
          "Start with beginner-level content",
          "Take regular quizzes to track progress",
          "Set daily learning goals"
        ],
        next_goals: ["Complete your first quiz", "Earn your first badge"]
      })

      setStudyPlan({
        weekly_focus: "Getting started with personalized learning",
        daily_goals: [
          "Complete at least one learning activity",
          "Spend 15-20 minutes studying",
          "Ask questions when confused"
        ],
        recommended_activities: [
          "Take a beginner quiz",
          "Explore different topics",
          "Use the chat feature for help"
        ],
        estimated_time: "15-30 minutes daily",
        difficulty_adjustment: "Start with beginner level"
      })
      
    } catch (error) {
      console.error('Error fetching progress data:', error)
      setError('Unable to load progress data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-xl p-6">
        <LoadingSpinner message="Loading your progress..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-xl p-6">
        <div className="text-center">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-red-600 mb-2">Loading Error</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchProgressData}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">📊 Learning Progress</h2>
        <button
          onClick={fetchProgressData}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
        >
          Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 mb-6">
        {['overview', 'insights', 'study-plan', 'leaderboard'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg capitalize ${
              activeTab === tab
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {tab.replace('-', ' ')}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && analytics && (
        <div>
          {/* Level and Points */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-6 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100">Current Level</p>
                  <p className="text-3xl font-bold">{analytics.level}</p>
                </div>
                <div className="text-4xl">🎯</div>
              </div>
            </div>
            
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white p-6 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100">Total Points</p>
                  <p className="text-3xl font-bold">{analytics.total_points}</p>
                </div>
                <div className="text-4xl">⭐</div>
              </div>
            </div>
            
            <div className="bg-gradient-to-r from-green-500 to-teal-500 text-white p-6 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100">Accuracy</p>
                  <p className="text-3xl font-bold">{analytics.accuracy}%</p>
                </div>
                <div className="text-4xl">🎯</div>
              </div>
            </div>
          </div>

          {/* Badges */}
          {analytics.badges && analytics.badges.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-4">🏅 Your Badges ({analytics.badges_earned})</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {analytics.badges.map((badge, index) => (
                  <div key={index} className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg text-center">
                    <div className="text-3xl mb-2">{badge.icon}</div>
                    <h4 className="font-semibold text-yellow-800">{badge.name}</h4>
                    <p className="text-xs text-yellow-600">{badge.description}</p>
                    <p className="text-sm font-bold text-yellow-700 mt-2">+{badge.points} pts</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">{analytics.questions_answered}</div>
              <div className="text-sm text-blue-600">Questions Answered</div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">{analytics.quizzes_completed}</div>
              <div className="text-sm text-green-600">Quizzes Completed</div>
            </div>
            
            <div className="bg-orange-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-orange-600">{analytics.current_streak}</div>
              <div className="text-sm text-orange-600">Current Streak</div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-purple-600">{analytics.study_streak}</div>
              <div className="text-sm text-purple-600">Study Streak (days)</div>
            </div>
          </div>
        </div>
      )}

      {/* Insights Tab */}
      {activeTab === 'insights' && insights && (
        <div className="space-y-6">
          {/* Motivation Message */}
          <div className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-6 rounded-lg">
            <h3 className="text-xl font-semibold mb-2">💪 Keep Going!</h3>
            <p>{insights.motivation_message}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            {insights.strengths && insights.strengths.length > 0 && (
              <div className="bg-green-50 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-green-800 mb-4">🌟 Your Strengths</h3>
                <div className="space-y-2">
                  {insights.strengths.map((strength, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-green-700">{strength.topic}</span>
                      <span className="text-green-600 font-semibold">{strength.mastery}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Areas for Improvement */}
            {insights.areas_for_improvement && insights.areas_for_improvement.length > 0 && (
              <div className="bg-orange-50 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-orange-800 mb-4">🎯 Focus Areas</h3>
                <div className="space-y-2">
                  {insights.areas_for_improvement.map((area, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-orange-700">{area.topic}</span>
                      <span className="text-orange-600 font-semibold">{area.mastery}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Recommendations */}
          {insights.recommendations && insights.recommendations.length > 0 && (
            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-800 mb-4">💡 Recommendations</h3>
              <ul className="space-y-2">
                {insights.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span className="text-blue-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Next Goals */}
          {insights.next_goals && insights.next_goals.length > 0 && (
            <div className="bg-purple-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-purple-800 mb-4">🎯 Next Goals</h3>
              <ul className="space-y-2">
                {insights.next_goals.map((goal, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-purple-600 mr-2">🎯</span>
                    <span className="text-purple-700">{goal}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Study Plan Tab */}
      {activeTab === 'study-plan' && studyPlan && (
        <div className="space-y-6">
          <div className="bg-indigo-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-indigo-800 mb-4">📅 Your Personalized Study Plan</h3>
            
            {/* Weekly Focus */}
            <div className="mb-6">
              <h4 className="font-semibold text-indigo-700 mb-2">This Week's Focus:</h4>
              <p className="text-indigo-600 bg-white p-3 rounded">{studyPlan.weekly_focus}</p>
            </div>

            {/* Daily Goals */}
            <div className="mb-6">
              <h4 className="font-semibold text-indigo-700 mb-2">Daily Goals:</h4>
              <ul className="space-y-2">
                {studyPlan.daily_goals.map((goal, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-indigo-600 mr-2">✓</span>
                    <span className="text-indigo-600">{goal}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Recommended Activities */}
            <div className="mb-6">
              <h4 className="font-semibold text-indigo-700 mb-2">Recommended Activities:</h4>
              <ul className="space-y-2">
                {studyPlan.recommended_activities.map((activity, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-indigo-600 mr-2">•</span>
                    <span className="text-indigo-600">{activity}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Time and Difficulty */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded">
                <h4 className="font-semibold text-indigo-700 mb-2">Estimated Time:</h4>
                <p className="text-indigo-600">{studyPlan.estimated_time}</p>
              </div>
              <div className="bg-white p-4 rounded">
                <h4 className="font-semibold text-indigo-700 mb-2">Difficulty Level:</h4>
                <p className="text-indigo-600">{studyPlan.difficulty_adjustment}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard Tab */}
      {activeTab === 'leaderboard' && (
        <div>
          <h3 className="text-lg font-semibold mb-4">🏆 Top Learners</h3>
          <div className="space-y-3">
            {leaderboard.map((student, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${
                    index === 0 ? 'bg-yellow-500' :
                    index === 1 ? 'bg-gray-400' :
                    index === 2 ? 'bg-orange-600' : 'bg-blue-500'
                  }`}>
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium">Student {student.student_id.slice(-4)}</p>
                    <p className="text-sm text-gray-600">Level {student.level} • {student.badges} badges</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg">{student.score}</p>
                  <p className="text-sm text-gray-600">points</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}