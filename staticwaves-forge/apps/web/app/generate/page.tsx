'use client'

import { useState } from 'react'
import { Sparkles, History, BookOpen, Zap, Layers } from 'lucide-react'
import PromptPanel from '@/components/PromptPanel'
import Viewport3D from '@/components/Viewport3D'
import ExportPanel from '@/components/ExportPanel'
import JobStatus from '@/components/JobStatus'
import { useToast } from '@/components/Toast'

const EXAMPLE_PROMPTS = [
  {
    category: 'Weapons',
    prompts: [
      'A low-poly medieval sword with leather-wrapped grip',
      'Futuristic energy blade with glowing blue core',
      'Ornate fantasy staff with crystal top',
      'Steampunk revolver with brass details'
    ]
  },
  {
    category: 'Creatures',
    prompts: [
      'Stylized dragon with vibrant scales',
      'Cute low-poly fox with bushy tail',
      'Alien creature with bioluminescent features',
      'Mythical phoenix with flame effects'
    ]
  },
  {
    category: 'Props',
    prompts: [
      'Treasure chest overflowing with gold coins',
      'Sci-fi cargo crate with holographic labels',
      'Medieval wooden barrel with iron bands',
      'Cyberpunk vending machine with neon signs'
    ]
  }
]

export default function GeneratePage() {
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)
  const [previewModel, setPreviewModel] = useState<string | null>(null)
  const [showExamples, setShowExamples] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const { showToast } = useToast()

  const handleExampleSelect = (prompt: string) => {
    // This would trigger the PromptPanel to use this prompt
    showToast(`Example loaded: "${prompt.substring(0, 40)}..."`, 'info')
    setShowExamples(false)
  }

  const quickActions = [
    { icon: Sparkles, label: 'Random', tooltip: 'Generate random asset' },
    { icon: Layers, label: 'Batch', tooltip: 'Batch generation' },
    { icon: Zap, label: 'Quick', tooltip: 'Quick generation (low quality)' }
  ]

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 bg-gray-900/50 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-6 h-6 text-blue-400" />
              <h1 className="text-2xl font-bold">Asset Generator</h1>
            </div>
            <p className="text-sm text-gray-400">Create production-ready 3D assets from prompts</p>
          </div>
          <div className="flex gap-3">
            {/* Quick Actions */}
            {quickActions.map((action) => (
              <button
                key={action.label}
                className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors group"
                title={action.tooltip}
                onClick={() => showToast(`${action.label} mode activated`, 'info')}
              >
                <action.icon className="w-4 h-4" />
                <span className="hidden sm:inline">{action.label}</span>
              </button>
            ))}

            {/* Examples */}
            <div className="relative">
              <button
                onClick={() => setShowExamples(!showExamples)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <BookOpen className="w-4 h-4" />
                <span className="hidden sm:inline">Examples</span>
              </button>

              {showExamples && (
                <div className="absolute top-full right-0 mt-2 w-80 bg-gray-900 border border-gray-800 rounded-xl shadow-2xl z-50 animate-fade-in">
                  <div className="p-4 border-b border-gray-800">
                    <h3 className="font-semibold">Example Prompts</h3>
                    <p className="text-xs text-gray-400 mt-1">Click to use</p>
                  </div>
                  <div className="max-h-96 overflow-y-auto p-2">
                    {EXAMPLE_PROMPTS.map((category) => (
                      <div key={category.category} className="mb-4">
                        <div className="px-3 py-2 text-sm font-medium text-gray-400">
                          {category.category}
                        </div>
                        <div className="space-y-1">
                          {category.prompts.map((prompt, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleExampleSelect(prompt)}
                              className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors text-sm"
                            >
                              {prompt}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* History */}
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
            >
              <History className="w-4 h-4" />
              <span className="hidden sm:inline">History</span>
            </button>
          </div>
        </div>

        {/* Keyboard Shortcuts Hint */}
        <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <kbd className="px-2 py-1 bg-gray-800 rounded">Ctrl</kbd>
            <span>+</span>
            <kbd className="px-2 py-1 bg-gray-800 rounded">Enter</kbd>
            <span>Generate</span>
          </div>
          <div className="flex items-center gap-1">
            <kbd className="px-2 py-1 bg-gray-800 rounded">Ctrl</kbd>
            <span>+</span>
            <kbd className="px-2 py-1 bg-gray-800 rounded">R</kbd>
            <span>Random</span>
          </div>
          <div className="flex items-center gap-1">
            <kbd className="px-2 py-1 bg-gray-800 rounded">?</kbd>
            <span>Show all shortcuts</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-0">
        {/* Left Panel - Prompt & Controls */}
        <div className="lg:col-span-3 border-r border-gray-800 overflow-y-auto max-h-[calc(100vh-180px)]">
          <PromptPanel onJobCreated={setCurrentJobId} />
        </div>

        {/* Center - 3D Viewport */}
        <div className="lg:col-span-6 relative bg-black min-h-[400px] lg:min-h-0">
          <Viewport3D modelPath={previewModel} />

          {/* Viewport Overlay - Stats */}
          <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2 text-xs font-mono">
            <div className="text-gray-400">Viewport Stats</div>
            <div className="mt-1 space-y-0.5">
              <div>FPS: <span className="text-green-400">60</span></div>
              <div>Triangles: <span className="text-blue-400">{previewModel ? '5.2k' : '0'}</span></div>
            </div>
          </div>

          {/* Viewport Controls Hint */}
          {!previewModel && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center text-gray-500">
                <Sparkles className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg font-medium mb-2">No model loaded</p>
                <p className="text-sm">Generate an asset to preview it here</p>
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Export & Status */}
        <div className="lg:col-span-3 border-l border-gray-800 overflow-y-auto max-h-[calc(100vh-180px)]">
          <div className="p-6 space-y-6">
            {currentJobId && (
              <>
                <div className="border-b border-gray-800 pb-4">
                  <h3 className="font-semibold mb-1 flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-400" />
                    Generation Status
                  </h3>
                  <p className="text-xs text-gray-400">Real-time progress tracking</p>
                </div>
                <JobStatus
                  jobId={currentJobId}
                  onComplete={(result) => {
                    // Set preview model when generation completes
                    if (result.output_files?.glb) {
                      setPreviewModel(result.output_files.glb)
                      showToast('Asset generated successfully!', 'success')
                    }
                  }}
                />
              </>
            )}

            {!currentJobId && (
              <div className="text-center py-8 text-gray-500">
                <History className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm">No active generation</p>
                <p className="text-xs mt-1">Start generating to see progress</p>
              </div>
            )}

            <div className="border-t border-gray-800 pt-6">
              <ExportPanel />
            </div>
          </div>
        </div>
      </div>

      {/* History Sidebar */}
      {showHistory && (
        <div className="fixed inset-y-0 right-0 w-80 bg-gray-900 border-l border-gray-800 shadow-2xl z-40 animate-slide-in-right overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Generation History</h2>
              <button
                onClick={() => setShowHistory(false)}
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="bg-gray-800/50 rounded-lg p-3 hover:bg-gray-800 transition-colors cursor-pointer"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded flex items-center justify-center flex-shrink-0">
                      ⚔️
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">Medieval Sword</div>
                      <div className="text-xs text-gray-400 mt-1">2 hours ago</div>
                      <div className="text-xs text-green-400 mt-1">Completed</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Click outside to close dropdowns */}
      {(showExamples || showHistory) && (
        <div
          className="fixed inset-0 z-30"
          onClick={() => {
            setShowExamples(false)
            setShowHistory(false)
          }}
        />
      )}
    </div>
  )
}
