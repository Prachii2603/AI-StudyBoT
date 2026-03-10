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

export const generateQuiz = async (topic, difficulty, count, studentId = null) => {
  const response = await api.get(`/quiz/generate/${topic}`, {
    params: { difficulty, count, student_id: studentId },
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

export const analyzeQuizPerformance = async (quizResults, studentId) => {
  const response = await api.post('/chat/quiz-analysis', quizResults, {
    params: { student_id: studentId }
  })
  return response.data
}

export const getProgress = async (studentId) => {
  const response = await api.get(`/progress/${studentId}`)
  return response.data
}

export const getAchievements = async (studentId) => {
  const response = await api.get(`/progress/${studentId}/achievements`)
  return response.data
}

export const getLeaderboard = async () => {
  const response = await api.get('/progress/leaderboard')
  return response.data
}

export const getLearningRecommendations = async (studentId) => {
  const response = await api.get(`/chat/recommendations/${studentId}`)
  return response.data
}

export const getChatStudentProfile = async (studentId) => {
  const response = await api.get(`/chat/profile/${studentId}`)
  return response.data
}

export const completeQuiz = async (studentId, score, totalQuestions) => {
  const response = await api.post(`/progress/${studentId}/quiz-complete`, null, {
    params: { score, total_questions: totalQuestions }
  })
  return response.data
}

// Games API
export const getAvailableGames = async () => {
  const response = await api.get('/games/available')
  return response.data
}

export const startWordMatchGame = async (topic, studentId) => {
  const response = await api.post('/games/word-match/start', {
    topic,
    student_id: studentId
  })
  return response.data
}

export const makeWordMatch = async (gameId, term, definition) => {
  const response = await api.post('/games/word-match/match', {
    game_id: gameId,
    term,
    definition
  })
  return response.data
}

export const startLightningQuiz = async (topic, studentId) => {
  const response = await api.post('/games/lightning-quiz/start', {
    topic,
    student_id: studentId
  })
  return response.data
}

export const answerLightningQuestion = async (gameId, answer) => {
  const response = await api.post('/games/lightning-quiz/answer', {
    game_id: gameId,
    answer
  })
  return response.data
}

export const startMemoryCardsGame = async (topic, studentId) => {
  const response = await api.post('/games/memory-cards/start', {
    topic,
    student_id: studentId
  })
  return response.data
}

export const flipMemoryCard = async (gameId, cardId) => {
  const response = await api.post('/games/memory-cards/flip', {
    game_id: gameId,
    card_id: cardId
  })
  return response.data
}

export const getGameLeaderboard = async (gameType) => {
  const response = await api.get(`/games/leaderboard/${gameType}`)
  return response.data
}

// Onboarding API
export const registerStudent = async (registrationData) => {
  const response = await api.post('/onboarding/register', registrationData)
  return response.data
}

export const getLearningStyleQuestionnaire = async () => {
  const response = await api.get('/onboarding/learning-style-questionnaire')
  return response.data
}

export const assessLearningStyle = async (studentId, responses) => {
  const response = await api.post('/onboarding/assess-learning-style', {
    student_id: studentId,
    responses
  })
  return response.data
}

export const generateDiagnosticQuiz = async (studentId, topics) => {
  const response = await api.post('/onboarding/generate-diagnostic-quiz', {
    student_id: studentId,
    topics,
    questions_per_topic: 3
  })
  return response.data
}

export const submitDiagnosticResults = async (studentId, responses) => {
  const response = await api.post('/onboarding/submit-diagnostic-results', {
    student_id: studentId,
    responses
  })
  return response.data
}

export const getStudentProfile = async (studentId) => {
  const response = await api.get(`/onboarding/student-profile/${studentId}`)
  return response.data
}

export default api
