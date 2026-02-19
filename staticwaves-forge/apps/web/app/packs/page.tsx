'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Plus, TrendingUp, Download, DollarSign, Package } from 'lucide-react'
import PackCreationWizard from '@/components/PackCreationWizard'
import { useToast } from '@/components/Toast'

interface Pack {
  id: string
  name: string
  description: string
  assetCount: number
  price: number
  created: string
  status: 'draft' | 'published'
  downloads: number
  revenue: number
}

interface PackData {
  name: string
  description: string
  price: number
  category: string
  assets: string[]
  settings: {
    includeAnimations: boolean
    includeLODs: boolean
    formats: string[]
  }
}

export default function PacksPage() {
  const [packs, setPacks] = useState<Pack[]>([
    {
      id: '1',
      name: 'Fantasy Creatures Starter',
      description: '25 stylized fantasy creatures with animations',
      assetCount: 25,
      price: 39,
      created: '2024-01-10',
      status: 'published',
      downloads: 127,
      revenue: 4953
    },
    {
      id: '2',
      name: 'Sci-Fi Props Mega Kit',
      description: '60 sci-fi props for futuristic environments',
      assetCount: 60,
      price: 49,
      created: '2024-01-08',
      status: 'published',
      downloads: 89,
      revenue: 4361
    },
    {
      id: '3',
      name: 'Medieval Weapons Collection',
      description: 'Complete set of medieval weaponry',
      assetCount: 30,
      price: 29,
      created: '2024-01-15',
      status: 'draft',
      downloads: 0,
      revenue: 0
    }
  ])

  const [isWizardOpen, setIsWizardOpen] = useState(false)
  const { showToast } = useToast()

  const totalRevenue = packs.reduce((sum, pack) => sum + pack.revenue, 0)
  const totalDownloads = packs.reduce((sum, pack) => sum + pack.downloads, 0)

  const handleCreatePack = (packData: PackData) => {
    const newPack: Pack = {
      id: String(packs.length + 1),
      name: packData.name,
      description: packData.description,
      assetCount: packData.assets.length,
      price: packData.price,
      created: new Date().toISOString().split('T')[0],
      status: 'draft',
      downloads: 0,
      revenue: 0
    }
    setPacks([...packs, newPack])
    showToast(`Pack "${packData.name}" created successfully!`, 'success')
  }

  const handleGeneratePreset = (name: string) => {
    showToast(`Generating "${name}"... This may take a few minutes`, 'info')
    setTimeout(() => {
      showToast(`"${name}" generated successfully!`, 'success')
    }, 2000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Asset Packs</h1>
            <p className="text-gray-400">Create and manage marketplace asset packs</p>
          </div>

          <button
            onClick={() => setIsWizardOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
          >
            <Plus className="w-5 h-5" />
            Create Pack
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-gray-400">Total Revenue</div>
              <DollarSign className="w-5 h-5 text-green-400" />
            </div>
            <div className="text-3xl font-bold text-green-400">
              ${totalRevenue.toLocaleString()}
            </div>
            <div className="text-xs text-gray-500 mt-1">+12% from last month</div>
          </div>
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-gray-400">Total Downloads</div>
              <Download className="w-5 h-5 text-blue-400" />
            </div>
            <div className="text-3xl font-bold">{totalDownloads.toLocaleString()}</div>
            <div className="text-xs text-gray-500 mt-1">+8% from last month</div>
          </div>
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-gray-400">Published Packs</div>
              <Package className="w-5 h-5 text-purple-400" />
            </div>
            <div className="text-3xl font-bold">
              {packs.filter(p => p.status === 'published').length}
            </div>
            <div className="text-xs text-gray-500 mt-1">{packs.filter(p => p.status === 'draft').length} drafts</div>
          </div>
        </div>

        {/* Packs Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
          {packs.map((pack) => (
            <PackCard key={pack.id} pack={pack} />
          ))}
        </div>

        {/* Pack Presets */}
        <div className="mt-12">
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp className="w-6 h-6 text-blue-400" />
            <h2 className="text-2xl font-bold">Pre-Configured Packs</h2>
          </div>
          <p className="text-gray-400 mb-6">
            Generate these pre-configured asset packs with one click
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <PresetCard
              name="Low-Poly Environment Pack"
              description="40 buildings and terrain chunks for mobile games"
              assets={40}
              price={29}
              onGenerate={handleGeneratePreset}
            />
            <PresetCard
              name="Weapon Arsenal Collection"
              description="30 game-ready weapons with LODs"
              assets={30}
              price={35}
              onGenerate={handleGeneratePreset}
            />
            <PresetCard
              name="Creature Starter Bundle"
              description="15 animated fantasy creatures"
              assets={15}
              price={45}
              onGenerate={handleGeneratePreset}
            />
            <PresetCard
              name="Sci-Fi Environment Pack"
              description="50 futuristic props and structures"
              assets={50}
              price={39}
              onGenerate={handleGeneratePreset}
            />
          </div>
        </div>
      </div>

      {/* Pack Creation Wizard */}
      <PackCreationWizard
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
        onComplete={handleCreatePack}
      />
    </div>
  )
}

function PackCard({ pack }: { pack: Pack }) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 hover:border-blue-500/50 transition-all group">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-xl font-semibold group-hover:text-blue-400 transition-colors">
              {pack.name}
            </h3>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              pack.status === 'published'
                ? 'bg-green-500/20 text-green-400'
                : 'bg-yellow-500/20 text-yellow-400'
            }`}>
              {pack.status}
            </span>
          </div>
          <p className="text-sm text-gray-400">{pack.description}</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div>
          <div className="text-sm text-gray-400">Assets</div>
          <div className="text-xl font-semibold">{pack.assetCount}</div>
        </div>
        <div>
          <div className="text-sm text-gray-400">Downloads</div>
          <div className="text-xl font-semibold">{pack.downloads}</div>
        </div>
        <div>
          <div className="text-sm text-gray-400">Revenue</div>
          <div className="text-xl font-semibold text-green-400">
            ${pack.revenue.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Price */}
      <div className="text-2xl font-bold text-blue-400 mb-6">
        ${pack.price}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Link
          href={`/packs/${pack.id}/edit`}
          className="flex-1 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-center font-medium transition-colors"
        >
          Edit
        </Link>
        <Link
          href={`/packs/${pack.id}/export`}
          className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-center font-medium transition-colors"
        >
          Export
        </Link>
        <button className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
          </svg>
        </button>
      </div>
    </div>
  )
}

function PresetCard({ name, description, assets, price, onGenerate }: {
  name: string
  description: string
  assets: number
  price: number
  onGenerate: (name: string) => void
}) {
  return (
    <div className="bg-gray-900/30 border border-gray-800 rounded-xl p-6 hover:border-blue-500/50 transition-all group">
      <div className="flex items-start gap-4">
        <div className="p-3 bg-blue-500/10 rounded-lg">
          <Package className="w-6 h-6 text-blue-400" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold mb-2 group-hover:text-blue-400 transition-colors">
            {name}
          </h3>
          <p className="text-sm text-gray-400 mb-4">{description}</p>

          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-500">{assets} assets • ${price}</div>
            </div>
            <button
              onClick={() => onGenerate(name)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
            >
              Generate
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
