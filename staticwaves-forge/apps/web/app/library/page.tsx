'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Search, Grid3x3, List, Loader2 } from 'lucide-react'
import AssetDetailModal from '@/components/AssetDetailModal'
import { useToast } from '@/components/Toast'

interface Asset {
  id: string
  name: string
  type: string
  style: string
  created: string
  size: string
  polyCount: number
  downloads: number
  prompt?: string
  seed?: number
}

export default function LibraryPage() {
  const [view, setView] = useState<'grid' | 'list'>('grid')
  const [filter, setFilter] = useState<string>('all')
  const [search, setSearch] = useState<string>('')
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { showToast } = useToast()

  const assets: Asset[] = [
    {
      id: '1',
      name: 'Medieval Sword',
      type: 'weapon',
      style: 'low-poly',
      created: '2024-01-15',
      size: '2.3 MB',
      polyCount: 5234,
      downloads: 12,
      prompt: 'A low-poly medieval sword with leather grip',
      seed: 42857
    },
    {
      id: '2',
      name: 'Cyberpunk Crate',
      type: 'prop',
      style: 'stylized',
      created: '2024-01-14',
      size: '1.8 MB',
      polyCount: 3121,
      downloads: 8,
      prompt: 'Futuristic cargo crate with neon accents',
      seed: 91234
    },
    {
      id: '3',
      name: 'Fantasy Dragon',
      type: 'creature',
      style: 'realistic',
      created: '2024-01-13',
      size: '8.4 MB',
      polyCount: 15234,
      downloads: 25,
      prompt: 'Majestic red dragon with detailed scales',
      seed: 55512
    },
    {
      id: '4',
      name: 'Sci-Fi Console',
      type: 'prop',
      style: 'realistic',
      created: '2024-01-12',
      size: '4.2 MB',
      polyCount: 7823,
      downloads: 15,
      prompt: 'High-tech control console with holographic displays',
      seed: 77889
    },
    {
      id: '5',
      name: 'Battle Axe',
      type: 'weapon',
      style: 'stylized',
      created: '2024-01-11',
      size: '3.1 MB',
      polyCount: 4521,
      downloads: 9,
      prompt: 'Viking battle axe with runic engravings',
      seed: 33445
    },
    {
      id: '6',
      name: 'Treasure Chest',
      type: 'prop',
      style: 'low-poly',
      created: '2024-01-10',
      size: '2.7 MB',
      polyCount: 2845,
      downloads: 18,
      prompt: 'Wooden treasure chest with gold trim',
      seed: 66778
    }
  ]

  const filteredAssets = assets.filter(asset => {
    const matchesFilter = filter === 'all' || asset.type === filter
    const matchesSearch = asset.name.toLowerCase().includes(search.toLowerCase()) ||
                         asset.type.toLowerCase().includes(search.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const handleDownload = (asset: Asset, format: string) => {
    showToast(`Downloading ${asset.name} as ${format}...`, 'success')
    // Simulate download
    setTimeout(() => {
      showToast(`${asset.name} downloaded successfully!`, 'success')
    }, 1500)
  }

  const handleDelete = (asset: Asset) => {
    showToast(`${asset.name} has been deleted`, 'info')
    setSelectedAsset(null)
  }

  const handleShare = (asset: Asset) => {
    navigator.clipboard.writeText(window.location.origin + '/library/' + asset.id)
    showToast('Share link copied to clipboard!', 'success')
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Asset Library</h1>
            <p className="text-gray-400">Manage your generated 3D assets</p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/generate"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
            >
              + New Asset
            </Link>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search assets..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2 focus:border-blue-500 focus:outline-none"
                />
                <Search className="w-5 h-5 absolute left-3 top-2.5 text-gray-400" />
              </div>
            </div>

            {/* Filter */}
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:border-blue-500 focus:outline-none"
            >
              <option value="all">All Types</option>
              <option value="weapon">Weapons</option>
              <option value="creature">Creatures</option>
              <option value="prop">Props</option>
              <option value="character">Characters</option>
            </select>

            {/* View Toggle */}
            <div className="flex bg-gray-800 rounded-lg p-1">
              <button
                onClick={() => setView('grid')}
                className={`px-3 py-1 rounded ${view === 'grid' ? 'bg-blue-600' : 'hover:bg-gray-700'} transition-colors`}
              >
                <Grid3x3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setView('list')}
                className={`px-3 py-1 rounded ${view === 'list' ? 'bg-blue-600' : 'hover:bg-gray-700'} transition-colors`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <LoadingSkeleton key={i} />
            ))}
          </div>
        ) : (
          <>
            {/* Empty State */}
            {filteredAssets.length === 0 ? (
              <div className="text-center py-16">
                <div className="text-6xl mb-4">📦</div>
                <h3 className="text-xl font-semibold mb-2">No assets found</h3>
                <p className="text-gray-400 mb-6">
                  {search || filter !== 'all'
                    ? 'Try adjusting your search or filters'
                    : 'Start by generating your first 3D asset'}
                </p>
                <Link
                  href="/generate"
                  className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
                >
                  Generate Asset
                </Link>
              </div>
            ) : (
              /* Assets Grid/List */
              view === 'grid' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredAssets.map((asset) => (
                    <AssetCardGrid
                      key={asset.id}
                      asset={asset}
                      onClick={() => setSelectedAsset(asset)}
                      onDownload={(format) => handleDownload(asset, format)}
                    />
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredAssets.map((asset) => (
                    <AssetCardList
                      key={asset.id}
                      asset={asset}
                      onClick={() => setSelectedAsset(asset)}
                      onDownload={(format) => handleDownload(asset, format)}
                    />
                  ))}
                </div>
              )
            )}
          </>
        )}
      </div>

      {/* Asset Detail Modal */}
      {selectedAsset && (
        <AssetDetailModal
          asset={selectedAsset}
          isOpen={!!selectedAsset}
          onClose={() => setSelectedAsset(null)}
          onDownload={(format) => handleDownload(selectedAsset, format)}
          onDelete={() => handleDelete(selectedAsset)}
          onShare={() => handleShare(selectedAsset)}
        />
      )}
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden animate-pulse-slow">
      <div className="aspect-square bg-gray-800"></div>
      <div className="p-4 space-y-3">
        <div className="h-5 bg-gray-800 rounded w-3/4"></div>
        <div className="h-4 bg-gray-800 rounded w-1/2"></div>
        <div className="h-4 bg-gray-800 rounded w-2/3"></div>
        <div className="flex gap-2 mt-4">
          <div className="flex-1 h-10 bg-gray-800 rounded"></div>
          <div className="w-10 h-10 bg-gray-800 rounded"></div>
        </div>
      </div>
    </div>
  )
}

