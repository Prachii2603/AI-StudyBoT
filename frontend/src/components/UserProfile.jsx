import { useState, useEffect } from 'react'
import { getCurrentUser } from '../services/api'

export default function UserProfile({ user }) {
  const [profile, setProfile] = useState(user)
  const [loading, setLoading] = useState(false)

  const refreshProfile = async () => {
    setLoading(true)
    try {
      const updatedProfile = await getCurrentUser()
      setProfile(updatedProfile)
    } catch (error) {
      console.error('Error refreshing profile:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">👤 User Profile</h2>
        <button
          onClick={refreshProfile}
          disabled={loading}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400"
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Basic Information */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">Basic Information</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-600">Name</label>
            <p className="text-lg text-gray-800">{profile.name}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Email</label>
            <p className="text-lg text-gray-800">{profile.email}</p>
          </div>

          {profile.age && (
            <div>
              <label className="block text-sm font-medium text-gray-600">Age</label>
              <p className="text-lg text-gray-800">{profile.age} years old</p>
            </div>
          )}

          {profile.grade && (
            <div>
              <label className="block text-sm font-medium text-gray-600">Grade/Level</label>
              <p className="text-lg text-gray-800 capitalize">{profile.grade}</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-600">Member Since</label>
            <p className="text-lg text-gray-800">
              {new Date(profile.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Learning Information */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">Learning Profile</h3>
          
          {profile.interests && profile.interests.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">Learning Interests</label>
              <div className="flex flex-wrap gap-2">
                {profile.interests.map((interest, index) => (
                  <span
                    key={index}
                    className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm"
                  >
                    {interest}
                  </span>
                ))}
              </div>
            </div>
          )}

          {profile.learning_profile && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-600">Total Sessions</label>
                <p className="text-lg text-gray-800">{profile.learning_profile.total_sessions}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600">Questions Answered</label>
                <p className="text-lg text-gray-800">{profile.learning_profile.total_questions_answered}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600">Average Score</label>
                <p className="text-lg text-gray-800">
                  {Math.round(profile.learning_profile.average_score * 100)}%
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600">Preferred Difficulty</label>
                <div className="flex items-center space-x-2">
                  {[1, 2, 3].map((level) => (
                    <div
                      key={level}
                      className={`w-4 h-4 rounded-full ${
                        level <= profile.learning_profile.preferred_difficulty
                          ? 'bg-indigo-600'
                          : 'bg-gray-300'
                      }`}
                    />
                  ))}
                  <span className="text-sm text-gray-600 ml-2">
                    {profile.learning_profile.preferred_difficulty === 1 && 'Beginner'}
                    {profile.learning_profile.preferred_difficulty === 2 && 'Intermediate'}
                    {profile.learning_profile.preferred_difficulty === 3 && 'Advanced'}
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600">Learning Style</label>
                <p className="text-lg text-gray-800 capitalize">
                  {profile.learning_profile.learning_style}
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg text-center">
          <div className="text-2xl font-bold text-blue-600">
            {profile.learning_profile?.total_sessions || 0}
          </div>
          <div className="text-sm text-blue-600">Learning Sessions</div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg text-center">
          <div className="text-2xl font-bold text-green-600">
            {profile.learning_profile?.total_questions_answered || 0}
          </div>
          <div className="text-sm text-green-600">Questions Answered</div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg text-center">
          <div className="text-2xl font-bold text-purple-600">
            {Math.round((profile.learning_profile?.average_score || 0) * 100)}%
          </div>
          <div className="text-sm text-purple-600">Average Score</div>
        </div>
      </div>

      {/* Tips */}
      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h4 className="font-medium text-yellow-800 mb-2">💡 Learning Tips</h4>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• Try different difficulty levels to challenge yourself</li>
          <li>• Take quizzes regularly to track your progress</li>
          <li>• Play educational games to make learning fun</li>
          <li>• Ask the AI tutor questions about topics you're curious about</li>
        </ul>
      </div>
    </div>
  )
}