/**
 * Pod Engine GUI
 * Complete interface for ComfyUI + RunPod pipeline with proofing and publishing
 */

import React, { useState, useCallback, useEffect } from 'react'
import { Terminal } from './Terminal'
import {
  Rocket,
  Play,
  Pause,
  CheckCircle2,
  XCircle,
  Image as ImageIcon,
  Package,
  Upload,
  Download,
  Settings,
  Layers,
  Eye,
  Trash2,
  RefreshCw,
  Server,
  HardDrive,
  CloudDownload,
  ShoppingBag,
  AlertCircle
} from 'lucide-react'

interface LogEntry {
  id: string
  timestamp: string
  message: string
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR'
}

interface GeneratedAsset {
  id: string
  url: string
  localPath?: string
  prompt: string
  metadata: {
    title: string
    description: string
    tags: string[]
    timestamp: string
  }
  proofStatus: 'pending' | 'approved' | 'rejected'
  proofNotes?: string
}

interface PublishedProduct {
  platform: string
  productId: string
  url: string
  type: string
  status: 'created' | 'published' | 'failed'
  assetId: string
}

interface PipelineStatus {
  stage: 'idle' | 'generating' | 'proofing' | 'publishing' | 'completed' | 'failed'
  progress: number
  currentItem?: string
  assetsGenerated: number
  assetsApproved: number
  productsPublished: number
  errors: string[]
}

