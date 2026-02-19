'use client'

import Link from 'next/link'
import { useState } from 'react'
import {
  TrendingUp,
  Package,
  Download,
  DollarSign,
  Clock,
  Sparkles,
  BarChart3,
  Activity
} from 'lucide-react'

interface Asset {
  id: string
  name: string
  type: string
  status: 'completed' | 'processing' | 'failed'
  polyCount: number
  created: string
}

export default function DashboardPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d')

  const stats = {
    totalAssets: 247,
    totalJobs: 312,
    totalPacks: 12,
    monthlyGenerated: 89,
    growth: {
      assets: 12,
      jobs: 8,
      packs: 25,
      monthly: 15
    }
  }

  const recentAssets: Asset[] = [
    { id: '1', name: 'Medieval Sword', type: 'weapon', status: 'completed', polyCount: 5234, created: '2 hours ago' },
    { id: '2', name: 'Fantasy Dragon', type: 'creature', status: 'completed', polyCount: 15234, created: '5 hours ago' },
    { id: '3', name: 'Sci-Fi Crate', type: 'prop', status: 'processing', polyCount: 3121, created: '1 day ago' },
    { id: '4', name: 'Battle Axe', type: 'weapon', status: 'completed', polyCount: 4521, created: '2 days ago' },
    { id: '5', name: 'Space Station', type: 'building', status: 'failed', polyCount: 0, created: '3 days ago' }
  ]

  // Mock chart data for the last 30 days
  const chartData = Array.from({ length: 30 }, (_, i) => ({
    day: i + 1,
    generations: Math.floor(Math.random() * 15) + 5,
    downloads: Math.floor(Math.random() * 25) + 10
  }))

  const maxGenerations = Math.max(...chartData.map(d => d.generations))
  const maxDownloads = Math.max(...chartData.map(d => d.downloads))

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
              <Activity className="w-8 h-8 text-blue-400" />
              Dashboard
            </h1>
            <p className="text-gray-400">Overview of your asset generation activity</p>
          </div>

          {/* Time Range Selector */}
          <div className="flex bg-gray-800 rounded-lg p-1">
            {(['7d', '30d', '90d'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  timeRange === range ? 'bg-blue-600' : 'hover:bg-gray-700'
                }`}
              >
                {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
              </button>
            ))}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={Package}
            label="Total Assets"
            value={stats.totalAssets}
            growth={stats.growth.assets}
            color="blue"
          />
          <StatCard
            icon={Sparkles}
            label="Total Jobs"
            value={stats.totalJobs}
            growth={stats.growth.jobs}
            color="purple"
          />
          <StatCard
            icon={TrendingUp}
            label="Asset Packs"
            value={stats.totalPacks}
            growth={stats.growth.packs}
            color="green"
          />
          <StatCard
            icon={Clock}
            label="This Month"
            value={stats.monthlyGenerated}
            growth={stats.growth.monthly}
            color="yellow"
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Generation Activity Chart */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-400" />
                  Generation Activity
                </h3>
                <p className="text-sm text-gray-400 mt-1">Daily asset generations</p>
              </div>
            </div>

            {/* Simple Bar Chart */}
            <div className="h-48 flex items-end justify-between gap-1">
              {chartData.map((data, i) => (
                <div
                  key={i}
                  className="flex-1 bg-gradient-to-t from-blue-600 to-blue-400 rounded-t hover:opacity-80 transition-opacity cursor-pointer relative group"
                  style={{
                    height: `${(data.generations / maxGenerations) * 100}%`,
                    minHeight: '8px'
                  }}
                  title={`Day ${data.day}: ${data.generations} generations`}
                >
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                    {data.generations} gen
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
              <span>Day 1</span>
              <span>Day {chartData.length}</span>
            </div>
          </div>

          {/* Download Activity Chart */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Download className="w-5 h-5 text-green-400" />
                  Download Activity
                </h3>
                <p className="text-sm text-gray-400 mt-1">Daily asset downloads</p>
              </div>
            </div>

            {/* Simple Area Chart */}
            <div className="h-48 flex items-end justify-between gap-1">
              {chartData.map((data, i) => (
                <div
                  key={i}
                  className="flex-1 bg-gradient-to-t from-green-600 to-green-400 rounded-t hover:opacity-80 transition-opacity cursor-pointer relative group"
                  style={{
                    height: `${(data.downloads / maxDownloads) * 100}%`,
                    minHeight: '8px'
                  }}
                  title={`Day ${data.day}: ${data.downloads} downloads`}
                >
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                    {data.downloads} dl
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
              <span>Day 1</span>
              <span>Day {chartData.length}</span>
            </div>
          </div>
        </div>

        {/* Recent Assets and Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Assets */}
          <div className="lg:col-span-2 bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Recent Assets</h3>
              <Link
                href="/library"
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                View All →
              </Link>
            </div>

            <div className="space-y-3">
              {recentAssets.map((asset) => (
                <div
                  key={asset.id}
                  className="flex items-center gap-4 p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors"
                >
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-2xl">
                      {asset.type === 'weapon' ? '⚔️' :
                       asset.type === 'creature' ? '🐉' :
                       asset.type === 'building' ? '🏛️' :
                       '📦'}
                    </span>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{asset.name}</div>
                    <div className="text-sm text-gray-400">
                      {asset.status === 'completed' && `${asset.polyCount.toLocaleString()} polys`}
                      {asset.status === 'processing' && 'Processing...'}
                      {asset.status === 'failed' && 'Generation failed'}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-sm text-gray-500">{asset.created}</div>
                    <div className={`px-2 py-1 rounded text-xs font-medium ${
                      asset.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                      asset.status === 'processing' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {asset.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-6">Quick Actions</h3>

            <div className="space-y-3">
              <Link
                href="/generate"
                className="flex items-center gap-3 p-4 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors group"
              >
                <Sparkles className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-medium">Generate Asset</div>
                  <div className="text-xs opacity-90">Create new 3D model</div>
                </div>
              </Link>

              <Link
                href="/packs"
                className="flex items-center gap-3 p-4 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors group"
              >
                <Package className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-medium">Create Pack</div>
                  <div className="text-xs text-gray-400">Bundle assets together</div>
                </div>
              </Link>

              <Link
                href="/library"
                className="flex items-center gap-3 p-4 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors group"
              >
                <Download className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-medium">Browse Library</div>
                  <div className="text-xs text-gray-400">View all assets</div>
                </div>
              </Link>

              <button className="w-full flex items-center gap-3 p-4 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors group">
                <DollarSign className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <div className="text-left">
                  <div className="font-medium">View Analytics</div>
                  <div className="text-xs text-gray-400">Detailed insights</div>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Usage Meter */}
        <div className="mt-8 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold">Monthly Usage</h3>
              <p className="text-sm text-gray-400 mt-1">
                {stats.monthlyGenerated} of 100 generations used
              </p>
            </div>
            <div className="text-2xl font-bold text-blue-400">
              {100 - stats.monthlyGenerated} left
            </div>
          </div>

          {/* Progress Bar */}
          <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-600 to-purple-600 rounded-full transition-all duration-500"
              style={{ width: `${(stats.monthlyGenerated / 100) * 100}%` }}
            />
          </div>

          <div className="mt-4 flex items-center justify-between text-sm">
            <span className="text-gray-400">Resets in 12 days</span>
            <Link href="/settings" className="text-blue-400 hover:text-blue-300 transition-colors">
              Upgrade Plan →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({
  icon: Icon,
  label,
  value,
  growth,
  color
}: {
  icon: any
  label: string
  value: number
  growth: number
  color: 'blue' | 'purple' | 'green' | 'yellow'
}) {
  const colors = {
    blue: 'text-blue-400 bg-blue-500/10',
    purple: 'text-purple-400 bg-purple-500/10',
    green: 'text-green-400 bg-green-500/10',
    yellow: 'text-yellow-400 bg-yellow-500/10'
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all group">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colors[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="flex items-center gap-1 text-sm">
          <TrendingUp className="w-4 h-4 text-green-400" />
          <span className="text-green-400">+{growth}%</span>
        </div>
      </div>

      <div className="text-3xl font-bold mb-1">{value.toLocaleString()}</div>
      <div className="text-sm text-gray-400">{label}</div>
    </div>
  )
}
