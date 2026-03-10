import { useState, useEffect } from 'react'
import { generateQuiz, submitAnswer } from '../services/api'

export default function Quiz({ studentId }) {
  const [topic, setTopic] = useState('')
  const [questions, setQuestions] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [score, setScore] = useState(0)
  const [showResult, setShowResult] = useState(false)

  const handleGenerateQuiz = async () => {
    try {
      const quiz = await generateQuiz(topic, 1, 5)
      setQuestions(quiz)
      setCurrentQuestion(0)
      setScore(0)
      setShowResult(false)
    } catch (error) {
      console.error('Error generating quiz:', error)
    }
  }

  const handleSubmit = async () => {
    if (selectedAnswer === null) return

    try {
      const result = await submitAnswer(
        questions[currentQuestion].id,
        studentId,
        selectedAnswer
      )
      
      if (result.correct) setScore(score + 1)

      if (currentQuestion < questions.length - 1) {
        setCurrentQuestion(currentQuestion + 1)
        setSelectedAnswer(null)
      } else {
        setShowResult(true)
      }
    } catch (error) {
      console.error('Error submitting answer:', error)
    }
  }

  if (showResult) {
    return (
      <div className="bg-white rounded-lg shadow-xl p-8 text-center">
        <h2 className="text-3xl font-bold mb-4">Quiz Complete!</h2>
        <p className="text-xl mb-6">Your Score: {score}/{questions.length}</p>
        <button
          onClick={() => setQuestions([])}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
        >
          Take Another Quiz
        </button>
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-xl p-8">
        <h2 className="text-2xl font-bold mb-4">Generate Quiz</h2>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter topic (e.g., Mathematics, History)"
          className="w-full border rounded-lg px-4 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-indigo-600"
        />
        <button
          onClick={handleGenerateQuiz}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
        >
          Generate Quiz
        </button>
      </div>
    )
  }

  const question = questions[currentQuestion]

  return (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <div className="mb-6">
        <span className="text-sm text-gray-500">Question {currentQuestion + 1} of {questions.length}</span>
        <h2 className="text-2xl font-bold mt-2">{question.question}</h2>
      </div>

      <div className="space-y-3 mb-6">
        {question.options.map((option, idx) => (
          <button
            key={idx}
            onClick={() => setSelectedAnswer(idx)}
            className={`w-full text-left p-4 rounded-lg border-2 transition ${
              selectedAnswer === idx
                ? 'border-indigo-600 bg-indigo-50'
                : 'border-gray-200 hover:border-indigo-300'
            }`}
          >
            {option}
          </button>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={selectedAnswer === null}
        className="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 disabled:bg-gray-300"
      >
        Submit Answer
      </button>
    </div>
  )
}
