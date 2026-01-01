import { Music, Mic, Sword, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function HomePage() {
  const features = [
    {
      icon: Music,
      title: 'Generate Songs',
      description: 'Create full-length AI songs with structure and vocals',
      link: '/generate',
      color: 'from-purple-600 to-pink-600'
    },
    {
      icon: Mic,
      title: 'Live Freestyle',
      description: 'Chat-reactive freestyle rap generation in real-time',
      link: '/freestyle',
      color: 'from-blue-600 to-cyan-600'
    },
    {
      icon: Sword,
      title: 'AI Battles',
      description: 'Competitive rapper battles with real-time scoring',
      link: '/battle',
      color: 'from-red-600 to-orange-600'
    },
    {
      icon: TrendingUp,
      title: 'Auto-Release',
      description: 'Distribute to Spotify, TikTok, and YouTube automatically',
      link: '/release',
      color: 'from-green-600 to-emerald-600'
    }
  ]

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero */}
      <div className="text-center mb-16">
        <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          Welcome to MashDeck
        </h1>
        <p className="text-xl text-gray-400 mb-8">
          The world's first AI music system with full-length songs, live vocals, and auto-release
        </p>
        <Link to="/generate">
          <button className="button-primary text-lg px-8 py-4">
            Start Creating Music
          </button>
        </Link>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-2 gap-6 mb-12">
        {features.map((feature) => {
          const Icon = feature.icon
          return (
            <Link key={feature.title} to={feature.link}>
              <div className="card hover:border-accent transition-all cursor-pointer group">
                <div className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-8 h-8" />
                </div>
                <h3 className="text-2xl font-bold mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            </Link>
          )
        })}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-6">
        <div className="card text-center">
          <div className="text-3xl font-bold text-accent mb-1">3-6 min</div>
          <div className="text-gray-400">Song Length</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-accent mb-1">6 Styles</div>
          <div className="text-gray-400">Music Genres</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-accent mb-1">Real-time</div>
          <div className="text-gray-400">Live Features</div>
        </div>
      </div>
    </div>
  )
}
