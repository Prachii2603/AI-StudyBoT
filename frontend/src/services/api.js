import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const sendMessage = async (message, studentId, difficultyLevel) => {
  const response = await api.post('/chat/message', {
    message,
    student_id: studentId,
    difficulty_level: difficultyLevel,
  })
  return response.data
}

export const generateQuiz = async (topic, difficulty, count) => {
  const response = await api.get(`/quiz/generate/${topic}`, {
    params: { difficulty, count },
  })
  return response.data
}

export const submitAnswer = async (questionId, studentId, answer) => {
  const response = await api.post('/quiz/submit', {
    question_id: questionId,
    student_id: studentId,
    answer,
  })
  return response.data
}

export const getProgress = async (studentId) => {
  const response = await api.get(`/progress/${studentId}`)
  return response.data
}

export const getLeaderboard = async () => {
  const response = await api.get('/progress/leaderboard')
  return response.data
}

export default api
