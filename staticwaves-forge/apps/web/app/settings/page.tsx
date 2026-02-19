'use client'

import { useState } from 'react'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('general')

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Settings</h1>
          <p className="text-gray-400">Configure your StaticWaves Forge experience</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-2">
              {[
                { id: 'general', label: 'General', icon: '⚙️' },
                { id: 'generation', label: 'Generation', icon: '✨' },
                { id: 'export', label: 'Export', icon: '📤' },
                { id: 'api', label: 'API Keys', icon: '🔑' },
                { id: 'billing', label: 'Billing', icon: '💳' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white'
                      : 'hover:bg-gray-800 text-gray-400'
                  }`}
                >
                  <span className="text-xl">{tab.icon}</span>
                  <span className="font-medium">{tab.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="lg:col-span-3">
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              {activeTab === 'general' && <GeneralSettings />}
              {activeTab === 'generation' && <GenerationSettings />}
              {activeTab === 'export' && <ExportSettings />}
              {activeTab === 'api' && <APISettings />}
              {activeTab === 'billing' && <BillingSettings />}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function GeneralSettings() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">General Settings</h2>

      <div>
        <label className="block text-sm font-medium mb-2">Workspace Name</label>
        <input
          type="text"
          defaultValue="My Workspace"
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Default Asset Style</label>
        <select className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:border-blue-500 focus:outline-none">
          <option>Low-Poly</option>
          <option>Realistic</option>
          <option>Stylized</option>
          <option>Voxel</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <input type="checkbox" id="autoSave" className="w-4 h-4 rounded" defaultChecked />
        <label htmlFor="autoSave" className="text-sm">Auto-save generated assets</label>
      </div>

      <div className="flex items-center gap-2">
        <input type="checkbox" id="notifications" className="w-4 h-4 rounded" defaultChecked />
        <label htmlFor="notifications" className="text-sm">Enable email notifications</label>
      </div>

      <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors">
        Save Changes
      </button>
    </div>
  )
}

function GenerationSettings() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Generation Settings</h2>

      <div>
        <label className="block text-sm font-medium mb-2">Default Poly Budget</label>
        <input
          type="number"
          defaultValue={10000}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Target Engine</label>
        <select className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:border-blue-500 focus:outline-none">
          <option>Unity</option>
          <option>Unreal Engine</option>
          <option>Roblox</option>
          <option>Godot</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <input type="checkbox" id="autoRig" className="w-4 h-4 rounded" />
        <label htmlFor="autoRig" className="text-sm">Always include auto-rigging</label>
      </div>

      <div className="flex items-center gap-2">
        <input type="checkbox" id="generateLODs" className="w-4 h-4 rounded" defaultChecked />
        <label htmlFor="generateLODs" className="text-sm">Generate LOD levels automatically</label>
      </div>

      <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors">
        Save Changes
      </button>
    </div>
  )
}

function ExportSettings() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Export Settings</h2>

      <div>
        <label className="block text-sm font-medium mb-2">Default Export Formats</label>
        <div className="space-y-2">
          {['GLB', 'FBX', 'OBJ', 'GLTF'].map((format) => (
            <div key={format} className="flex items-center gap-2">
              <input
                type="checkbox"
                id={`format-${format}`}
                className="w-4 h-4 rounded"
                defaultChecked={['GLB', 'FBX'].includes(format)}
              />
              <label htmlFor={`format-${format}`} className="text-sm">{format}</label>
            </div>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Output Directory</label>
        <input
          type="text"
          defaultValue="/output"
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors">
        Save Changes
      </button>
    </div>
  )
}

function APISettings() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">API Keys</h2>

      <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
        <div className="flex gap-2 text-yellow-400 mb-2">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <span className="font-semibold">Security Warning</span>
        </div>
        <p className="text-sm text-yellow-300/80">
          Never share your API keys publicly. Keep them secure and rotate them regularly.
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">API Key</label>
        <div className="flex gap-2">
          <input
            type="password"
            defaultValue="sk_prod_1234567890abcdef"
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:border-blue-500 focus:outline-none font-mono text-sm"
            readOnly
          />
          <button className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
            Copy
          </button>
        </div>
      </div>

      <div className="flex gap-3">
        <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors">
          Regenerate Key
        </button>
        <button className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg font-semibold transition-colors">
          View Documentation
        </button>
      </div>
    </div>
  )
}

function BillingSettings() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Billing</h2>

      {/* Current Plan */}
      <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-xl p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold mb-2">Creator Plan</h3>
            <p className="text-gray-400">500 assets per month</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">$79</div>
            <div className="text-sm text-gray-400">/month</div>
          </div>
        </div>

        <div className="space-y-2 mb-4">
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>All asset types</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>Auto-rigging & animations</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>API access</span>
          </div>
        </div>

        <button className="w-full px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors">
          Upgrade Plan
        </button>
      </div>

      {/* Usage */}
      <div>
        <h3 className="font-semibold mb-3">Current Usage</h3>
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-400">Assets Generated</span>
            <span>45 / 500</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div className="bg-blue-500 h-full rounded-full" style={{ width: '9%' }} />
          </div>
        </div>
      </div>

      {/* Payment Method */}
      <div>
        <h3 className="font-semibold mb-3">Payment Method</h3>
        <div className="bg-gray-800/50 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-8 bg-gray-700 rounded flex items-center justify-center text-xs font-bold">
              VISA
            </div>
            <div>
              <div className="font-medium">•••• 4242</div>
              <div className="text-sm text-gray-400">Expires 12/25</div>
            </div>
          </div>
          <button className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
            Update
          </button>
        </div>
      </div>
    </div>
  )
}
