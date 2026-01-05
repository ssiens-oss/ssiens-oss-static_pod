/**
 * StaticWaves POD Engine - AI Image Generator
 * ComfyUI integration for automated image generation
 */

import React, { useState, useEffect } from 'react'
import {
  Wand2, Sparkles, Image as ImageIcon, Settings, Download,
  Loader2, CheckCircle, XCircle, Copy, Shuffle, Zap,
  Palette, Maximize2, Play, Pause, Trash2, RefreshCw
} from 'lucide-react'

interface GenerationJob {
  id: string
  prompt: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  imageUrl?: string
  error?: string
  createdAt: string
}

interface GenerationPreset {
  name: string
  prompt: string
  style: string
  category: string
}

const STYLE_PRESETS = [
  'Photorealistic', 'Digital Art', 'Oil Painting', 'Watercolor',
  'Anime', 'Cartoon', 'Abstract', '3D Render', 'Pixel Art',
  'Sketch', 'Pop Art', 'Minimalist', 'Retro', 'Cyberpunk'
]

const PROMPT_TEMPLATES: GenerationPreset[] = [
  {
    name: 'Nature Scene',
    prompt: 'A beautiful landscape with mountains and a lake at sunset, vibrant colors, highly detailed',
    style: 'Photorealistic',
    category: 'Nature'
  },
  {
    name: 'Abstract Art',
    prompt: 'Abstract geometric shapes with bold colors and dynamic composition, modern art',
    style: 'Abstract',
    category: 'Art'
  },
  {
    name: 'Cute Animal',
    prompt: 'Adorable fluffy animal character with big eyes, colorful and cheerful, kawaii style',
    style: 'Cartoon',
    category: 'Characters'
  },
  {
    name: 'Space Scene',
    prompt: 'Cosmic nebula with stars and planets, deep space, vibrant purple and blue colors',
    style: '3D Render',
    category: 'Space'
  },
  {
    name: 'Floral Design',
    prompt: 'Elegant floral pattern with roses and leaves, detailed botanical illustration',
    style: 'Watercolor',
    category: 'Nature'
  },
  {
    name: 'Typography Art',
    prompt: 'Motivational quote in beautiful typography, modern design with decorative elements',
    style: 'Minimalist',
    category: 'Typography'
  }
]

