import { useState } from 'react'
import { Music, Play, Download, Loader } from 'lucide-react'
import axios from 'axios'

export default function GeneratePage() {
  const [formData, setFormData] = useState({
    style: 'edm',
    bpm: '',
    key: '',
    title: '',
    create_variants: false
  })

  const [generating, setGenerating] = useState(false)
  const [result, setResult] = useState(null)

  const styles = [
    { id: 'edm', name: 'EDM', desc: 'Electronic Dance Music' },
    { id: 'lofi', name: 'Lo-Fi', desc: 'Chill Lo-Fi Beats' },
    { id: 'trap', name: 'Trap', desc: 'Hard Trap' },
    { id: 'hiphop', name: 'Hip-Hop', desc: 'Classic Hip-Hop' },
    { id: 'ambient', name: 'Ambient', desc: 'Atmospheric' },
    { id: 'rock', name: 'Rock', desc: 'Rock Music' }
  ]

  const handleGenerate = async () => {
    setGenerating(true)
    setResult(null)

    try {
      const response = await axios.post('/api/generate/song', {
        style: formData.style,
        bpm: formData.bpm ? parseInt(formData.bpm) : null,
        key: formData.key || null,
        title: formData.title || null,
        create_variants: formData.create_variants
      })

      setResult(response.data)

      // Poll for status
      const jobId = response.data.job_id
      const pollInterval = setInterval(async () => {
        const statusRes = await axios.get(`/api/generate/status/${jobId}`)

        if (statusRes.data.status === 'completed') {
          clearInterval(pollInterval)
          setGenerating(false)
          setResult(statusRes.data)
        } else if (statusRes.data.status === 'failed') {
          clearInterval(pollInterval)
          setGenerating(false)
          alert('Generation failed: ' + statusRes.data.error)
        }
      }, 2000)

    } catch (error) {
      setGenerating(false)
      alert('Error: ' + error.message)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-8">Generate Full Song</h1>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Generation Form */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Song Settings</h2>

          {/* Style Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-3">Style</label>
            <div className="grid grid-cols-2 gap-3">
              {styles.map((style) => (
                <button
                  key={style.id}
                  onClick={() => setFormData({ ...formData, style: style.id })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    formData.style === style.id
                      ? 'border-accent bg-accent/10'
                      : 'border-gray-700 hover:border-gray-600'
                  }`}
                >
                  <div className="font-bold">{style.name}</div>
                  <div className="text-xs text-gray-400">{style.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* BPM */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">BPM (Optional)</label>
            <input
              type="number"
              value={formData.bpm}
              onChange={(e) => setFormData({ ...formData, bpm: e.target.value })}
              placeholder="Auto"
              className="w-full bg-tertiary border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-accent"
            />
          </div>

          {/* Key */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Key (Optional)</label>
            <input
              type="text"
              value={formData.key}
              onChange={(e) => setFormData({ ...formData, key: e.target.value })}
              placeholder="e.g., F minor"
              className="w-full bg-tertiary border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-accent"
            />
          </div>

          {/* Title */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Title (Optional)</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Auto-generated"
              className="w-full bg-tertiary border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-accent"
            />
          </div>

          {/* Variants */}
          <div className="mb-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.create_variants}
                onChange={(e) => setFormData({ ...formData, create_variants: e.target.checked })}
                className="w-5 h-5"
              />
              <span className="text-sm">Create platform variants</span>
            </label>
            <p className="text-xs text-gray-500 mt-1">
              Generate Spotify, TikTok, YouTube optimized versions
            </p>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="w-full button-primary flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Music className="w-5 h-5" />
                Generate Song
              </>
            )}
          </button>

          {generating && (
            <div className="mt-4 text-center text-sm text-gray-400">
              This may take 2-5 minutes...
            </div>
          )}
        </div>

        {/* Result Display */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Output</h2>

          {!result && !generating && (
            <div className="text-center py-12 text-gray-500">
              <Music className="w-16 h-16 mx-auto mb-4 opacity-20" />
              <p>Configure settings and click Generate to create your song</p>
            </div>
          )}

          {generating && (
            <div className="text-center py-12">
              <Loader className="w-16 h-16 mx-auto mb-4 animate-spin text-accent" />
              <p className="text-gray-400">Generating your song...</p>
              <div className="mt-4 text-sm text-gray-500">
                <div>✓ Planning structure</div>
                <div>✓ Generating sections</div>
                <div>⏳ Arranging timeline</div>
                <div>⏳ Mastering audio</div>
              </div>
            </div>
          )}

          {result && result.status === 'completed' && (
            <div>
              <div className="mb-4 p-4 bg-green-900/20 border border-green-700 rounded-lg">
                <div className="text-green-400 font-bold mb-1">✓ Generation Complete!</div>
                <div className="text-sm text-gray-400">
                  {result.output?.metadata?.title || 'Song'} - {result.output?.metadata?.style}
                </div>
              </div>

              {/* Audio Player */}
              <div className="mb-6 p-4 bg-tertiary rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <button className="w-12 h-12 bg-accent rounded-full flex items-center justify-center">
                    <Play className="w-6 h-6" />
                  </button>
                  <div className="flex-1">
                    <div className="h-2 bg-gray-700 rounded-full">
                      <div className="h-2 bg-accent rounded-full" style={{ width: '0%' }} />
                    </div>
                  </div>
                </div>
                <div className="text-xs text-gray-400">
                  {result.output?.metadata?.bpm} BPM • {result.output?.metadata?.key}
                </div>
              </div>

              {/* Download Options */}
              <div className="space-y-2">
                <button className="w-full flex items-center justify-between p-3 bg-tertiary hover:bg-gray-700 rounded-lg transition-colors">
                  <span>Final Master</span>
                  <Download className="w-5 h-5" />
                </button>
                <button className="w-full flex items-center justify-between p-3 bg-tertiary hover:bg-gray-700 rounded-lg transition-colors">
                  <span>Section Stems</span>
                  <Download className="w-5 h-5" />
                </button>
                {formData.create_variants && (
                  <button className="w-full flex items-center justify-between p-3 bg-tertiary hover:bg-gray-700 rounded-lg transition-colors">
                    <span>Platform Variants</span>
                    <Download className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
