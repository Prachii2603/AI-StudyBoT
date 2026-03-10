import { useState } from 'react'
import { login, register } from '../services/api'

export default function Login({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    age: '',
    grade: '',
    interests: []
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const interests = [
    'Mathematics', 'Science', 'Programming', 'Machine Learning',
    'Physics', 'Chemistry', 'Biology', 'History', 'Literature', 'Art'
  ]

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    
    if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        interests: checked 
          ? [...prev.interests, value]
          : prev.interests.filter(interest => interest !== value)
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (!isLogin) {
        // Registration validation
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match')
          setLoading(false)
          return
        }
        if (formData.password.length < 6) {
          setError('Password must be at least 6 characters')
          setLoading(false)
          return
        }
        if (!formData.name || !formData.email) {
          setError('Name and email are required')
          setLoading(false)
          return
        }
      }

      const response = isLogin 
        ? await login(formData.email, formData.password)
        : await register(formData)

      if (response.success) {
        // Store user data in localStorage
        localStorage.setItem('user', JSON.stringify(response.user))
        localStorage.setItem('token', response.token)
        onLogin(response.user)
      } else {
        setError(response.message || 'Authentication failed')
      }
    } catch (error) {
      console.error('Auth error:', error)
      setError(error.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const toggleMode = () => {
    setIsLogin(!isLogin)
    setError('')
    setFormData({
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      age: '',
      grade: '',
      interests: []
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-cyan-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-4xl mb-4">🤖</div>
          <h1 className="text-2xl font-bold text-gray-800">AI StudyBot</h1>
          <p className="text-gray-600 mt-2">
            {isLogin ? 'Welcome back!' : 'Start your learning journey'}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name (Registration only) */}
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Enter your full name"
                required={!isLogin}
              />
            </div>
          )}

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address *
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your email"
              required
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password *
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your password"
              required
            />
          </div>

          {/* Confirm Password (Registration only) */}
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password *
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Confirm your password"
                required={!isLogin}
              />
            </div>
          )}

          {/* Additional Registration Fields */}
          {!isLogin && (
            <>
              {/* Age and Grade */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Age
                  </label>
                  <input
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Age"
                    min="5"
                    max="100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Grade/Level
                  </label>
                  <select
                    name="grade"
                    value={formData.grade}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="">Select Grade</option>
                    <option value="elementary">Elementary</option>
                    <option value="middle">Middle School</option>
                    <option value="high">High School</option>
                    <option value="college">College</option>
                    <option value="graduate">Graduate</option>
                    <option value="professional">Professional</option>
                  </select>
                </div>
              </div>

              {/* Learning Interests */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Learning Interests (Select all that apply)
                </label>
                <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                  {interests.map(interest => (
                    <label key={interest} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        value={interest}
                        checked={formData.interests.includes(interest)}
                        onChange={handleChange}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="text-sm text-gray-700">{interest}</span>
                    </label>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                {isLogin ? 'Signing In...' : 'Creating Account...'}
              </div>
            ) : (
              isLogin ? 'Sign In' : 'Create Account'
            )}
          </button>
        </form>

        {/* Toggle Mode */}
        <div className="mt-6 text-center">
          <p className="text-gray-600">
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            <button
              onClick={toggleMode}
              className="ml-2 text-indigo-600 hover:text-indigo-700 font-medium"
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
        </div>

        {/* Demo Account */}
        {isLogin && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-600 text-center">
              Demo Account: demo@example.com / password123
            </p>
          </div>
        )}
      </div>
    </div>
  )
}