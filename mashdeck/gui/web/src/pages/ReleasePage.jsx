import { useState } from 'react'
import { Upload, Music, CheckCircle } from 'lucide-react'
import axios from 'axios'

export default function ReleasePage() {
  const [formData, setFormData] = useState({
    audio_path: '',
    title: '',
    artist: 'MashDeck AI',
    genre: 'Electronic',
    platforms: {
      spotify: true,
      tiktok: true,
      youtube: true
    }
  })

  const [releasing, setReleasing] = useState(false)
  const [results, setResults] = useState(null)

  const handleRelease = async () => {
    setReleasing(true)
    setResults(null)

    try {
      const selectedPlatforms = Object.keys(formData.platforms).filter(
        (key) => formData.platforms[key]
      )

      const response = await axios.post('/api/release', {
        audio_path: formData.audio_path,
        title: formData.title,
        artist: formData.artist,
        genre: formData.genre,
        platforms: selectedPlatforms
      })

      setResults(response.data.results)
    } catch (error) {
      alert('Error: ' + error.message)
    } finally {
      setReleasing(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-8">Auto-Release</h1>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Release Form */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Track Details</h2>

          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Audio File Path</label>
            <input
              type="text"
              value={formData.audio_path}
              onChange={(e) => setFormData({ ...formData, audio_path: e.target.value })}
              placeholder="e.g., output/song_123/song_final.wav"
              className="w-full bg-tertiary border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-accent"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Track Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="My Amazing Track"
              className="w-full bg-tertiary border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-accent"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Artist Name</label>
            <input
              type="text"
              value={formData.artist}
              onChange={(e) => setFormData({ ...formData, artist: e.target.value })}
              placeholder="Your Name"
              className="w-full bg-tertiary border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-accent"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Genre</label>
            <select
              value={formData.genre}
              onChange={(e) => setFormData({ ...formData, genre: e.target.value })}
              className="w-full bg-tertiary border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-accent"
            >
              <option value="Electronic">Electronic</option>
              <option value="Hip-Hop">Hip-Hop</option>
              <option value="Rock">Rock</option>
              <option value="Pop">Pop</option>
              <option value="Ambient">Ambient</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium mb-3">Platforms</label>
            <div className="space-y-3">
              {Object.keys(formData.platforms).map((platform) => (
                <label key={platform} className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.platforms[platform]}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        platforms: {
                          ...formData.platforms,
                          [platform]: e.target.checked
                        }
                      })
                    }
                    className="w-5 h-5"
                  />
                  <span className="capitalize font-medium">{platform}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={handleRelease}
            disabled={releasing || !formData.audio_path || !formData.title}
            className="w-full button-primary flex items-center justify-center gap-2"
          >
            {releasing ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Releasing...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                Release Track
              </>
            )}
          </button>
        </div>

        {/* Results */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Release Status</h2>

          {!results && !releasing && (
            <div className="text-center py-12 text-gray-500">
              <Music className="w-16 h-16 mx-auto mb-4 opacity-20" />
              <p>Fill in track details and click Release</p>
            </div>
          )}

          {releasing && (
            <div className="text-center py-12">
              <div className="w-16 h-16 border-4 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-gray-400">Processing release...</p>
            </div>
          )}

          {results && (
            <div className="space-y-4">
              {Object.entries(results).map(([platform, result]) => (
                <div
                  key={platform}
                  className={`p-4 rounded-lg border-2 ${
                    result.status === 'pending'
                      ? 'border-yellow-500 bg-yellow-900/20'
                      : result.status === 'error'
                      ? 'border-red-500 bg-red-900/20'
                      : 'border-green-500 bg-green-900/20'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold capitalize">{platform}</span>
                    {result.status === 'pending' && (
                      <CheckCircle className="w-5 h-5 text-yellow-500" />
                    )}
                  </div>

                  <div className="text-sm text-gray-400">
                    Status: <span className="capitalize">{result.status}</span>
                  </div>

                  {result.error && (
                    <div className="text-sm text-red-400 mt-2">
                      Error: {result.error}
                    </div>
                  )}

                  {result.upload_id && (
                    <div className="text-xs text-gray-500 mt-2">
                      ID: {result.upload_id}
                    </div>
                  )}

                  {result.release_id && (
                    <div className="text-xs text-gray-500 mt-2">
                      Release ID: {result.release_id}
                    </div>
                  )}
                </div>
              ))}

              <div className="mt-6 p-4 bg-green-900/20 border border-green-700 rounded-lg">
                <div className="text-green-400 font-bold mb-1">
                  ✓ Release Initiated
                </div>
                <div className="text-sm text-gray-400">
                  Your track has been queued for distribution. Check each platform for
                  final approval status.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
