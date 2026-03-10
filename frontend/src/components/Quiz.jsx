import { useState, useEffect } from 'react'
import { generateQuiz, submitAnswer } from '../services/api'
import LoadingSpinner from './LoadingSpinner'

export default function Quiz({ studentId }) {
  const [topic, setTopic] = useState('')
  const [questions, setQuestions] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [quizResults, setQuizResults] = useState([])
  const [showResult, setShowResult] = useState(false)
  const [showFeedback, setShowFeedback] = useState(false)
  const [currentFeedback, setCurrentFeedback] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [startTime, setStartTime] = useState(null)

  const handleGenerateQuiz = async () => {
    if (!topic.trim()) return
    
    setLoading(true)
    try {
      const quiz = await generateQuiz(topic, 1, 10, studentId) // Minimum 10 questions
      setQuestions(quiz)
      setCurrentQuestion(0)
      setQuizResults([])
      setShowResult(false)
      setShowFeedback(false)
      setAnalysis(null)
      setStartTime(Date.now())
    } catch (error) {
      console.error('Error generating quiz:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (selectedAnswer === null) return

    setLoading(true)
    const questionStartTime = startTime || Date.now()
    const timeSpent = Math.floor((Date.now() - questionStartTime) / 1000)
    
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
        time_taken: timeSpent,
        points_earned: result.points_earned || 0,
        total_points: result.total_points || 0,
        new_badges: result.new_badges || [],
        level_up: result.level_up || false,
        current_streak: result.current_streak || 0,
        help: result.help || null
      }
      
      setQuizResults(prev => [...prev, questionResult])
      setCurrentFeedback(result)
      setShowFeedback(true)

    } catch (error) {
      console.error('Error submitting answer:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNextQuestion = () => {
    setShowFeedback(false)
    setCurrentFeedback(null)
    
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
      setSelectedAnswer(null)
      setStartTime(Date.now())
    } else {
      // Quiz completed - show final results
      setShowResult(true)
    }
  }

  // Render feedback for current answer
  const renderAnswerFeedback = () => {
    if (!currentFeedback) return null

    const isCorrect = currentFeedback.correct
    const hasHelp = currentFeedback.help && currentFeedback.show_explanation

    return (
      <div className="bg-white rounded-lg shadow-xl p-8">
        {/* Result Header */}
        <div className={`text-center mb-6 p-6 rounded-lg ${
          isCorrect ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          <div className="text-6xl mb-2">
            {isCorrect ? '✅' : '❌'}
          </div>
          <h2 className={`text-2xl font-bold mb-2 ${
            isCorrect ? 'text-green-800' : 'text-red-800'
          }`}>
            {isCorrect ? 'Correct!' : 'Not Quite Right'}
          </h2>
          <p className={`text-lg ${
            isCorrect ? 'text-green-600' : 'text-red-600'
          }`}>
            {isCorrect ? currentFeedback.encouragement : 'Let me help you understand this better'}
          </p>
        </div>

        {/* Points and Achievements */}
        {(currentFeedback.points_earned > 0 || currentFeedback.new_badges?.length > 0) && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-yellow-800">Rewards Earned:</span>
              <span className="text-yellow-600">+{currentFeedback.points_earned} points</span>
            </div>
            
            {currentFeedback.level_up && (
              <div className="mb-2 text-purple-600 font-semibold">
                🎉 Level Up! You reached a new level!
              </div>
            )}
            
            {currentFeedback.current_streak > 1 && (
              <div className="mb-2 text-orange-600">
                🔥 Streak: {currentFeedback.current_streak} correct answers in a row!
              </div>
            )}
            
            {currentFeedback.new_badges?.map((badge, index) => (
              <div key={index} className="flex items-center space-x-2 mb-2">
                <span className="text-2xl">{badge.icon}</span>
                <div>
                  <span className="font-semibold text-yellow-800">{badge.name}</span>
                  <p className="text-sm text-yellow-600">{badge.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Detailed Help for Wrong Answers */}
        {hasHelp && (
          <div className="space-y-6">
            {/* Encouragement */}
            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
              <p className="text-blue-800 font-medium">{currentFeedback.help.encouragement}</p>
            </div>

            {/* Explanation */}
            {currentFeedback.help.explanation && (
              <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">💡 Let me explain:</h3>
                <p className="text-gray-700">{currentFeedback.help.explanation}</p>
              </div>
            )}

            {/* Examples */}
            {currentFeedback.help.examples?.length > 0 && (
              <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-3">📚 Examples:</h3>
                <div className="space-y-2">
                  {currentFeedback.help.examples.map((example, index) => (
                    <div key={index} className="bg-white p-3 rounded border-l-4 border-green-400">
                      <p className="text-green-700 text-sm">{example}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Learning Resources */}
            {currentFeedback.help.resources?.length > 0 && (
              <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800 mb-3">🔗 Helpful Resources:</h3>
                <div className="space-y-2">
                  {currentFeedback.help.resources.map((resource, index) => (
                    <a
                      key={index}
                      href={resource.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block bg-white p-3 rounded border hover:shadow-sm transition-shadow"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-purple-700">{resource.title}</h4>
                          <p className="text-sm text-purple-600">{resource.type}</p>
                        </div>
                        <span className="text-purple-500">→</span>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Next Steps */}
            {currentFeedback.help.next_steps?.length > 0 && (
              <div className="bg-indigo-50 border border-indigo-200 p-4 rounded-lg">
                <h3 className="font-semibold text-indigo-800 mb-3">🎯 What to do next:</h3>
                <ul className="space-y-2">
                  {currentFeedback.help.next_steps.map((step, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-indigo-600 mr-2">•</span>
                      <span className="text-indigo-700 text-sm">{step}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Continue Button */}
        <div className="mt-8 text-center">
          <button
            onClick={handleNextQuestion}
            className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 font-semibold"
          >
            {currentQuestion === questions.length - 1 ? 'See Final Results' : 'Continue to Next Question'}
          </button>
        </div>
      </div>
    )
  }

  const renderQuizAnalysis = () => {
    const totalQuestions = quizResults.length
    const correctAnswers = quizResults.filter(r => r.correct).length
    const percentage = Math.round((correctAnswers / totalQuestions) * 100)
    const totalPoints = quizResults.reduce((sum, r) => sum + (r.points_earned || 0), 0)
    const allBadges = quizResults.flatMap(r => r.new_badges || [])

    return (
      <div className="bg-white rounded-lg shadow-xl p-8">
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold mb-2">🎉 Quiz Complete!</h2>
          <div className={`text-6xl font-bold mb-2 ${
            percentage >= 80 ? 'text-green-600' :
            percentage >= 60 ? 'text-blue-600' :
            percentage >= 40 ? 'text-yellow-600' :
            'text-red-600'
          }`}>
            {percentage}%
          </div>
          <div className={`text-xl font-semibold mb-2 ${
            percentage >= 80 ? 'text-green-600' :
            percentage >= 60 ? 'text-blue-600' :
            percentage >= 40 ? 'text-yellow-600' :
            'text-red-600'
          }`}>
            {percentage >= 80 ? 'Excellent!' :
             percentage >= 60 ? 'Good Job!' :
             percentage >= 40 ? 'Keep Practicing!' :
             'Need More Study'}
          </div>
          <p className="text-gray-600">
            {correctAnswers} out of {totalQuestions} questions correct
          </p>
          <p className="text-lg font-semibold text-indigo-600 mt-2">
            Total Points Earned: {totalPoints}
          </p>
        </div>

        {/* New Badges Earned */}
        {allBadges.length > 0 && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h3 className="text-lg font-semibold text-yellow-800 mb-3">🏅 New Badges Earned!</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {allBadges.map((badge, index) => (
                <div key={index} className="flex items-center space-x-3 bg-white p-3 rounded">
                  <span className="text-3xl">{badge.icon}</span>
                  <div>
                    <h4 className="font-semibold text-yellow-800">{badge.name}</h4>
                    <p className="text-sm text-yellow-600">{badge.description}</p>
                    <p className="text-xs text-yellow-500">+{badge.points} points</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-4 justify-center">
          <button
            onClick={() => {
              setQuestions([])
              setShowResult(false)
              setShowFeedback(false)
              setQuizResults([])
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
  }

  // Show answer feedback
  if (showFeedback && currentFeedback) {
    return renderAnswerFeedback()
  }

  // Show final results
  if (showResult) {
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
