import { useState } from 'react'
import { Sword, Play, Crown } from 'lucide-react'
import axios from 'axios'

export default function BattlePage() {
  const [battleActive, setBattleActive] = useState(false)
  const [rounds, setRounds] = useState([])
  const [currentRound, setCurrentRound] = useState(0)
  const [scoreA, setScoreA] = useState(0)
  const [scoreB, setScoreB] = useState(0)
  const [winner, setWinner] = useState(null)

  const [config, setConfig] = useState({
    rounds: 3,
    bars: 4
  })

  const handleStart = async () => {
    try {
      await axios.post('/api/battle/start', config)
      setBattleActive(true)
      setRounds([])
      setCurrentRound(0)
      setScoreA(0)
      setScoreB(0)
      setWinner(null)
    } catch (error) {
      alert('Error starting battle: ' + error.message)
    }
  }

  const handleExecuteRound = async () => {
    try {
      const response = await axios.post('/api/battle/round', null, {
        params: { bars: config.bars }
      })

      const roundData = response.data.round
      setRounds([...rounds, roundData])
      setCurrentRound(currentRound + 1)
      setScoreA(scoreA + roundData.side_a_score)
      setScoreB(scoreB + roundData.side_b_score)

      if (currentRound + 1 >= config.rounds) {
        // Battle over
        const battleWinner = scoreA + roundData.side_a_score > scoreB + roundData.side_b_score ? 'A' : 'B'
        setWinner(battleWinner)
        await axios.post('/api/battle/end')
      }

    } catch (error) {
      alert('Error executing round: ' + error.message)
    }
  }

  const addTestMessages = async () => {
    // Add simulated chat messages
    const messagesA = ['fire', 'energy', 'lets go', 'sick']
    const messagesB = ['yeah', 'vibe', 'intense', 'wow']

    for (const msg of messagesA) {
      await axios.post('/api/battle/chat', {
        side: 'A',
        username: 'user_a',
        message: msg
      })
    }

    for (const msg of messagesB) {
      await axios.post('/api/battle/chat', {
        side: 'B',
        username: 'user_b',
        message: msg
      })
    }
  }

  if (!battleActive) {
    return (
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">AI Rapper Battle</h1>

        <div className="card max-w-md mx-auto">
          <div className="w-24 h-24 bg-gradient-to-br from-red-600 to-orange-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <Sword className="w-12 h-12" />
          </div>

          <h2 className="text-2xl font-bold text-center mb-6">Start Battle</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Number of Rounds</label>
              <select
                value={config.rounds}
                onChange={(e) => setConfig({ ...config, rounds: parseInt(e.target.value) })}
                className="w-full bg-tertiary border border-gray-700 rounded-lg px-4 py-2"
              >
                <option value={1}>1 Round</option>
                <option value={3}>3 Rounds</option>
                <option value={5}>5 Rounds</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Bars per Round</label>
              <select
                value={config.bars}
                onChange={(e) => setConfig({ ...config, bars: parseInt(e.target.value) })}
                className="w-full bg-tertiary border border-gray-700 rounded-lg px-4 py-2"
              >
                <option value={4}>4 Bars</option>
                <option value={8}>8 Bars</option>
                <option value={16}>16 Bars</option>
              </select>
            </div>

            <button
              onClick={handleStart}
              className="w-full button-primary"
            >
              Start Battle
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-4xl font-bold mb-8">🥊 Battle in Progress</h1>

      {/* Scoreboard */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className={`card ${winner === 'A' ? 'border-yellow-500 border-2' : ''}`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl font-bold">Side A</h3>
            {winner === 'A' && <Crown className="w-8 h-8 text-yellow-500" />}
          </div>
          <div className="text-5xl font-bold text-accent mb-2">{scoreA.toFixed(1)}</div>
          <div className="text-gray-400">Total Score</div>
        </div>

        <div className={`card ${winner === 'B' ? 'border-yellow-500 border-2' : ''}`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl font-bold">Side B</h3>
            {winner === 'B' && <Crown className="w-8 h-8 text-yellow-500" />}
          </div>
          <div className="text-5xl font-bold text-accent mb-2">{scoreB.toFixed(1)}</div>
          <div className="text-gray-400">Total Score</div>
        </div>
      </div>

      {/* Round Display */}
      <div className="card mb-8">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold">
            Round {currentRound} of {config.rounds}
          </h3>
          {!winner && (
            <div className="flex gap-2">
              <button
                onClick={addTestMessages}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm"
              >
                Add Test Chat
              </button>
              <button
                onClick={handleExecuteRound}
                className="button-primary flex items-center gap-2"
              >
                <Play className="w-5 h-5" />
                Execute Round
              </button>
            </div>
          )}
        </div>

        {/* Rounds History */}
        <div className="space-y-4">
          {rounds.map((round, idx) => (
            <div key={idx} className="p-4 bg-tertiary rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <span className="font-bold">Round {round.round_num}</span>
                <span className="text-sm text-gray-400">
                  Winner: Side {round.winner}
                </span>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Side A ({round.side_a_score.toFixed(1)})</div>
                  <div className="text-sm bg-secondary p-3 rounded">
                    {round.side_a_lyrics}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-400 mb-1">Side B ({round.side_b_score.toFixed(1)})</div>
                  <div className="text-sm bg-secondary p-3 rounded">
                    {round.side_b_lyrics}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {winner && (
          <div className="mt-8 p-6 bg-gradient-to-r from-yellow-600 to-orange-600 rounded-lg text-center">
            <Crown className="w-16 h-16 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-2">WINNER: SIDE {winner}</h2>
            <p className="text-xl">
              Final Score: {winner === 'A' ? scoreA.toFixed(1) : scoreB.toFixed(1)} - {winner === 'A' ? scoreB.toFixed(1) : scoreA.toFixed(1)}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
