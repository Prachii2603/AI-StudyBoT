import { useState, useEffect } from 'react'
import { getProgress, getLeaderboard } from '../services/api'

export default function Dashboard({ studentId }) {
  const [progress, setProgress] = useState(null)
  const [leaderboard, setLeaderboard] = useState([])

  useEffect(() => {
    loadData()
  }, [studentId])

  const loadData = async () => {
    try {
      const progressData = await getProgress(studentId)
      const leaderboardData = await getLeaderboard()
      setProgress(progressData)
      setLeaderboard(leaderboardData)
    } catch (error) {
      console.error('Error loading dashboard:', error)
    }
  }

  if (!progress) return <div>Loading...</div>

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white rounded-lg shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-4">Your Progress</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Level</span>
            <span className="text-3xl font-bold text-indigo-600">{progress.level}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Total Points</span>
            <span className="text-2xl font-semibold">{progress.points}</span>
          </div>
          <div>
            <span className="text-gray-600 block mb-2">Badges</span>
            <div className="flex flex-wrap gap-2">
              {progress.badges.length > 0 ? (
                progress.badges.map((badge, idx) => (
                  <span key={idx} className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
                    🏆 {badge}
                  </span>
                ))
              ) : (
                <span className="text-gray-400">No badges yet</span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-4">Leaderboard</h2>
        <div className="space-y-3">
          {leaderboard.map((student, idx) => (
            <div
              key={idx}
              className={`flex justify-between items-center p-3 rounded-lg ${
                student.student_id === studentId ? 'bg-indigo-50 border-2 border-indigo-600' : 'bg-gray-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-xl font-bold text-gray-400">#{idx + 1}</span>
                <span className="font-semibold">
                  {student.student_id === studentId ? 'You' : `Student ${idx + 1}`}
                </span>
              </div>
              <div className="text-right">
                <div className="font-bold text-indigo-600">{student.points} pts</div>
                <div className="text-sm text-gray-500">Level {student.level}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