function AssetCardGrid({
  asset,
  onClick,
  onDownload
}: {
  asset: Asset
  onClick: () => void
  onDownload: (format: string) => void
}) {
  return (
    <div
      className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden hover:border-blue-500/50 transition-all group cursor-pointer"
      onClick={onClick}
    >
      {/* Thumbnail */}
      <div className="aspect-square bg-gradient-to-br from-blue-500/10 to-purple-500/10 flex items-center justify-center relative overflow-hidden">
        <span className="text-6xl group-hover:scale-110 transition-transform">
          {asset.type === 'weapon' ? '⚔️' :
           asset.type === 'creature' ? '🐉' :
           '📦'}
        </span>
        <div className="absolute top-2 right-2">
          <div className="bg-black/50 backdrop-blur-sm px-2 py-1 rounded text-xs">
            {asset.style}
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="font-semibold mb-2 group-hover:text-blue-400 transition-colors">
          {asset.name}
        </h3>
        <div className="text-sm text-gray-400 space-y-1">
          <div>{asset.polyCount.toLocaleString()} polygons</div>
          <div>{asset.size} • {asset.downloads} downloads</div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-4">
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDownload('GLB')
            }}
            className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
          >
            Download
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onClick()
            }}
            className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

function AssetCardList({
  asset,
  onClick,
  onDownload
}: {
  asset: Asset
  onClick: () => void
  onDownload: (format: string) => void
}) {
  return (
    <div
      className="bg-gray-900/50 border border-gray-800 rounded-xl p-4 hover:border-blue-500/50 transition-all group flex items-center gap-4 cursor-pointer"
      onClick={onClick}
    >
      {/* Thumbnail */}
      <div className="w-20 h-20 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-lg flex items-center justify-center flex-shrink-0">
        <span className="text-3xl">
          {asset.type === 'weapon' ? '⚔️' :
           asset.type === 'creature' ? '🐉' :
           '📦'}
        </span>
      </div>

      {/* Info */}
      <div className="flex-1 grid grid-cols-4 gap-4 items-center">
        <div>
          <div className="font-semibold group-hover:text-blue-400 transition-colors">
            {asset.name}
          </div>
          <div className="text-sm text-gray-400">{asset.type}</div>
        </div>
        <div className="text-sm text-gray-400">
          {asset.polyCount.toLocaleString()} polys
        </div>
        <div className="text-sm text-gray-400">
          {asset.size}
        </div>
        <div className="text-sm text-gray-400">
          {asset.downloads} downloads
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2 flex-shrink-0">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDownload('GLB')
          }}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
        >
          Download
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onClick()
          }}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
          </svg>
        </button>
      </div>
    </div>
  )
}
