'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Asset {
  id: string
  name: string
  type: string
  style: string
  created: string
  thumbnail?: string
  polyCount: number
  status: 'completed' | 'processing' | 'failed'
}

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalAssets: 0,
    activeJobs: 0,
    totalPacks: 0,
    monthlyGenerated: 0
  })

  const [recentAssets, setRecentAssets] = useState<Asset[]>([])

  useEffect(() => {
    // Fetch stats and recent assets
    // Mock data for now
    setStats({
      totalAssets: 127,
      activeJobs: 3,
      totalPacks: 8,
      monthlyGenerated: 45
    })

    setRecentAssets([
      {
        id: '1',
        name: 'Fantasy Sword',
        type: 'weapon',
        style: 'low-poly',
        created: '2 hours ago',
        polyCount: 5234,
        status: 'completed'
      },
      {
        id: '2',
        name: 'Sci-Fi Crate',
        type: 'prop',
        style: 'stylized',
        created: '5 hours ago',
        polyCount: 3121,
        status: 'completed'
      },
      {
        id: '3',
        name: 'Dragon Creature',
        type: 'creature',
        style: 'realistic',
        created: '1 day ago',
        polyCount: 15234,
        status: 'processing'
      }
    ])
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className="text-gray-400">Overview of your 3D asset generation activity</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Assets"
            value={stats.totalAssets}
            icon="📦"
            trend="+12 this week"
          />
          <StatCard
            title="Active Jobs"
            value={stats.activeJobs}
            icon="⏳"
            trend="Processing now"
            trendColor="text-blue-400"
          />
          <StatCard
            title="Asset Packs"
            value={stats.totalPacks}
            icon="🎁"
            trend="+2 this month"
          />
          <StatCard
            title="Monthly Generated"
            value={stats.monthlyGenerated}
            icon="📈"
            trend="90% of quota"
          />
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Assets */}
          <div className="lg:col-span-2 bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Recent Assets</h2>
              <Link
                href="/library"
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                View All →
              </Link>
            </div>

            <div className="space-y-4">
              {recentAssets.map((asset) => (
                <AssetCard key={asset.id} asset={asset} />
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-6">Quick Actions</h2>

            <div className="space-y-3">
              <Link
                href="/generate"
                className="flex items-center gap-3 p-4 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors group"
              >
                <span className="text-2xl">✨</span>
                <div className="flex-1">
                  <div className="font-semibold">Generate Asset</div>
                  <div className="text-xs text-blue-100">Create new 3D asset</div>
                </div>
                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>

              <Link
                href="/packs/create"
                className="flex items-center gap-3 p-4 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors group"
              >
                <span className="text-2xl">📦</span>
                <div className="flex-1">
                  <div className="font-semibold">Create Pack</div>
                  <div className="text-xs text-gray-400">Bundle assets</div>
                </div>
                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>

              <Link
                href="/library?view=batch"
                className="flex items-center gap-3 p-4 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors group"
              >
                <span className="text-2xl">⚡</span>
                <div className="flex-1">
                  <div className="font-semibold">Batch Generate</div>
                  <div className="text-xs text-gray-400">Multiple assets</div>
                </div>
                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>

              <div className="pt-4 border-t border-gray-700">
                <div className="text-sm text-gray-400 mb-2">Usage This Month</div>
                <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                  <div className="bg-blue-500 h-full rounded-full" style={{ width: '90%' }} />
                </div>
                <div className="text-xs text-gray-500 mt-1">45 / 50 assets</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon, trend, trendColor = 'text-green-400' }: {
  title: string
  value: number
  icon: string
  trend: string
  trendColor?: string
}) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 hover:border-blue-500/50 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <span className="text-3xl">{icon}</span>
        <div className="text-right">
          <div className="text-3xl font-bold">{value}</div>
          <div className="text-sm text-gray-400">{title}</div>
        </div>
      </div>
      <div className={`text-xs ${trendColor}`}>{trend}</div>
    </div>
  )
}

function AssetCard({ asset }: { asset: Asset }) {
  const statusColors = {
    completed: 'bg-green-500/20 text-green-400 border-green-500/30',
    processing: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    failed: 'bg-red-500/20 text-red-400 border-red-500/30'
  }

  return (
    <div className="flex items-center gap-4 p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors group">
      {/* Thumbnail Placeholder */}
      <div className="w-16 h-16 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-lg flex items-center justify-center">
        <span className="text-2xl">
          {asset.type === 'weapon' ? '⚔️' :
           asset.type === 'creature' ? '🐉' :
           asset.type === 'prop' ? '📦' : '🎮'}
        </span>
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="font-semibold truncate group-hover:text-blue-400 transition-colors">
          {asset.name}
        </div>
        <div className="text-sm text-gray-400">
          {asset.type} • {asset.style} • {asset.polyCount.toLocaleString()} polys
        </div>
        <div className="text-xs text-gray-500 mt-1">{asset.created}</div>
      </div>

      {/* Status */}
      <div className={`px-3 py-1 rounded-full text-xs font-medium border ${statusColors[asset.status]}`}>
        {asset.status}
      </div>
    </div>
  )
}
