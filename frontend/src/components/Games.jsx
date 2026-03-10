import { useState, useEffect } from 'react'
import { getAvailableGames, startWordMatchGame, makeWordMatch, startLightningQuiz, answerLightningQuestion, startMemoryCardsGame, flipMemoryCard } from '../services/api'

export default function Games({ studentId }) {
  const [availableGames, setAvailableGames] = useState([])
  const [activeGame, setActiveGame] = useState(null)
  const [gameData, setGameData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedTopic, setSelectedTopic] = useState('machine learning')

  useEffect(() => {
    loadAvailableGames()
  }, [])

  const loadAvailableGames = async () => {
    try {
      const games = await getAvailableGames()
      setAvailableGames(games)
    } catch (error) {
      console.error('Error loading games:', error)
    }
  }

  const startGame = async (gameType) => {
    setLoading(true)
    try {
      let gameResponse
      switch (gameType) {
        case 'word-match':
          gameResponse = await startWordMatchGame(selectedTopic, studentId)
          break
        case 'lightning-quiz':
          gameResponse = await startLightningQuiz(selectedTopic, studentId)
          break
        case 'memory-cards':
          gameResponse = await startMemoryCardsGame(selectedTopic, studentId)
          break
        default:
          throw new Error('Unknown game type')
      }
      
      setActiveGame(gameType)
      setGameData(gameResponse)
    } catch (error) {
      console.error('Error starting game:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleWordMatch = async (term, definition) => {
    try {
      const result = await makeWordMatch(gameData.game_id, term, definition)
      if (result.game_completed) {
        alert(`Game Complete! Final Score: ${result.final_score}`)
        setActiveGame(null)
        setGameData(null)
      } else {
        // Update UI based on result
        console.log(result)
      }
    } catch (error) {
      console.error('Error making match:', error)
    }
  }

  const handleLightningAnswer = async (answer) => {
    try {
      const result = await answerLightningQuestion(gameData.game_id, answer)
      if (result.game_completed) {
        alert(`Game Complete! Score: ${result.final_score}, Accuracy: ${result.accuracy}%`)
        setActiveGame(null)
        setGameData(null)
      } else {
        setGameData(prev => ({ ...prev, ...result }))
      }
    } catch (error) {
      console.error('Error answering question:', error)
    }
  }

  const handleCardFlip = async (cardId) => {
    try {
      const result = await flipMemoryCard(gameData.game_id, cardId)
      if (result.game_completed) {
        alert(`Game Complete! Score: ${result.final_score}, Moves: ${result.moves}`)
        setActiveGame(null)
        setGameData(null)
      } else {
        // Update card states
        console.log(result)
      }
    } catch (error) {
      console.error('Error flipping card:', error)
    }
  }

  const renderGameSelection = () => (
    <div className="bg-white rounded-lg shadow-xl p-6">
      <h2 className="text-2xl font-bold mb-6 text-center">🎮 Educational Games</h2>
      
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Choose a topic for your games:
        </label>
        <select
          value={selectedTopic}
          onChange={(e) => setSelectedTopic(e.target.value)}
          className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-600"
        >
          <option value="machine learning">Machine Learning</option>
          <option value="programming">Programming</option>
          <option value="mathematics">Mathematics</option>
          <option value="science">Science</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {availableGames.map((game) => (
          <div key={game.id} className="border rounded-lg p-4 hover:shadow-lg transition-shadow">
            <div className="text-3xl mb-2 text-center">{game.icon}</div>
            <h3 className="font-semibold text-lg mb-2">{game.name}</h3>
            <p className="text-gray-600 text-sm mb-3">{game.description}</p>
            <div className="flex justify-between items-center text-xs text-gray-500 mb-3">
              <span>⏱️ {game.estimated_time}</span>
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">{game.difficulty}</span>
            </div>
            <button
              onClick={() => startGame(game.id)}
              disabled={loading}
              className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400"
            >
              {loading ? 'Starting...' : 'Play Now'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )

  const renderWordMatchGame = () => (
    <div className="bg-white rounded-lg shadow-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">🎯 Word Match Challenge</h2>
        <button
          onClick={() => { setActiveGame(null); setGameData(null) }}
          className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
        >
          Back to Games
        </button>
      </div>
      
      <p className="text-gray-600 mb-6">{gameData?.instructions}</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold mb-3">Terms</h3>
          <div className="space-y-2">
            {gameData?.terms?.map((term, idx) => (
              <button
                key={idx}
                className="w-full text-left p-3 border rounded-lg hover:bg-blue-50 hover:border-blue-300"
                onClick={() => handleWordMatch(term, 'selected')}
              >
                {term}
              </button>
            ))}
          </div>
        </div>
        
        <div>
          <h3 className="font-semibold mb-3">Definitions</h3>
          <div className="space-y-2">
            {gameData?.definitions?.map((definition, idx) => (
              <button
                key={idx}
                className="w-full text-left p-3 border rounded-lg hover:bg-green-50 hover:border-green-300"
                onClick={() => handleWordMatch('selected', definition)}
              >
                {definition}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )

  const renderLightningQuiz = () => (
    <div className="bg-white rounded-lg shadow-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">⚡ Lightning Quiz</h2>
        <button
          onClick={() => { setActiveGame(null); setGameData(null) }}
          className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
        >
          Back to Games
        </button>
      </div>
      
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Question {gameData?.question_number} of {gameData?.total_questions}</span>
          <span>⏰ {gameData?.time_limit}s</span>
        </div>
      </div>
      
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-4">{gameData?.question?.question}</h3>
        <div className="space-y-2">
          {gameData?.question?.options?.map((option, idx) => (
            <button
              key={idx}
              onClick={() => handleLightningAnswer(idx)}
              className="w-full text-left p-3 border rounded-lg hover:bg-indigo-50 hover:border-indigo-300"
            >
              {option}
            </button>
          ))}
        </div>
      </div>
    </div>
  )

  const renderMemoryCards = () => (
    <div className="bg-white rounded-lg shadow-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">🃏 Memory Cards</h2>
        <button
          onClick={() => { setActiveGame(null); setGameData(null) }}
          className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
        >
          Back to Games
        </button>
      </div>
      
      <p className="text-gray-600 mb-6">{gameData?.instructions}</p>
      
      <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
        {gameData?.cards?.map((card) => (
          <button
            key={card.id}
            onClick={() => handleCardFlip(card.id)}
            className={`aspect-square border-2 rounded-lg p-2 text-sm font-medium transition-all ${
              card.flipped 
                ? 'bg-blue-100 border-blue-300' 
                : 'bg-gray-100 border-gray-300 hover:bg-gray-200'
            }`}
          >
            {card.flipped ? '📝' : '❓'}
          </button>
        ))}
      </div>
    </div>
  )

  if (activeGame === 'word-match') return renderWordMatchGame()
  if (activeGame === 'lightning-quiz') return renderLightningQuiz()
  if (activeGame === 'memory-cards') return renderMemoryCards()
  
  return renderGameSelection()
}