export default function ImageGenerator() {
  const [prompt, setPrompt] = useState('')
  const [negativePrompt, setNegativePrompt] = useState('blurry, low quality, distorted')
  const [style, setStyle] = useState('Photorealistic')
  const [width, setWidth] = useState(4500)
  const [height, setHeight] = useState(5400)
  const [steps, setSteps] = useState(30)
  const [guidanceScale, setGuidanceScale] = useState(7.5)
  const [batchSize, setBatchSize] = useState(1)

  const [jobs, setJobs] = useState<GenerationJob[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)

  const API_BASE = 'http://localhost:8000/api'
  const token = localStorage.getItem('token')

  // Fetch existing jobs on mount
  useEffect(() => {
    fetchJobs()
  }, [])

  const fetchJobs = async () => {
    try {
      const response = await fetch(`${API_BASE}/generation/jobs`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setJobs(data)
      }
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    }
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      alert('Please enter a prompt')
      return
    }

    setIsGenerating(true)

    try {
      const response = await fetch(`${API_BASE}/generation/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt,
          negative_prompt: negativePrompt,
          style,
          width,
          height,
          steps,
          guidance_scale: guidanceScale,
          batch_size: batchSize
        })
      })

      if (!response.ok) {
        throw new Error('Generation failed')
      }

      const newJob = await response.json()
      setJobs([newJob, ...jobs])

      // Start polling for job status
      pollJobStatus(newJob.id)
    } catch (error: any) {
      alert('Failed to start generation: ' + error.message)
    } finally {
      setIsGenerating(false)
    }
  }

  const pollJobStatus = async (jobId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE}/generation/jobs/${jobId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (response.ok) {
          const updatedJob = await response.json()
          setJobs(prevJobs =>
            prevJobs.map(job => job.id === jobId ? updatedJob : job)
          )

          // Stop polling if job is complete or failed
          if (updatedJob.status === 'completed' || updatedJob.status === 'failed') {
            clearInterval(interval)
          }
        }
      } catch (error) {
        console.error('Failed to poll job status:', error)
      }
    }, 2000) // Poll every 2 seconds
  }

  const handleTemplateSelect = (template: GenerationPreset) => {
    setPrompt(template.prompt)
    setStyle(template.style)
    setSelectedTemplate(template.name)
  }

  const handleRandomPrompt = () => {
    const randomTemplate = PROMPT_TEMPLATES[Math.floor(Math.random() * PROMPT_TEMPLATES.length)]
    handleTemplateSelect(randomTemplate)
  }

  const handleSaveToLibrary = async (jobId: string) => {
    try {
      const response = await fetch(`${API_BASE}/generation/jobs/${jobId}/save`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        alert('Image saved to design library!')
        fetchJobs()
      }
    } catch (error) {
      alert('Failed to save image')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'queued':
        return <Loader2 className="w-5 h-5 text-yellow-600 animate-pulse" />
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'queued':
        return 'bg-yellow-100 text-yellow-800'
      case 'processing':
        return 'bg-blue-100 text-blue-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-3 rounded-lg">
            <Wand2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">AI Image Generator</h2>
            <p className="text-gray-600">Create stunning designs with AI powered by ComfyUI</p>
          </div>
        </div>
        <button
          onClick={fetchJobs}
          className="p-2 hover:bg-gray-100 rounded-lg transition"
          title="Refresh jobs"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Generation Settings Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Prompt Templates */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-600" />
                Quick Start Templates
              </h3>
              <button
                onClick={handleRandomPrompt}
                className="flex items-center gap-2 px-3 py-1 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition text-sm"
              >
                <Shuffle className="w-4 h-4" />
                Random
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {PROMPT_TEMPLATES.map((template) => (
                <button
                  key={template.name}
                  onClick={() => handleTemplateSelect(template)}
                  className={`p-3 rounded-lg border-2 transition text-left ${
                    selectedTemplate === template.name
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 hover:border-purple-300 bg-white'
                  }`}
                >
                  <div className="font-medium text-sm">{template.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{template.category}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Prompt Input */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <ImageIcon className="w-5 h-5 text-blue-600" />
              Describe Your Image
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prompt
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="A beautiful sunset over mountains with vibrant colors..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent resize-none"
                  rows={4}
                />
                <p className="text-xs text-gray-500 mt-2">
                  Describe what you want to see. Be specific and detailed for best results.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Negative Prompt (What to avoid)
                </label>
                <input
                  type="text"
                  value={negativePrompt}
                  onChange={(e) => setNegativePrompt(e.target.value)}
                  placeholder="blurry, low quality, distorted"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Palette className="w-4 h-4 inline mr-1" />
                  Art Style
                </label>
                <select
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                >
                  {STYLE_PRESETS.map((styleOption) => (
                    <option key={styleOption} value={styleOption}>
                      {styleOption}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Advanced Settings */}
          <div className="bg-white rounded-lg shadow p-6">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full flex items-center justify-between mb-4"
            >
              <h3 className="font-semibold flex items-center gap-2">
                <Settings className="w-5 h-5 text-gray-600" />
                Advanced Settings
              </h3>
              <span className="text-sm text-gray-500">
                {showAdvanced ? 'Hide' : 'Show'}
              </span>
            </button>

            {showAdvanced && (
              <div className="space-y-4 pt-4 border-t">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Width
                    </label>
                    <select
                      value={width}
                      onChange={(e) => setWidth(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value={4500}>4500px (POD Standard)</option>
                      <option value={1024}>1024px</option>
                      <option value={512}>512px</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Height
                    </label>
                    <select
                      value={height}
                      onChange={(e) => setHeight(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value={5400}>5400px (POD Standard)</option>
                      <option value={1024}>1024px</option>
                      <option value={512}>512px</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Inference Steps: {steps}
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={steps}
                    onChange={(e) => setSteps(Number(e.target.value))}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    More steps = higher quality but slower generation
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Guidance Scale: {guidanceScale}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="20"
                    step="0.5"
                    value={guidanceScale}
                    onChange={(e) => setGuidanceScale(Number(e.target.value))}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    How closely to follow the prompt (7-9 recommended)
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Batch Size
                  </label>
                  <select
                    value={batchSize}
                    onChange={(e) => setBatchSize(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value={1}>1 image</option>
                    <option value={2}>2 images</option>
                    <option value={4}>4 images</option>
                    <option value={8}>8 images</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !prompt.trim()}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 text-lg shadow-lg"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Zap className="w-6 h-6" />
                Generate {batchSize > 1 ? `${batchSize} Images` : 'Image'}
              </>
            )}
          </button>
        </div>

        {/* Generation Queue Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-6 sticky top-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <Loader2 className="w-5 h-5 text-purple-600" />
              Generation Queue ({jobs.length})
            </h3>

            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {jobs.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <ImageIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">No generations yet</p>
                  <p className="text-xs mt-1">Start creating amazing images!</p>
                </div>
              ) : (
                jobs.map((job) => (
                  <div
                    key={job.id}
                    className="border rounded-lg p-3 space-y-2 hover:shadow-md transition"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(job.status)}
                        <span className={`text-xs px-2 py-1 rounded font-medium ${getStatusColor(job.status)}`}>
                          {job.status}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(job.createdAt).toLocaleTimeString()}
                      </span>
                    </div>

                    <p className="text-sm text-gray-700 line-clamp-2">
                      {job.prompt}
                    </p>

                    {job.status === 'processing' && (
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs text-gray-600">
                          <span>Progress</span>
                          <span>{job.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full transition-all"
                            style={{ width: `${job.progress}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {job.status === 'completed' && job.imageUrl && (
                      <div className="space-y-2">
                        <img
                          src={job.imageUrl}
                          alt="Generated"
                          className="w-full rounded border"
                        />
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleSaveToLibrary(job.id)}
                            className="flex-1 bg-green-600 text-white py-1 px-2 rounded text-xs hover:bg-green-700 transition flex items-center justify-center gap-1"
                          >
                            <Download className="w-3 h-3" />
                            Save to Library
                          </button>
                          <button
                            className="p-1 border rounded hover:bg-gray-50 transition"
                            title="View full size"
                          >
                            <Maximize2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )}

                    {job.status === 'failed' && job.error && (
                      <p className="text-xs text-red-600">
                        Error: {job.error}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
