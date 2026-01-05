/**
 * StaticWaves POD Engine - Main Dashboard
 * Advanced analytics, campaign management, and real-time monitoring
 */

import React, { useState, useEffect } from 'react'
import {
  BarChart3, TrendingUp, Package, DollarSign, Users, Settings,
  Calendar, Play, Pause, RefreshCw, Download, Upload, Eye,
  CheckCircle, XCircle, Clock, AlertCircle
} from 'lucide-react'

interface DashboardStats {
  period_days: number
  total_designs: number
  total_products: number
  published_products: number
  total_revenue: number
  total_profit: number
  platform_stats: Record<string, number>
  avg_profit_per_product: number
}

interface Design {
  id: string
  filename: string
  width: number
  height: number
  status: string
  created_at: string
  tags: string[]
}

interface Product {
  id: string
  title: string
  product_type: string
  sale_price: number
  profit_margin: number
  platform: string
  status: string
  platform_url?: string
  created_at: string
}

interface Campaign {
  id: string
  name: string
  design_count: number
  designs_generated: number
  products_created: number
  status: string
  created_at: string
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'designs' | 'products' | 'campaigns' | 'analytics'>('overview')
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [designs, setDesigns] = useState<Design[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(true)

  // API base URL
  const API_BASE = 'http://localhost:8000/api'
  const token = localStorage.getItem('token')

  // Fetch dashboard data
  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      const headers = { 'Authorization': `Bearer ${token}` }

      const [statsRes, designsRes, productsRes, campaignsRes] = await Promise.all([
        fetch(`${API_BASE}/analytics/dashboard?days=30`, { headers }),
        fetch(`${API_BASE}/designs?limit=10`, { headers }),
        fetch(`${API_BASE}/products?limit=10`, { headers }),
        fetch(`${API_BASE}/campaigns?limit=10`, { headers })
      ])

      setStats(await statsRes.json())
      setDesigns(await designsRes.json())
      setProducts(await productsRes.json())
      setCampaigns(await campaignsRes.json())
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusColor = (status: string) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-800',
      processing: 'bg-blue-100 text-blue-800',
      published: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      running: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'published':
      case 'completed':
        return <CheckCircle className="w-4 h-4" />
      case 'processing':
      case 'running':
        return <Clock className="w-4 h-4 animate-spin" />
      case 'failed':
        return <XCircle className="w-4 h-4" />
      default:
        return <AlertCircle className="w-4 h-4" />
    }
  }

  // Overview Tab
  const OverviewTab = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Designs"
          value={stats?.total_designs || 0}
          icon={<Package className="w-6 h-6" />}
          color="bg-blue-500"
        />
        <StatCard
          title="Published Products"
          value={stats?.published_products || 0}
          icon={<TrendingUp className="w-6 h-6" />}
          color="bg-green-500"
        />
        <StatCard
          title="Total Revenue"
          value={formatCurrency(stats?.total_revenue || 0)}
          icon={<DollarSign className="w-6 h-6" />}
          color="bg-purple-500"
        />
        <StatCard
          title="Total Profit"
          value={formatCurrency(stats?.total_profit || 0)}
          icon={<BarChart3 className="w-6 h-6" />}
          color="bg-orange-500"
        />
      </div>

      {/* Platform Distribution */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Platform Distribution</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(stats?.platform_stats || {}).map(([platform, count]) => (
            <div key={platform} className="text-center">
              <div className="text-2xl font-bold text-blue-600">{count}</div>
              <div className="text-sm text-gray-600 capitalize">{platform}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <QuickAction
          title="Upload Design"
          description="Add a new design to your library"
          icon={<Upload className="w-8 h-8" />}
          onClick={() => setActiveTab('designs')}
        />
        <QuickAction
          title="Create Product"
          description="Turn a design into a product"
          icon={<Package className="w-8 h-8" />}
          onClick={() => setActiveTab('products')}
        />
        <QuickAction
          title="New Campaign"
          description="Start a batch generation campaign"
          icon={<Play className="w-8 h-8" />}
          onClick={() => setActiveTab('campaigns')}
        />
      </div>
    </div>
  )

  // Designs Tab
  const DesignsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Designs</h2>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700">
          <Upload className="w-4 h-4" />
          Upload Design
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {designs.map((design) => (
          <div key={design.id} className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition">
            <div className="aspect-square bg-gray-200 relative">
              <img
                src={`${API_BASE}/designs/${design.id}/preview?width=400`}
                alt={design.filename}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-2 right-2">
                <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(design.status)}`}>
                  {design.status}
                </span>
              </div>
            </div>
            <div className="p-4">
              <h3 className="font-semibold truncate">{design.filename}</h3>
              <p className="text-sm text-gray-600">{design.width} × {design.height}</p>
              <div className="mt-2 flex flex-wrap gap-1">
                {design.tags.map((tag, i) => (
                  <span key={i} className="px-2 py-1 bg-gray-100 text-xs rounded">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="mt-4 flex gap-2">
                <button className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 text-sm">
                  Create Product
                </button>
                <button className="p-2 border rounded hover:bg-gray-50">
                  <Eye className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  // Products Tab
  const ProductsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Products</h2>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700">
          <Package className="w-4 h-4" />
          Create Product
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Platform</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {products.map((product) => (
              <tr key={product.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="font-medium">{product.title}</div>
                  <div className="text-sm text-gray-500">{formatDate(product.created_at)}</div>
                </td>
                <td className="px-6 py-4 capitalize">{product.product_type}</td>
                <td className="px-6 py-4 capitalize">{product.platform}</td>
                <td className="px-6 py-4">{formatCurrency(product.sale_price)}</td>
                <td className="px-6 py-4 font-medium text-green-600">
                  {formatCurrency(product.profit_margin)}
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${getStatusColor(product.status)}`}>
                    {getStatusIcon(product.status)}
                    {product.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  {product.platform_url && (
                    <a
                      href={product.platform_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-sm"
                    >
                      View
                    </a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )

  // Campaigns Tab
  const CampaignsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Campaigns</h2>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700">
          <Play className="w-4 h-4" />
          New Campaign
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {campaigns.map((campaign) => (
          <div key={campaign.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-semibold text-lg">{campaign.name}</h3>
                <p className="text-sm text-gray-600">{formatDate(campaign.created_at)}</p>
              </div>
              <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(campaign.status)}`}>
                {campaign.status}
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Progress</span>
                <span className="font-medium">
                  {campaign.designs_generated} / {campaign.design_count}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${(campaign.designs_generated / campaign.design_count) * 100}%` }}
                />
              </div>

              <div className="grid grid-cols-2 gap-4 pt-3 border-t">
                <div>
                  <div className="text-2xl font-bold text-blue-600">{campaign.designs_generated}</div>
                  <div className="text-sm text-gray-600">Designs</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-600">{campaign.products_created}</div>
                  <div className="text-sm text-gray-600">Products</div>
                </div>
              </div>

              <div className="flex gap-2 pt-3">
                <button className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 text-sm">
                  View Details
                </button>
                {campaign.status === 'running' && (
                  <button className="px-4 border rounded hover:bg-gray-50">
                    <Pause className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  // Analytics Tab
  const AnalyticsTab = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Analytics & Insights</h2>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <h3 className="font-semibold text-gray-700">Avg Profit/Product</h3>
          </div>
          <p className="text-3xl font-bold text-green-600">
            {formatCurrency(stats?.avg_profit_per_product || 0)}
          </p>
          <p className="text-sm text-gray-600 mt-1">Per published product</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <Package className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-700">Conversion Rate</h3>
          </div>
          <p className="text-3xl font-bold text-blue-600">
            {stats && stats.total_designs > 0
              ? Math.round((stats.published_products / stats.total_designs) * 100)
              : 0}%
          </p>
          <p className="text-sm text-gray-600 mt-1">Designs to published products</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <DollarSign className="w-5 h-5 text-purple-600" />
            <h3 className="font-semibold text-gray-700">Total Revenue</h3>
          </div>
          <p className="text-3xl font-bold text-purple-600">
            {formatCurrency(stats?.total_revenue || 0)}
          </p>
          <p className="text-sm text-gray-600 mt-1">Last {stats?.period_days || 30} days</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="w-5 h-5 text-orange-600" />
            <h3 className="font-semibold text-gray-700">Profit Margin</h3>
          </div>
          <p className="text-3xl font-bold text-orange-600">
            {stats && stats.total_revenue > 0
              ? Math.round((stats.total_profit / stats.total_revenue) * 100)
              : 0}%
          </p>
          <p className="text-sm text-gray-600 mt-1">Average margin</p>
        </div>
      </div>

      {/* Platform Performance */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Platform Performance</h3>
        <div className="space-y-4">
          {Object.entries(stats?.platform_stats || {}).map(([platform, count]) => {
            const total = Object.values(stats?.platform_stats || {}).reduce((a: number, b: number) => a + b, 0)
            const percentage = total > 0 ? Math.round((Number(count) / total) * 100) : 0

            return (
              <div key={platform}>
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium capitalize">{platform}</span>
                  <span className="text-sm text-gray-600">{count} products ({percentage}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full transition-all"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Cost Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Cost Breakdown</h3>
          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">AI Generation Cost</span>
              <span className="font-semibold">
                {formatCurrency((stats?.total_designs || 0) * 0.06)}
              </span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Platform Fees (est.)</span>
              <span className="font-semibold">
                {formatCurrency((stats?.total_revenue || 0) * 0.15)}
              </span>
            </div>
            <div className="flex justify-between py-2 font-bold text-lg">
              <span>Net Profit</span>
              <span className="text-green-600">
                {formatCurrency(
                  (stats?.total_profit || 0) -
                  (stats?.total_designs || 0) * 0.06 -
                  (stats?.total_revenue || 0) * 0.15
                )}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Production Summary</h3>
          <div className="space-y-3">
            <div className="flex justify-between py-2">
              <span className="text-gray-600">Total Designs Created</span>
              <span className="font-semibold">{stats?.total_designs || 0}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-gray-600">Products Generated</span>
              <span className="font-semibold">{stats?.total_products || 0}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-gray-600">Successfully Published</span>
              <span className="font-semibold text-green-600">{stats?.published_products || 0}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-gray-600">Products Per Design</span>
              <span className="font-semibold">
                {stats && stats.total_designs > 0
                  ? (stats.total_products / stats.total_designs).toFixed(1)
                  : 0}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-600" />
          Growth Recommendations
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-semibold text-sm mb-2">Expand to More Platforms</h4>
            <p className="text-xs text-gray-600">
              Currently using {Object.keys(stats?.platform_stats || {}).length} platforms.
              Consider expanding to increase reach.
            </p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-semibold text-sm mb-2">Optimize Product Mix</h4>
            <p className="text-xs text-gray-600">
              Avg profit of {formatCurrency(stats?.avg_profit_per_product || 0)}.
              Test higher price points for premium designs.
            </p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-semibold text-sm mb-2">Scale Production</h4>
            <p className="text-xs text-gray-600">
              {stats?.total_designs || 0} designs in {stats?.period_days || 30} days.
              Run more campaigns to increase output.
            </p>
          </div>
        </div>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">StaticWaves POD Engine</h1>
            <div className="flex items-center gap-4">
              <button onClick={fetchDashboardData} className="p-2 hover:bg-gray-100 rounded">
                <RefreshCw className="w-5 h-5" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'designs', label: 'Designs', icon: Package },
              { id: 'products', label: 'Products', icon: TrendingUp },
              { id: 'campaigns', label: 'Campaigns', icon: Calendar },
              { id: 'analytics', label: 'Analytics', icon: Users }
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-3 py-4 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'designs' && <DesignsTab />}
        {activeTab === 'products' && <ProductsTab />}
        {activeTab === 'campaigns' && <CampaignsTab />}
        {activeTab === 'analytics' && <AnalyticsTab />}
      </main>
    </div>
  )
}

// Helper Components

const StatCard = ({ title, value, icon, color }: any) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-600 text-sm">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
      </div>
      <div className={`${color} text-white p-3 rounded-lg`}>
        {icon}
      </div>
    </div>
  </div>
)

const QuickAction = ({ title, description, icon, onClick }: any) => (
  <button
    onClick={onClick}
    className="bg-white rounded-lg shadow p-6 text-left hover:shadow-lg transition group"
  >
    <div className="flex items-start gap-4">
      <div className="bg-blue-100 text-blue-600 p-3 rounded-lg group-hover:bg-blue-600 group-hover:text-white transition">
        {icon}
      </div>
      <div>
        <h3 className="font-semibold">{title}</h3>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
      </div>
    </div>
  </button>
)