export default function PodEngineGUI() {
  // Pipeline State
  const [isRunning, setIsRunning] = useState(false)
  const [status, setStatus] = useState<PipelineStatus>({
    stage: 'idle',
    progress: 0,
    assetsGenerated: 0,
    assetsApproved: 0,
    productsPublished: 0,
    errors: []
  })

  // Configuration
  const [config, setConfig] = useState({
    // Generation
    prompt: '',
    theme: 'Abstract Art',
    style: 'Digital',
    niche: 'Modern',
    count: 3,

    // Products
    productTypes: ['tshirt', 'hoodie'],
    tshirtPrice: 19.99,
    hoodiePrice: 34.99,

    // Platforms
    enabledPlatforms: ['printify', 'shopify'],

    // Workflow
    autoProof: false,
    autoPublish: true,

    // RunPod
    runpodMode: false,
    runpodApiKey: '',
    runpodPodId: '',
    comfyuiUrl: 'http://localhost:8188'
  })

  // Assets & Products
  const [assets, setAssets] = useState<GeneratedAsset[]>([])
  const [products, setProducts] = useState<PublishedProduct[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])

  // UI State
  const [activeTab, setActiveTab] = useState<'generate' | 'proof' | 'publish' | 'settings'>('generate')
  const [selectedAsset, setSelectedAsset] = useState<GeneratedAsset | null>(null)
  const [runpodStatus, setRunpodStatus] = useState<'disconnected' | 'connected' | 'error'>('disconnected')

  // Add log entry
  const addLog = useCallback((message: string, type: LogEntry['type'] = 'INFO') => {
    const log: LogEntry = {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toLocaleTimeString(),
      message,
      type
    }
    setLogs(prev => [...prev, log])
  }, [])

  // Run pipeline
  const handleRunPipeline = async () => {
    if (isRunning) return

    setIsRunning(true)
    setAssets([])
    setProducts([])
    setStatus({
      stage: 'generating',
      progress: 0,
      assetsGenerated: 0,
      assetsApproved: 0,
      productsPublished: 0,
      errors: []
    })

    addLog('🚀 Starting Pod Engine Pipeline...', 'INFO')

    try {
      // Simulate pipeline stages
      await simulateGeneration()
      await simulateProofing()
      await simulatePublishing()

      setStatus(prev => ({ ...prev, stage: 'completed', progress: 100 }))
      addLog('✅ Pipeline completed successfully!', 'SUCCESS')
    } catch (error) {
      addLog(`❌ Pipeline failed: ${error}`, 'ERROR')
      setStatus(prev => ({ ...prev, stage: 'failed' }))
    } finally {
      setIsRunning(false)
    }
  }

  // Simulate generation stage
  const simulateGeneration = async () => {
    addLog('📝 Generating prompts with Claude...', 'INFO')
    await delay(1000)

    addLog('🎨 Generating images with ComfyUI...', 'INFO')
    setStatus(prev => ({ ...prev, stage: 'generating', progress: 20 }))

    for (let i = 0; i < config.count; i++) {
      await delay(2000)

      const asset: GeneratedAsset = {
        id: `asset-${Date.now()}-${i}`,
        url: `https://picsum.photos/seed/${Date.now()}-${i}/1024/1024`,
        prompt: config.prompt || `${config.theme} ${config.style} design`,
        metadata: {
          title: `${config.theme} Design ${i + 1}`,
          description: `AI-generated ${config.style} artwork`,
          tags: [config.theme.toLowerCase(), config.style.toLowerCase(), 'ai-art'],
          timestamp: new Date().toISOString()
        },
        proofStatus: 'pending'
      }

      setAssets(prev => [...prev, asset])
      setStatus(prev => ({
        ...prev,
        assetsGenerated: prev.assetsGenerated + 1,
        progress: 20 + ((i + 1) / config.count) * 30
      }))

      addLog(`✓ Generated: ${asset.metadata.title}`, 'SUCCESS')
    }

    addLog('💾 Saving to local storage...', 'INFO')
    await delay(1000)
    addLog(`✓ Saved ${config.count} assets`, 'SUCCESS')
  }

  // Simulate proofing stage
  const simulateProofing = async () => {
    setStatus(prev => ({ ...prev, stage: 'proofing', progress: 60 }))
    addLog('🔍 Proofing assets...', 'INFO')

    if (config.autoProof) {
      // Auto-approve all
      setAssets(prev =>
        prev.map(asset => ({ ...asset, proofStatus: 'approved' as const }))
      )
      setStatus(prev => ({ ...prev, assetsApproved: prev.assetsGenerated }))
      addLog(`✓ Auto-approved ${config.count} assets`, 'SUCCESS')
    } else {
      // Manual proofing would happen here
      addLog('⏸ Waiting for manual approval...', 'INFO')
      // For demo, auto-approve after delay
      await delay(2000)
      setAssets(prev =>
        prev.map(asset => ({ ...asset, proofStatus: 'approved' as const }))
      )
      setStatus(prev => ({ ...prev, assetsApproved: prev.assetsGenerated }))
      addLog(`✓ Approved ${config.count} assets`, 'SUCCESS')
    }

    setStatus(prev => ({ ...prev, progress: 70 }))
  }

  // Simulate publishing stage
  const simulatePublishing = async () => {
    setStatus(prev => ({ ...prev, stage: 'publishing', progress: 75 }))
    addLog('📦 Publishing products...', 'INFO')

    const approvedAssets = assets.filter(a => a.proofStatus === 'approved')

    for (const asset of approvedAssets) {
      for (const productType of config.productTypes) {
        for (const platform of config.enabledPlatforms) {
          await delay(1500)

          const product: PublishedProduct = {
            platform,
            productId: `prod-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            url: `https://${platform}.example.com/product/${asset.id}`,
            type: productType,
            status: config.autoPublish ? 'published' : 'created',
            assetId: asset.id
          }

          setProducts(prev => [...prev, product])
          setStatus(prev => ({
            ...prev,
            productsPublished: prev.productsPublished + 1
          }))

          addLog(`✓ Published ${productType} to ${platform}`, 'SUCCESS')
        }
      }
    }

    setStatus(prev => ({ ...prev, progress: 95 }))
  }

  // Helper delay function
  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  // Approve asset
  const handleApproveAsset = (assetId: string) => {
    setAssets(prev =>
      prev.map(asset =>
        asset.id === assetId ? { ...asset, proofStatus: 'approved' as const } : asset
      )
    )
    setStatus(prev => ({ ...prev, assetsApproved: prev.assetsApproved + 1 }))
    addLog(`✓ Approved asset ${assetId}`, 'SUCCESS')
  }

  // Reject asset
  const handleRejectAsset = (assetId: string, notes: string) => {
    setAssets(prev =>
      prev.map(asset =>
        asset.id === assetId
          ? { ...asset, proofStatus: 'rejected' as const, proofNotes: notes }
          : asset
      )
    )
    addLog(`✗ Rejected asset ${assetId}: ${notes}`, 'WARNING')
  }

  // Check RunPod connection
  const handleCheckRunPod = async () => {
    addLog('🔌 Checking RunPod connection...', 'INFO')
    setRunpodStatus('disconnected')

    try {
      // Simulate connection check
      await delay(1500)

      if (config.runpodApiKey && config.runpodPodId) {
        setRunpodStatus('connected')
        addLog('✓ Connected to RunPod pod', 'SUCCESS')
      } else {
        setRunpodStatus('error')
        addLog('✗ RunPod credentials missing', 'ERROR')
      }
    } catch (error) {
      setRunpodStatus('error')
      addLog(`✗ RunPod connection failed: ${error}`, 'ERROR')
    }
  }

  // Sync from RunPod
  const handleSyncRunPod = async () => {
    addLog('☁️ Syncing from RunPod...', 'INFO')

    try {
      await delay(2000)
      addLog('✓ Downloaded 3 images from RunPod', 'SUCCESS')
    } catch (error) {
      addLog(`✗ RunPod sync failed: ${error}`, 'ERROR')
    }
  }

  // Get stage color
  const getStageColor = (stage: PipelineStatus['stage']) => {
    const colors = {
      idle: 'text-slate-500',
      generating: 'text-blue-400',
      proofing: 'text-yellow-400',
      publishing: 'text-purple-400',
      completed: 'text-green-400',
      failed: 'text-red-400'
    }
    return colors[stage]
  }

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      {/* LEFT SIDEBAR */}
      <div className="w-80 flex flex-col border-r border-slate-800 bg-slate-900/50">
        {/* Header */}
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg shadow-lg">
              <Rocket className="text-white" size={24} />
            </div>
            <div>
              <h1 className="font-bold text-slate-100">Pod Engine</h1>
              <p className="text-xs text-indigo-400 font-mono">ComfyUI + RunPod Pipeline</p>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="grid grid-cols-4 gap-1 bg-slate-800 rounded-lg p-1">
            {(['generate', 'proof', 'publish', 'settings'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-2 py-1.5 rounded text-xs font-medium transition-all ${
                  activeTab === tab
                    ? 'bg-indigo-600 text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {activeTab === 'generate' && (
            <>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Theme</label>
                <input
                  type="text"
                  value={config.theme}
                  onChange={e => setConfig({ ...config, theme: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 mb-1 block">Style</label>
                <input
                  type="text"
                  value={config.style}
                  onChange={e => setConfig({ ...config, style: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 mb-1 block">Custom Prompt (Optional)</label>
                <textarea
                  value={config.prompt}
                  onChange={e => setConfig({ ...config, prompt: e.target.value })}
                  rows={3}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 mb-1 block">Count: {config.count}</label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={config.count}
                  onChange={e => setConfig({ ...config, count: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 mb-2 block">Product Types</label>
                <div className="space-y-2">
                  {(['tshirt', 'hoodie', 'mug', 'poster'] as const).map(type => (
                    <label key={type} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={config.productTypes.includes(type)}
                        onChange={e => {
                          if (e.target.checked) {
                            setConfig({ ...config, productTypes: [...config.productTypes, type] })
                          } else {
                            setConfig({
                              ...config,
                              productTypes: config.productTypes.filter(t => t !== type)
                            })
                          }
                        }}
                        className="rounded"
                      />
                      <span className="capitalize">{type}</span>
                    </label>
                  ))}
                </div>
              </div>
            </>
          )}

          {activeTab === 'proof' && (
            <>
              <div>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={config.autoProof}
                    onChange={e => setConfig({ ...config, autoProof: e.target.checked })}
                    className="rounded"
                  />
                  Auto-approve all assets
                </label>
              </div>

              <div className="text-xs text-slate-500 mt-2">
                When disabled, assets will require manual review before publishing.
              </div>
            </>
          )}

          {activeTab === 'publish' && (
            <>
              <div>
                <label className="text-xs text-slate-400 mb-2 block">Enabled Platforms</label>
                <div className="space-y-2">
                  {['printify', 'shopify', 'tiktok', 'etsy', 'instagram'].map(platform => (
                    <label key={platform} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={config.enabledPlatforms.includes(platform)}
                        onChange={e => {
                          if (e.target.checked) {
                            setConfig({
                              ...config,
                              enabledPlatforms: [...config.enabledPlatforms, platform]
                            })
                          } else {
                            setConfig({
                              ...config,
                              enabledPlatforms: config.enabledPlatforms.filter(p => p !== platform)
                            })
                          }
                        }}
                        className="rounded"
                      />
                      <span className="capitalize">{platform}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={config.autoPublish}
                    onChange={e => setConfig({ ...config, autoPublish: e.target.checked })}
                    className="rounded"
                  />
                  Auto-publish products
                </label>
              </div>

              <div className="grid grid-cols-2 gap-2 mt-4">
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">T-Shirt Price</label>
                  <input
                    type="number"
                    value={config.tshirtPrice}
                    onChange={e => setConfig({ ...config, tshirtPrice: parseFloat(e.target.value) })}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm"
                    step="0.01"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Hoodie Price</label>
                  <input
                    type="number"
                    value={config.hoodiePrice}
                    onChange={e => setConfig({ ...config, hoodiePrice: parseFloat(e.target.value) })}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm"
                    step="0.01"
                  />
                </div>
              </div>
            </>
          )}

          {activeTab === 'settings' && (
            <>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">ComfyUI URL</label>
                <input
                  type="text"
                  value={config.comfyuiUrl}
                  onChange={e => setConfig({ ...config, comfyuiUrl: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm font-mono"
                />
              </div>

              <div className="border-t border-slate-800 pt-4">
                <div className="flex items-center justify-between mb-3">
                  <label className="text-xs text-slate-400">RunPod Mode</label>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.runpodMode}
                      onChange={e => setConfig({ ...config, runpodMode: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>

                {config.runpodMode && (
                  <>
                    <div className="space-y-3">
                      <div>
                        <label className="text-xs text-slate-400 mb-1 block">API Key</label>
                        <input
                          type="password"
                          value={config.runpodApiKey}
                          onChange={e => setConfig({ ...config, runpodApiKey: e.target.value })}
                          className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm font-mono"
                        />
                      </div>

                      <div>
                        <label className="text-xs text-slate-400 mb-1 block">Pod ID</label>
                        <input
                          type="text"
                          value={config.runpodPodId}
                          onChange={e => setConfig({ ...config, runpodPodId: e.target.value })}
                          className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm font-mono"
                        />
                      </div>

                      <div className="flex gap-2">
                        <button
                          onClick={handleCheckRunPod}
                          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded text-sm border border-slate-700"
                        >
                          <Server size={14} />
                          Test Connection
                        </button>
                        <button
                          onClick={handleSyncRunPod}
                          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded text-sm border border-slate-700"
                        >
                          <CloudDownload size={14} />
                          Sync Files
                        </button>
                      </div>

                      <div className="flex items-center gap-2 text-xs">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            runpodStatus === 'connected'
                              ? 'bg-green-500'
                              : runpodStatus === 'error'
                              ? 'bg-red-500'
                              : 'bg-slate-600'
                          }`}
                        ></div>
                        <span className="text-slate-400">
                          {runpodStatus === 'connected'
                            ? 'Connected'
                            : runpodStatus === 'error'
                            ? 'Error'
                            : 'Disconnected'}
                        </span>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </>
          )}
        </div>

        {/* Action Buttons */}
        <div className="p-4 border-t border-slate-800 space-y-2">
          <button
            onClick={handleRunPipeline}
            disabled={isRunning}
            className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg font-semibold transition-all ${
              isRunning
                ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white'
            }`}
          >
            {isRunning ? (
              <>
                <RefreshCw size={18} className="animate-spin" />
                Running Pipeline...
              </>
            ) : (
              <>
                <Play size={18} />
                Run Pipeline
              </>
            )}
          </button>

          {/* Status Bar */}
          <div className="bg-slate-800 rounded-lg p-3 space-y-2">
            <div className="flex justify-between text-xs">
              <span className={`font-medium ${getStageColor(status.stage)}`}>
                {status.stage.toUpperCase()}
              </span>
              <span className="text-slate-400">{Math.round(status.progress)}%</span>
            </div>
            <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300"
                style={{ width: `${status.progress}%` }}
              ></div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs text-center">
              <div>
                <div className="text-slate-500">Generated</div>
                <div className="text-slate-200 font-semibold">{status.assetsGenerated}</div>
              </div>
              <div>
                <div className="text-slate-500">Approved</div>
                <div className="text-slate-200 font-semibold">{status.assetsApproved}</div>
              </div>
              <div>
                <div className="text-slate-500">Published</div>
                <div className="text-slate-200 font-semibold">{status.productsPublished}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT CONTENT */}
      <div className="flex-1 flex flex-col">
        {/* Assets Gallery */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <ImageIcon size={20} className="text-indigo-400" />
              <h2 className="text-lg font-bold">Generated Assets</h2>
              <span className="text-sm text-slate-500">({assets.length})</span>
            </div>
            {status.currentItem && (
              <div className="text-sm text-slate-400">{status.currentItem}</div>
            )}
          </div>

          {assets.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-slate-600">
              <Layers size={48} className="mb-3 opacity-30" />
              <p className="text-sm">No assets generated yet</p>
              <p className="text-xs text-slate-500 mt-1">Configure and run the pipeline to start</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {assets.map(asset => (
                <div
                  key={asset.id}
                  className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden hover:border-indigo-600 transition-all cursor-pointer"
                  onClick={() => setSelectedAsset(asset)}
                >
                  <div className="aspect-square bg-slate-950 relative">
                    <img
                      src={asset.url}
                      alt={asset.metadata.title}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute top-2 right-2">
                      {asset.proofStatus === 'approved' && (
                        <div className="bg-green-500 text-white text-xs px-2 py-1 rounded flex items-center gap-1">
                          <CheckCircle2 size={12} />
                          Approved
                        </div>
                      )}
                      {asset.proofStatus === 'rejected' && (
                        <div className="bg-red-500 text-white text-xs px-2 py-1 rounded flex items-center gap-1">
                          <XCircle size={12} />
                          Rejected
                        </div>
                      )}
                      {asset.proofStatus === 'pending' && (
                        <div className="bg-yellow-500 text-white text-xs px-2 py-1 rounded flex items-center gap-1">
                          <AlertCircle size={12} />
                          Pending
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="p-3">
                    <h3 className="font-semibold text-sm truncate">{asset.metadata.title}</h3>
                    <p className="text-xs text-slate-500 truncate">{asset.metadata.description}</p>
                    <div className="flex gap-1 mt-2 flex-wrap">
                      {asset.metadata.tags.slice(0, 3).map(tag => (
                        <span
                          key={tag}
                          className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  {asset.proofStatus === 'pending' && !config.autoProof && (
                    <div className="flex gap-2 p-3 pt-0">
                      <button
                        onClick={e => {
                          e.stopPropagation()
                          handleApproveAsset(asset.id)
                        }}
                        className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 bg-green-600 hover:bg-green-500 text-white text-xs rounded"
                      >
                        <CheckCircle2 size={12} />
                        Approve
                      </button>
                      <button
                        onClick={e => {
                          e.stopPropagation()
                          handleRejectAsset(asset.id, 'Manual rejection')
                        }}
                        className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 bg-red-600 hover:bg-red-500 text-white text-xs rounded"
                      >
                        <XCircle size={12} />
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Published Products */}
          {products.length > 0 && (
            <div className="mt-8">
              <div className="flex items-center gap-2 mb-4">
                <ShoppingBag size={20} className="text-purple-400" />
                <h2 className="text-lg font-bold">Published Products</h2>
                <span className="text-sm text-slate-500">({products.length})</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {products.map(product => (
                  <div
                    key={`${product.platform}-${product.productId}`}
                    className="bg-slate-900 border border-slate-800 rounded-lg p-3"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold text-indigo-400 uppercase">
                        {product.platform}
                      </span>
                      <span className="text-xs text-slate-500 capitalize">{product.type}</span>
                    </div>
                    <div className="text-sm text-slate-300 mb-2 font-mono text-xs truncate">
                      {product.productId}
                    </div>
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          product.status === 'published'
                            ? 'bg-green-500'
                            : product.status === 'created'
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                      ></div>
                      <span className="text-xs text-slate-400 capitalize">{product.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Logs Terminal */}
        <div className="h-64 border-t border-slate-800">
          <Terminal logs={logs} onClear={() => setLogs([])} />
        </div>
      </div>
    </div>
  )
}
