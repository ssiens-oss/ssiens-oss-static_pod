import { useEffect } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Music, Mic, Sword, Store, Upload, Home, Settings, FolderOpen } from 'lucide-react'
import GeneratePage from './pages/GeneratePage'
import FreestylePage from './pages/FreestylePage'
import BattlePage from './pages/BattlePage'
import MarketplacePage from './pages/MarketplacePage'
import ReleasePage from './pages/ReleasePage'
import HomePage from './pages/HomePage'
import SettingsPage from './pages/SettingsPage'
import ProjectsPage from './pages/ProjectsPage'
import { ToastContainer } from './components'
import useStore from './store'

function App() {
  const location = useLocation()
  const initialize = useStore((state) => state.initialize)
  const cleanup = useStore((state) => state.cleanup)

  // Initialize store on mount
  useEffect(() => {
    initialize()
    return () => cleanup()
  }, [initialize, cleanup])

  const navigation = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/projects', icon: FolderOpen, label: 'Projects' },
    { path: '/generate', icon: Music, label: 'Generate' },
    { path: '/freestyle', icon: Mic, label: 'Freestyle' },
    { path: '/battle', icon: Sword, label: 'Battle' },
    { path: '/marketplace', icon: Store, label: 'Marketplace' },
    { path: '/release', icon: Upload, label: 'Release' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <div className="min-h-screen bg-primary text-white">
      {/* Toast Notifications */}
      <ToastContainer />

      {/* Header */}
      <header className="glass sticky top-0 z-50 border-b border-gray-800">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                <Music className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">MashDeck</h1>
                <p className="text-xs text-gray-400">AI Music Production Studio</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 min-h-screen bg-secondary border-r border-gray-800 p-4">
          <nav className="space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    isActive
                      ? 'bg-accent text-white'
                      : 'text-gray-400 hover:bg-tertiary hover:text-white'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              )
            })}
          </nav>

          {/* Token Balance */}
          <div className="mt-8 p-4 bg-tertiary rounded-lg">
            <div className="text-sm text-gray-400 mb-1">Token Balance</div>
            <div className="text-2xl font-bold text-accent">1,250 CT</div>
            <div className="text-xs text-gray-500 mt-1">Compute Tokens</div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/generate" element={<GeneratePage />} />
            <Route path="/freestyle" element={<FreestylePage />} />
            <Route path="/battle" element={<BattlePage />} />
            <Route path="/marketplace" element={<MarketplacePage />} />
            <Route path="/release" element={<ReleasePage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
