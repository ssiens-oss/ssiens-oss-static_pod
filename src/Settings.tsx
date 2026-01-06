/**
 * StaticWaves POD Engine - Settings Panel
 * Manage API keys, preferences, and account settings
 */

import React, { useState, useEffect } from 'react'
import {
  Settings as SettingsIcon, Key, Globe, Bell, User, Shield,
  Save, Eye, EyeOff, CheckCircle, AlertCircle, RefreshCw,
  Trash2, Download, Upload, Copy, Check
} from 'lucide-react'

interface UserSettings {
  email: string
  username: string
  printify_api_key?: string
  printify_shop_id?: string
  shopify_store_url?: string
  shopify_access_token?: string
}

export default function Settings() {
  const [settings, setSettings] = useState<UserSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  // Visibility toggles for API keys
  const [showPrintifyKey, setShowPrintifyKey] = useState(false)
  const [showShopifyToken, setShowShopifyToken] = useState(false)
  const [copied, setCopied] = useState<string | null>(null)

  // Form state
  const [printifyApiKey, setPrintifyApiKey] = useState('')
  const [printifyShopId, setPrintifyShopId] = useState('')
  const [shopifyStoreUrl, setShopifyStoreUrl] = useState('')
  const [shopifyAccessToken, setShopifyAccessToken] = useState('')

  const API_BASE = 'http://localhost:8000/api'
  const token = localStorage.getItem('token')

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await fetch(`${API_BASE}/users/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setSettings(data)
        setPrintifyApiKey(data.printify_api_key || '')
        setPrintifyShopId(data.printify_shop_id || '')
        setShopifyStoreUrl(data.shopify_store_url || '')
        setShopifyAccessToken(data.shopify_access_token || '')
      }
    } catch (err) {
      setError('Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setError('')
    setSaved(false)

    try {
      const response = await fetch(`${API_BASE}/users/me/settings`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          printify_api_key: printifyApiKey,
          printify_shop_id: printifyShopId,
          shopify_store_url: shopifyStoreUrl,
          shopify_access_token: shopifyAccessToken
        })
      })

      if (!response.ok) {
        throw new Error('Failed to save settings')
      }

      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
      fetchSettings()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleCopy = async (text: string, key: string) => {
    await navigator.clipboard.writeText(text)
    setCopied(key)
    setTimeout(() => setCopied(null), 2000)
  }

  const maskApiKey = (key: string) => {
    if (!key || key.length < 8) return '••••••••'
    return key.substring(0, 4) + '••••••••' + key.substring(key.length - 4)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="bg-gradient-to-br from-blue-500 to-indigo-500 p-3 rounded-lg">
          <SettingsIcon className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold">Settings</h2>
          <p className="text-gray-600">Manage your account and integrations</p>
        </div>
      </div>

      {/* Success/Error Messages */}
      {saved && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <p className="text-green-800">Settings saved successfully!</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Settings Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Account Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-blue-600" />
              Account Information
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={settings?.username || ''}
                  disabled
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={settings?.email || ''}
                  disabled
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600"
                />
              </div>
            </div>
          </div>

          {/* Printify Integration */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <Key className="w-5 h-5 text-purple-600" />
              Printify Integration
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Key
                </label>
                <div className="relative">
                  <input
                    type={showPrintifyKey ? 'text' : 'password'}
                    value={printifyApiKey}
                    onChange={(e) => setPrintifyApiKey(e.target.value)}
                    placeholder="Enter your Printify API key"
                    className="w-full px-4 py-2 pr-24 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  />
                  <div className="absolute right-2 top-2 flex gap-1">
                    <button
                      onClick={() => setShowPrintifyKey(!showPrintifyKey)}
                      className="p-1 hover:bg-gray-100 rounded"
                      title={showPrintifyKey ? 'Hide' : 'Show'}
                    >
                      {showPrintifyKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                    {printifyApiKey && (
                      <button
                        onClick={() => handleCopy(printifyApiKey, 'printify')}
                        className="p-1 hover:bg-gray-100 rounded"
                        title="Copy"
                      >
                        {copied === 'printify' ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                      </button>
                    )}
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Get your API key from{' '}
                  <a href="https://printify.com" target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:underline">
                    Printify Settings
                  </a>
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Shop ID
                </label>
                <input
                  type="text"
                  value={printifyShopId}
                  onChange={(e) => setPrintifyShopId(e.target.value)}
                  placeholder="e.g., 12345678"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Shopify Integration */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <Globe className="w-5 h-5 text-green-600" />
              Shopify Integration
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Store URL
                </label>
                <input
                  type="text"
                  value={shopifyStoreUrl}
                  onChange={(e) => setShopifyStoreUrl(e.target.value)}
                  placeholder="your-store.myshopify.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Access Token
                </label>
                <div className="relative">
                  <input
                    type={showShopifyToken ? 'text' : 'password'}
                    value={shopifyAccessToken}
                    onChange={(e) => setShopifyAccessToken(e.target.value)}
                    placeholder="Enter your Shopify access token"
                    className="w-full px-4 py-2 pr-24 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600 focus:border-transparent"
                  />
                  <div className="absolute right-2 top-2 flex gap-1">
                    <button
                      onClick={() => setShowShopifyToken(!showShopifyToken)}
                      className="p-1 hover:bg-gray-100 rounded"
                      title={showShopifyToken ? 'Hide' : 'Show'}
                    >
                      {showShopifyToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                    {shopifyAccessToken && (
                      <button
                        onClick={() => handleCopy(shopifyAccessToken, 'shopify')}
                        className="p-1 hover:bg-gray-100 rounded"
                        title="Copy"
                      >
                        {copied === 'shopify' ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {saving ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Save Settings
              </>
            )}
          </button>
        </div>

        {/* Sidebar - Quick Info */}
        <div className="space-y-6">
          {/* Account Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-4">Account Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Designs Created</span>
                <span className="font-semibold">{settings?.designs_created || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Products Published</span>
                <span className="font-semibold">{settings?.products_published || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Revenue</span>
                <span className="font-semibold text-green-600">
                  ${(settings?.total_revenue || 0).toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Integration Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5 text-blue-600" />
              Integration Status
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Printify</span>
                {printifyApiKey && printifyShopId ? (
                  <span className="flex items-center gap-1 text-green-600 text-sm">
                    <CheckCircle className="w-4 h-4" />
                    Connected
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-gray-400 text-sm">
                    <AlertCircle className="w-4 h-4" />
                    Not Connected
                  </span>
                )}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Shopify</span>
                {shopifyStoreUrl && shopifyAccessToken ? (
                  <span className="flex items-center gap-1 text-green-600 text-sm">
                    <CheckCircle className="w-4 h-4" />
                    Connected
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-gray-400 text-sm">
                    <AlertCircle className="w-4 h-4" />
                    Not Connected
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-lg flex items-center gap-2 text-sm">
                <Download className="w-4 h-4 text-blue-600" />
                Export Data
              </button>
              <button className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-lg flex items-center gap-2 text-sm">
                <RefreshCw className="w-4 h-4 text-green-600" />
                Refresh Stats
              </button>
              <button className="w-full text-left px-3 py-2 hover:bg-red-50 rounded-lg flex items-center gap-2 text-sm text-red-600">
                <Trash2 className="w-4 h-4" />
                Clear Cache
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
