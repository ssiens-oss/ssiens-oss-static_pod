import { useState, useEffect } from 'react'
import { Store, Download, Star } from 'lucide-react'
import axios from 'axios'

export default function MarketplacePage() {
  const [assets, setAssets] = useState([])
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    loadAssets()
  }, [filter])

  const loadAssets = async () => {
    try {
      const response = await axios.get('/api/marketplace/assets', {
        params: filter !== 'all' ? { asset_type: filter } : {}
      })
      setAssets(response.data.assets)
    } catch (error) {
      console.error('Error loading assets:', error)
    }
  }

  const handlePurchase = async (assetId) => {
    try {
      const response = await axios.post(
        `/api/marketplace/purchase/${assetId}`,
        null,
        {
          params: {
            user_id: 'user_123',
            balance: 1250
          }
        }
      )

      if (response.data.success) {
        alert('Purchase successful!')
        loadAssets()
      } else {
        alert('Purchase failed: ' + response.data.error)
      }
    } catch (error) {
      alert('Error: ' + error.message)
    }
  }

  const assetTypes = [
    { id: 'all', name: 'All Assets' },
    { id: 'preset', name: 'Presets' },
    { id: 'voice', name: 'Voice Packs' },
    { id: 'midi', name: 'MIDI' },
    { id: 'persona', name: 'Personas' },
    { id: 'battle_theme', name: 'Battle Themes' }
  ]

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-4xl font-bold mb-8">Creator Marketplace</h1>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-8 overflow-x-auto">
        {assetTypes.map((type) => (
          <button
            key={type.id}
            onClick={() => setFilter(type.id)}
            className={`px-6 py-2 rounded-lg whitespace-nowrap transition-all ${
              filter === type.id
                ? 'bg-accent text-white'
                : 'bg-tertiary text-gray-400 hover:bg-gray-700'
            }`}
          >
            {type.name}
          </button>
        ))}
      </div>

      {/* Assets Grid */}
      {assets.length === 0 ? (
        <div className="card text-center py-20">
          <Store className="w-16 h-16 mx-auto mb-4 opacity-20" />
          <p className="text-gray-500">No assets found</p>
          <p className="text-sm text-gray-600 mt-2">
            Check back later for new creator assets
          </p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assets.map((asset) => (
            <div key={asset.id} className="card hover:border-accent transition-all">
              {/* Asset Type Badge */}
              <div className="inline-block px-3 py-1 bg-accent/20 text-accent text-xs font-bold rounded-full mb-4">
                {asset.type}
              </div>

              {/* Asset Info */}
              <h3 className="text-xl font-bold mb-2">{asset.name}</h3>
              <p className="text-sm text-gray-400 mb-4">{asset.description}</p>

              {/* Creator */}
              <div className="text-sm text-gray-500 mb-4">
                by {asset.creator_name}
              </div>

              {/* Stats */}
              <div className="flex items-center gap-4 mb-4 text-sm">
                <div className="flex items-center gap-1">
                  <Download className="w-4 h-4" />
                  <span>{asset.downloads}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                  <span>{asset.rating.toFixed(1)}</span>
                </div>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-2 mb-4">
                {asset.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-tertiary text-xs rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              {/* Price & Purchase */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-700">
                <div>
                  <div className="text-2xl font-bold text-accent">
                    {asset.price_tokens} CT
                  </div>
                  <div className="text-xs text-gray-500">Compute Tokens</div>
                </div>
                <button
                  onClick={() => handlePurchase(asset.id)}
                  className="px-6 py-2 bg-accent hover:bg-accent-hover rounded-lg transition-colors"
                >
                  Purchase
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
