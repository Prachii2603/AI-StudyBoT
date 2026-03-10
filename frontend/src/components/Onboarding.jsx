import { useState } from 'react'
import { registerStudent, assessLearningStyle, generateDiagnosticQuiz, submitDiagnosticResults } from '../services/api'

export default function Onboarding({ onComplete }) {
  const [step, setStep] = useState(1)
  const [studentData, setStudentData] = useState({})
  const [loading, setLoading] = useState(false)

  const handleRegistration = async (formData) => {
    setLoading(true)
    try {
      const result = await registerStudent(formData)
      setStudentData(result)
      setStep(2)
    } catch (error) {
      console.error('Registration failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLearningStyleAssessment = async (responses) => {
    setLoading(true)
    try {
      const result = await assessLearningStyle(studentData.student_id, responses)
      setStudentData(prev => ({ ...prev, ...result }))
      setStep(3)
    } catch (error) {
      console.error('Learning style assessment failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDiagnosticQuiz = async (responses) => {
    setLoading(true)
    try {
      const result = await submitDiagnosticResults(studentData.student_id, responses)
      setStudentData(prev => ({ ...prev, ...result }))
      onComplete(studentData)
    } catch (error) {
      console.error('Diagnostic quiz failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-gray-800">Welcome to AI Learning Platform</h1>
          <div className="text-sm text-gray-500">Step {step} of 3</div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-indigo-600 h-2 rounded-full transition-all duration-300" style={{ width: `${(step / 3) * 100}%` }}></div>
        </div>
      </div>

      {step === 1 && <RegistrationStep onNext={handleRegistration} loading={loading} />}
      {step === 2 && <LearningStyleStep onNext={handleLearningStyleAssessment} loading={loading} />}
      {step === 3 && <DiagnosticQuizStep onNext={handleDiagnosticQuiz} loading={loading} studentId={studentData.student_id} />}
    </div>
  )
}

function RegistrationStep({ onNext, loading }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    age_group: 'adult',
    learning_goals: [],
    preferred_subjects: []
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onNext(formData)
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <h2 className="text-2xl font-bold mb-6">Let's Get Started</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Name *</label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Email (Optional)</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Age Group</label>
          <select
            value={formData.age_group}
            onChange={(e) => setFormData(prev => ({ ...prev, age_group: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="child">Child (Under 13)</option>
            <option value="teen">Teen (13-17)</option>
            <option value="adult">Adult (18+)</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading || !formData.name}
          className="w-full bg-indigo-600 text-white py-3 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Creating Profile...' : 'Continue'}
        </button>
      </form>
    </div>
  )
}

function LearningStyleStep({ onNext, loading }) {
  const [responses, setResponses] = useState({})

  const questions = [
    { id: 'prefer_diagrams', text: 'Do you prefer learning through diagrams and visual aids?' },
    { id: 'prefer_lectures', text: 'Do you learn best by listening to lectures or audio content?' },
    { id: 'prefer_hands_on', text: 'Do you prefer hands-on activities and practical exercises?' },
    { id: 'remember_faces', text: 'Do you easily remember faces but forget names?' },
    { id: 'learn_by_reading', text: 'Do you prefer to learn by reading text and written materials?' }
  ]

  const handleResponse = (questionId, answer) => {
    setResponses(prev => ({ ...prev, [questionId]: answer }))
  }

  const handleSubmit = () => {
    onNext(responses)
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <h2 className="text-2xl font-bold mb-6">Learning Style Assessment</h2>
      <p className="text-gray-600 mb-8">Help us understand how you learn best by answering these questions.</p>
      
      <div className="space-y-6">
        {questions.map((question) => (
          <div key={question.id} className="border-b border-gray-200 pb-4">
            <p className="text-lg mb-3">{question.text}</p>
            <div className="flex gap-4">
              <button
                onClick={() => handleResponse(question.id, 'yes')}
                className={`px-6 py-2 rounded-md ${
                  responses[question.id] === 'yes'
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Yes
              </button>
              <button
                onClick={() => handleResponse(question.id, 'no')}
                className={`px-6 py-2 rounded-md ${
                  responses[question.id] === 'no'
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                No
              </button>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading || Object.keys(responses).length < questions.length}
        className="w-full mt-8 bg-indigo-600 text-white py-3 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50"
      >
        {loading ? 'Analyzing...' : 'Continue to Assessment'}
      </button>
    </div>
  )
}

function DiagnosticQuizStep({ onNext, loading, studentId }) {
  const [quizData, setQuizData] = useState(null)
  const [responses, setResponses] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(0)

  // Mock diagnostic quiz - in real implementation, fetch from API
  const mockQuiz = [
    {
      id: 'py_1',
      question: 'What keyword is used to define a function in Python?',
      options: ['func', 'def', 'function', 'define'],
      correct_answer: 1,
      topic: 'python'
    },
    {
      id: 'ml_1',
      question: 'What is supervised learning?',
      options: ['Learning without labels', 'Learning with labeled data', 'Learning through rewards', 'Learning by trial'],
      correct_answer: 1,
      topic: 'machine learning'
    }
  ]

  const handleAnswer = (answerIndex) => {
    const question = mockQuiz[currentQuestion]
    const isCorrect = answerIndex === question.correct_answer
    
    const response = {
      question_id: question.id,
      topic: question.topic,
      is_correct: isCorrect,
      selected_answer: answerIndex,
      response_time: 30.0
    }
    
    setResponses(prev => [...prev, response])
    
    if (currentQuestion < mockQuiz.length - 1) {
      setCurrentQuestion(prev => prev + 1)
    } else {
      onNext(responses.concat([response]))
    }
  }

  if (currentQuestion >= mockQuiz.length) {
    return (
      <div className="bg-white rounded-lg shadow-xl p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
        <p className="text-lg">Processing your results...</p>
      </div>
    )
  }

  const question = mockQuiz[currentQuestion]

  return (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Diagnostic Assessment</h2>
          <span className="text-sm text-gray-500">
            Question {currentQuestion + 1} of {mockQuiz.length}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentQuestion + 1) / mockQuiz.length) * 100}%` }}
          ></div>
        </div>
      </div>

      <div className="mb-8">
        <h3 className="text-xl font-semibold mb-6">{question.question}</h3>
        <div className="space-y-3">
          {question.options.map((option, index) => (
            <button
              key={index}
              onClick={() => handleAnswer(index)}
              className="w-full text-left p-4 border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-indigo-500 transition-colors"
            >
              <span className="font-medium mr-3">{String.fromCharCode(65 + index)}.</span>
              {option}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}