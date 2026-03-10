import { useState, useEffect } from 'react'
import { generateQuiz, submitAnswer, analyzeQuizPerformance } from '../services/api'

export default function Quiz({ studentId }) {
  const [topic, setTopic] = useState('')
  const [questions, setQuestions] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [quizResults, setQuizResults] = useState([])
  const [showResult, setShowResult] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleGenerateQuiz = async () => {
    if (!topic.trim()) return
    
    setLoading(true)
    try {
      const quiz = await generateQuiz(topic, 1, 10, studentId) // Minimum 10 questions
      setQuestions(quiz)
      setCurrentQuestion(0)
      setQuizResults([])
      setShowResult(false)
      setAnalysis(null)
    } catch (error) {
      console.error('Error generating quiz:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (selectedAnswer === null) return

    setLoading(true)
    try {
      const result = await submitAnswer(
        questions[currentQuestion].id,
        studentId,
        selectedAnswer
      )
      
      // Store result for analysis
      const questionResult = {
        question_id: questions[currentQuestion].id,
        question: questions[currentQuestion].question,
        correct: result.correct,
        selected_answer: selectedAnswer,
        correct_answer: questions[currentQuestion].correct_answer,
        explanation: result.explanation
      }
      
      setQuizResults(prev => [...prev, questionResult])

      if (currentQuestion < questions.length - 1) {
        setCurrentQuestion(currentQuestion + 1)
        setSelectedAnswer(null)
      } else {
        // Quiz completed - analyze performance
        const allResults = [...quizResults, questionResult]
        const analysisResult = await analyzeQuizPerformance(allResults, studentId)
        setAnalysis(analysisResult)
        setShowResult(true)
      }
    } catch (error) {
      console.error('Error submitting answer:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderQuizAnalysis = () => (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <div className="text-center mb-6">
        <h2 className="text-3xl font-bold mb-2">📊 Quiz Analysis</h2>
        <div className={`text-6xl font-bold mb-2 ${
          analysis.performance_level.color === 'green' ? 'text-green-600' :
          analysis.performance_level.color === 'blue' ? 'text-blue-600' :
          analysis.performance_level.color === 'yellow' ? 'text-yellow-600' :
          analysis.performance_level.color === 'orange' ? 'text-orange-600' :
          'text-red-600'
        }`}>
          {analysis.score.percentage}%
        </div>
        <div className={`text-xl font-semibold mb-2 ${
          analysis.performance_level.color === 'green' ? 'text-green-600' :
          analysis.performance_level.color === 'blue' ? 'text-blue-600' :
          analysis.performance_level.color === 'yellow' ? 'text-yellow-600' :
          analysis.performance_level.color === 'orange' ? 'text-orange-600' :
          'text-red-600'
        }`}>
          {analysis.performance_level.level}
        </div>
        <p className="text-gray-600">{analysis.performance_level.description}</p>
        <p className="text-sm text-gray-500 mt-2">
          {analysis.score.correct} out of {analysis.score.total} questions correct
        </p>
      </div>

      {/* Weak Concepts */}
      {analysis.weak_concepts.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-red-600">🎯 Areas for Improvement</h3>
          <div className="space-y-3">
            {analysis.weak_concepts.map((concept, idx) => (
              <div key={idx} className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-medium text-red-800">{concept.concept}</h4>
                  <span className="text-sm text-red-600">
                    {Math.round(concept.accuracy * 100)}% accuracy
                  </span>
                </div>
                <p className="text-sm text-red-700">
                  You missed {concept.questions_missed} out of {concept.total_questions} questions in this area.
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strong Concepts */}
      {analysis.strong_concepts.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-green-600">💪 Your Strengths</h3>
          <div className="space-y-3">
            {analysis.strong_concepts.map((concept, idx) => (
              <div key={idx} className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-medium text-green-800">{concept.concept}</h4>
                  <span className="text-sm text-green-600">
                    {Math.round(concept.accuracy * 100)}% accuracy
                  </span>
                </div>
                <p className="text-sm text-green-700">
                  Great job! You got {concept.questions_correct} out of {concept.total_questions} questions right.
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">📚 Study Recommendations</h3>
          <div className="space-y-3">
            {analysis.recommendations.map((rec, idx) => (
              <div key={idx} className={`border rounded-lg p-4 ${
                rec.type === 'improvement' ? 'bg-blue-50 border-blue-200' : 'bg-purple-50 border-purple-200'
              }`}>
                <h4 className={`font-medium mb-2 ${
                  rec.type === 'improvement' ? 'text-blue-800' : 'text-purple-800'
                }`}>
                  {rec.title}
                </h4>
                <p className={`text-sm mb-2 ${
                  rec.type === 'improvement' ? 'text-blue-700' : 'text-purple-700'
                }`}>
                  {rec.description}
                </p>
                <p className={`text-sm font-medium ${
                  rec.type === 'improvement' ? 'text-blue-600' : 'text-purple-600'
                }`}>
                  💡 {rec.action}
                </p>
                
                {/* Learning Resources */}
                {rec.resources && rec.resources.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-xs font-medium text-gray-600">Recommended Resources:</p>
                    {rec.resources.map((resource, resIdx) => (
                      <a
                        key={resIdx}
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block text-xs bg-white border rounded p-2 hover:shadow-sm transition-shadow"
                      >
                        <div className="font-medium text-blue-600">{resource.title}</div>
                        <div className="text-gray-600">{resource.description}</div>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Next Steps */}
      {analysis.next_steps.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">🚀 Next Steps</h3>
          <div className="bg-gray-50 border rounded-lg p-4">
            <ul className="space-y-2">
              {analysis.next_steps.map((step, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-start">
                  <span className="mr-2">•</span>
                  <span>{step}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div className="flex gap-4 justify-center">
        <button
          onClick={() => {
            setQuestions([])
            setShowResult(false)
            setAnalysis(null)
            setTopic('')
          }}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
        >
          Take Another Quiz
        </button>
        <button
          onClick={() => handleGenerateQuiz()}
          className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
        >
          Retake This Quiz
        </button>
      </div>
    </div>
  )

  if (showResult && analysis) {
    return renderQuizAnalysis()
  }

  if (questions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-xl p-8">
        <h2 className="text-2xl font-bold mb-6 text-center">📝 Enhanced Quiz System</h2>
        <div className="max-w-md mx-auto">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter a topic for your quiz (minimum 10 questions):
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Machine Learning, Python Programming, Mathematics"
              className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-600"
            />
          </div>
          <button
            onClick={handleGenerateQuiz}
            disabled={loading || !topic.trim()}
            className="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating Quiz...' : 'Generate Quiz (10 Questions)'}
          </button>
          
          <div className="mt-6 text-sm text-gray-600">
            <h3 className="font-medium mb-2">✨ Enhanced Features:</h3>
            <ul className="space-y-1 text-xs">
              <li>• Minimum 10 comprehensive questions</li>
              <li>• Detailed performance analysis</li>
              <li>• Weak concept identification</li>
              <li>• Personalized study recommendations</li>
              <li>• Learning resource links</li>
              <li>• Progress tracking and insights</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }

  const question = questions[currentQuestion]
  const progress = ((currentQuestion + 1) / questions.length) * 100

  return (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-500">
            Question {currentQuestion + 1} of {questions.length}
          </span>
          <span className="text-sm text-gray-500">{Math.round(progress)}% Complete</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-bold mb-4">{question.question}</h2>
        <div className="space-y-3">
          {question.options.map((option, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedAnswer(idx)}
              className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                selectedAnswer === idx
                  ? 'border-indigo-600 bg-indigo-50'
                  : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center">
                <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                  selectedAnswer === idx
                    ? 'border-indigo-600 bg-indigo-600'
                    : 'border-gray-300'
                }`}>
                  {selectedAnswer === idx && (
                    <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5"></div>
                  )}
                </div>
                {option}
              </div>
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={selectedAnswer === null || loading}
        className="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {loading ? 'Processing...' : currentQuestion === questions.length - 1 ? 'Complete Quiz' : 'Next Question'}
      </button>
    </div>
  )
}
