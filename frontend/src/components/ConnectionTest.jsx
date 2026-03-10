import { useState } from 'react'
import { sendMessage } from '../services/api'

export default function ConnectionTest() {
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const testConnection = async () => {
    setLoading(true)
    setError('')
    setResponse('')
    
    try {
      console.log('Testing connection...')
      const result = await sendMessage('Hello, test connection', 'test-user', 1)
      console.log('Connection test result:', result)
      
      // Handle both old and new response formats
      const content = result.content || result || 'Connection successful!'
      setResponse(content)
    } catch (err) {
      console.error('Connection test error:', err)
      setError(err.message || 'Connection failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">🔗 Connection Test</h2>
      
      <button
        onClick={testConnection}
        disabled={loading}
        className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 mb-4"
      >
        {loading ? 'Testing...' : 'Test Backend Connection'}
      </button>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong>Error:</strong> {error}
        </div>
      )}

      {response && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          <strong>✅ Success!</strong>
          <p className="mt-2 whitespace-pre-wrap">{response}</p>
        </div>
      )}

      <div className="mt-4 text-sm text-gray-600">
        <p><strong>Backend URL:</strong> http://localhost:8000</p>
        <p><strong>Frontend URL:</strong> http://localhost:3000</p>
        <p><strong>Status:</strong> {loading ? 'Testing...' : error ? 'Error' : response ? 'Connected' : 'Ready to test'}</p>
      </div>
    </div>
  )
}