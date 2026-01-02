import React, { useState, useCallback, useRef } from 'react';
import { Terminal } from './components/Terminal';
import { LogEntry, LogType } from './types';
import {
  Rocket,
  Layers,
  Box,
  Settings,
  Play,
  Image as ImageIcon,
  CheckCircle2,
  Loader2,
  AlertCircle,
  ShoppingBag,
  TrendingUp,
  Zap,
  Globe,
  DollarSign,
  Package
} from 'lucide-react';

interface Platform {
  id: string;
  name: string;
  icon: string;
  enabled: boolean;
  color: string;
}

interface PipelineConfig {
  // Prompt generation
  theme?: string;
  style?: string;
  niche?: string;
  customPrompt?: string;

  // Product settings
  productTypes: ('tshirt' | 'hoodie')[];
  designCount: number;
  autoPublish: boolean;

  // Pricing
  tshirtPrice: number;
  hoodiePrice: number;

  // Platforms
  platforms: Platform[];
}

interface PipelineStats {
  totalDesigns: number;
  totalProducts: number;
  successRate: number;
  platformBreakdown: Record<string, number>;
}

export default function PodPipelineApp() {
  // --- State ---
  const [config, setConfig] = useState<PipelineConfig>({
    theme: '',
    style: 'minimalist',
    niche: '',
    customPrompt: '',
    productTypes: ['tshirt', 'hoodie'],
    designCount: 5,
    autoPublish: true,
    tshirtPrice: 19.99,
    hoodiePrice: 34.99,
    platforms: [
      { id: 'printify', name: 'Printify', icon: '📦', enabled: true, color: 'bg-green-600' },
      { id: 'shopify', name: 'Shopify', icon: '🛍️', enabled: true, color: 'bg-emerald-600' },
      { id: 'tiktok', name: 'TikTok Shop', icon: '🎵', enabled: false, color: 'bg-pink-600' },
      { id: 'etsy', name: 'Etsy', icon: '🎨', enabled: false, color: 'bg-orange-600' },
      { id: 'instagram', name: 'Instagram', icon: '📸', enabled: false, color: 'bg-purple-600' },
      { id: 'facebook', name: 'Facebook', icon: '👥', enabled: false, color: 'bg-blue-600' },
    ]
  });

  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [currentTab, setCurrentTab] = useState<'config' | 'platforms' | 'analytics'>('config');

  // Preview images
  const [previewImages, setPreviewImages] = useState<string[]>([]);
  const [generatedProducts, setGeneratedProducts] = useState<any[]>([]);

  // Stats
  const [stats, setStats] = useState<PipelineStats>({
    totalDesigns: 0,
    totalProducts: 0,
    successRate: 0,
    platformBreakdown: {}
  });

  // --- Handlers ---
  const addLog = useCallback((message: string, type: LogType = LogType.INFO) => {
    setLogs(prev => [...prev, {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
      message,
      type
    }]);
  }, []);

  const togglePlatform = (platformId: string) => {
    setConfig(prev => ({
      ...prev,
      platforms: prev.platforms.map(p =>
        p.id === platformId ? { ...p, enabled: !p.enabled } : p
      )
    }));
  };

  const toggleProductType = (type: 'tshirt' | 'hoodie') => {
    setConfig(prev => {
      const types = prev.productTypes.includes(type)
        ? prev.productTypes.filter(t => t !== type)
        : [...prev.productTypes, type];
      return { ...prev, productTypes: types };
    });
  };

  const handleRunPipeline = async () => {
    if (isRunning) return;

    const enabledPlatforms = config.platforms.filter(p => p.enabled);
    if (enabledPlatforms.length === 0) {
      addLog("⚠️  Please enable at least one platform!", LogType.WARNING);
      return;
    }

    if (config.productTypes.length === 0) {
      addLog("⚠️  Please select at least one product type!", LogType.WARNING);
      return;
    }

    setIsRunning(true);
    setProgress(0);
    setLogs([]);
    setPreviewImages([]);
    setGeneratedProducts([]);

    try {
      // Simulate pipeline execution (replace with real orchestrator call)
      addLog("🚀 Starting POD automation pipeline...", LogType.INFO);
      setProgress(10);

      addLog(`📝 Generating ${config.designCount} creative prompts with Claude...`, LogType.INFO);
      await sleep(1500);
      setProgress(25);
      addLog(`✓ Generated ${config.designCount} creative prompts`, LogType.SUCCESS);

      addLog("🎨 Generating AI images with ComfyUI...", LogType.INFO);
      await sleep(2000);
      setProgress(50);

      // Add preview images
      const mockImages = Array(Math.min(config.designCount, 3)).fill(0).map((_, i) =>
        `https://placehold.co/400x400/1e293b/94a3b8?text=Design+${i+1}`
      );
      setPreviewImages(mockImages);
      addLog(`✓ Generated ${config.designCount} images`, LogType.SUCCESS);

      addLog("💾 Saving images to storage...", LogType.INFO);
      await sleep(1000);
      setProgress(65);
      addLog(`✓ Saved ${config.designCount} images`, LogType.SUCCESS);

      // Create products on each platform
      let productCount = 0;
      const platformBreakdown: Record<string, number> = {};

      for (const platform of enabledPlatforms) {
        addLog(`📦 Publishing to ${platform.name}...`, LogType.INFO);
        await sleep(1500);

        const productsPerPlatform = config.designCount * config.productTypes.length;
        productCount += productsPerPlatform;
        platformBreakdown[platform.id] = productsPerPlatform;

        addLog(`✓ Published ${productsPerPlatform} products to ${platform.name}`, LogType.SUCCESS);
        setProgress(prev => Math.min(prev + (20 / enabledPlatforms.length), 95));
      }

      setProgress(100);
      setGeneratedProducts([
        ...Array(productCount).fill(0).map((_, i) => ({
          id: `prod-${i}`,
          name: `Design ${Math.floor(i / config.productTypes.length) + 1}`,
          type: config.productTypes[i % config.productTypes.length],
          platform: enabledPlatforms[i % enabledPlatforms.length].name,
          status: 'published'
        }))
      ]);

      setStats({
        totalDesigns: config.designCount,
        totalProducts: productCount,
        successRate: 100,
        platformBreakdown
      });

      addLog(`✅ Pipeline complete! Created ${productCount} products across ${enabledPlatforms.length} platforms`, LogType.SUCCESS);

    } catch (error) {
      addLog(`❌ Pipeline failed: ${error}`, LogType.ERROR);
    } finally {
      setIsRunning(false);
    }
  };

  // Helper
  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">

      {/* --- LEFT SIDEBAR: Configuration --- */}
      <div className="w-96 flex flex-col border-r border-slate-800 bg-slate-900/50">

        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg shadow-lg shadow-indigo-500/20">
            <ShoppingBag className="text-white" size={24} />
          </div>
          <div>
            <h1 className="font-bold text-slate-100 leading-tight">POD Pipeline</h1>
            <p className="text-xs text-indigo-400 font-mono">Multi-Platform Studio</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-800">
          <button
            onClick={() => setCurrentTab('config')}
            className={`flex-1 px-4 py-2.5 text-sm font-medium transition-colors ${
              currentTab === 'config'
                ? 'bg-slate-800 text-indigo-400 border-b-2 border-indigo-500'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-800/50'
            }`}
          >
            <Settings size={16} className="inline mr-1.5" />
            Config
          </button>
          <button
            onClick={() => setCurrentTab('platforms')}
            className={`flex-1 px-4 py-2.5 text-sm font-medium transition-colors ${
              currentTab === 'platforms'
                ? 'bg-slate-800 text-indigo-400 border-b-2 border-indigo-500'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-800/50'
            }`}
          >
            <Globe size={16} className="inline mr-1.5" />
            Platforms
          </button>
          <button
            onClick={() => setCurrentTab('analytics')}
            className={`flex-1 px-4 py-2.5 text-sm font-medium transition-colors ${
              currentTab === 'analytics'
                ? 'bg-slate-800 text-indigo-400 border-b-2 border-indigo-500'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-800/50'
            }`}
          >
            <TrendingUp size={16} className="inline mr-1.5" />
            Stats
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">

          {/* CONFIG TAB */}
          {currentTab === 'config' && (
            <>
              {/* Prompt Configuration */}
              <div className="space-y-4">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Prompt Generation</label>

                <div className="space-y-3">
                  <div>
                    <span className="text-xs text-slate-400 mb-1 block">Theme/Niche</span>
                    <input
                      type="text"
                      placeholder="e.g., Abstract Art, Nature, Gaming"
                      value={config.niche}
                      onChange={e => setConfig({...config, niche: e.target.value})}
                      className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                  </div>

                  <div>
                    <span className="text-xs text-slate-400 mb-1 block">Art Style</span>
                    <select
                      value={config.style}
                      onChange={e => setConfig({...config, style: e.target.value})}
                      className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                    >
                      <option value="minimalist">Minimalist</option>
                      <option value="abstract">Abstract</option>
                      <option value="geometric">Geometric</option>
                      <option value="watercolor">Watercolor</option>
                      <option value="vintage">Vintage</option>
                      <option value="modern">Modern</option>
                    </select>
                  </div>

                  <div>
                    <span className="text-xs text-slate-400 mb-1 block">Custom Prompt (Optional)</span>
                    <textarea
                      placeholder="Override with custom prompt..."
                      value={config.customPrompt}
                      onChange={e => setConfig({...config, customPrompt: e.target.value})}
                      className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 h-20 resize-none"
                    />
                  </div>
                </div>
              </div>

              {/* Product Configuration */}
              <div className="space-y-4">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Product Settings</label>

                <div>
                  <span className="text-xs text-slate-400 mb-2 block">Product Types</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => toggleProductType('tshirt')}
                      className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all border ${
                        config.productTypes.includes('tshirt')
                          ? 'bg-indigo-600 border-indigo-500 text-white'
                          : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600'
                      }`}
                    >
                      👕 T-Shirt
                    </button>
                    <button
                      onClick={() => toggleProductType('hoodie')}
                      className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all border ${
                        config.productTypes.includes('hoodie')
                          ? 'bg-indigo-600 border-indigo-500 text-white'
                          : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600'
                      }`}
                    >
                      🧥 Hoodie
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <span className="text-xs text-slate-400 mb-1 block">Design Count</span>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      value={config.designCount}
                      onChange={e => setConfig({...config, designCount: parseInt(e.target.value) || 1})}
                      className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div className="flex items-end">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={config.autoPublish}
                        onChange={e => setConfig({...config, autoPublish: e.target.checked})}
                        className="w-4 h-4 bg-slate-800 border-slate-700 rounded"
                      />
                      <span className="text-xs text-slate-300">Auto-Publish</span>
                    </label>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <span className="text-xs text-slate-400 mb-1 flex items-center gap-1">
                      <DollarSign size={12} /> T-Shirt Price
                    </span>
                    <input
                      type="number"
                      step="0.01"
                      value={config.tshirtPrice}
                      onChange={e => setConfig({...config, tshirtPrice: parseFloat(e.target.value) || 0})}
                      className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <span className="text-xs text-slate-400 mb-1 flex items-center gap-1">
                      <DollarSign size={12} /> Hoodie Price
                    </span>
                    <input
                      type="number"
                      step="0.01"
                      value={config.hoodiePrice}
                      onChange={e => setConfig({...config, hoodiePrice: parseFloat(e.target.value) || 0})}
                      className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
              </div>
            </>
          )}

          {/* PLATFORMS TAB */}
          {currentTab === 'platforms' && (
            <div className="space-y-3">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Distribution Platforms
              </label>

              {config.platforms.map(platform => (
                <div
                  key={platform.id}
                  onClick={() => togglePlatform(platform.id)}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    platform.enabled
                      ? `${platform.color} bg-opacity-20 border-opacity-50`
                      : 'bg-slate-800/50 border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{platform.icon}</span>
                      <div>
                        <div className="font-medium text-sm">{platform.name}</div>
                        <div className="text-xs text-slate-400">
                          {platform.enabled ? 'Active' : 'Disabled'}
                        </div>
                      </div>
                    </div>
                    {platform.enabled && <CheckCircle2 size={20} className="text-emerald-400" />}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* ANALYTICS TAB */}
          {currentTab === 'analytics' && (
            <div className="space-y-4">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Pipeline Statistics
              </label>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-xs text-slate-400 mb-1">Total Designs</div>
                  <div className="text-2xl font-bold text-indigo-400">{stats.totalDesigns}</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-xs text-slate-400 mb-1">Total Products</div>
                  <div className="text-2xl font-bold text-emerald-400">{stats.totalProducts}</div>
                </div>
              </div>

              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-xs text-slate-400 mb-1">Success Rate</div>
                <div className="text-2xl font-bold text-purple-400">{stats.successRate}%</div>
                <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-purple-500 transition-all"
                    style={{ width: `${stats.successRate}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-xs text-slate-400 mb-3">Platform Breakdown</div>
                <div className="space-y-2">
                  {Object.entries(stats.platformBreakdown).map(([platform, count]) => {
                    const platformData = config.platforms.find(p => p.id === platform);
                    return (
                      <div key={platform} className="flex items-center justify-between text-sm">
                        <span className="text-slate-300">{platformData?.icon} {platformData?.name}</span>
                        <span className="font-mono text-slate-400">{count}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Action Button */}
        <div className="p-4 bg-slate-900 border-t border-slate-800">
          <button
            onClick={handleRunPipeline}
            disabled={isRunning}
            className={`w-full flex items-center justify-center gap-2 py-3.5 rounded-lg font-semibold shadow-lg transition-all ${
              isRunning
                ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-indigo-900/20'
            }`}
          >
            {isRunning ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                Running Pipeline...
              </>
            ) : (
              <>
                <Zap size={20} />
                Start POD Pipeline
              </>
            )}
          </button>

          {/* Progress Bar */}
          {isRunning && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Progress</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300 ease-out"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* --- RIGHT CONTENT: Preview & Logs --- */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Top Area: Design Previews */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="flex items-center gap-2 mb-4">
            <ImageIcon size={20} className="text-indigo-400"/>
            <h2 className="text-lg font-bold">Generated Designs</h2>
          </div>

          {previewImages.length === 0 ? (
            <div className="flex items-center justify-center h-64 bg-slate-900 border-2 border-dashed border-slate-800 rounded-xl">
              <div className="text-center text-slate-600">
                <Layers size={48} className="mx-auto mb-3 opacity-20"/>
                <p className="text-sm">Design previews will appear here</p>
                <p className="text-xs mt-1">Configure settings and run the pipeline</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-4">
              {previewImages.map((img, idx) => (
                <div key={idx} className="bg-slate-900 border-2 border-slate-800 rounded-xl overflow-hidden hover:border-indigo-600 transition-colors">
                  <div className="aspect-square relative">
                    <img
                      src={img}
                      alt={`Design ${idx + 1}`}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute top-2 left-2 bg-black/70 backdrop-blur px-2 py-1 rounded text-xs font-mono">
                      Design {idx + 1}
                    </div>
                  </div>
                  <div className="p-3 border-t border-slate-800">
                    <div className="text-xs text-slate-400 mb-1">Products Created</div>
                    <div className="flex gap-1">
                      {config.productTypes.map(type => (
                        <div key={type} className="flex-1 text-center py-1 bg-slate-800 rounded text-xs">
                          {type === 'tshirt' ? '👕' : '🧥'} {config.platforms.filter(p => p.enabled).length}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Product Grid */}
          {generatedProducts.length > 0 && (
            <div className="mt-6">
              <div className="flex items-center gap-2 mb-4">
                <Package size={20} className="text-emerald-400"/>
                <h2 className="text-lg font-bold">Published Products</h2>
                <span className="text-sm text-slate-400">({generatedProducts.length} total)</span>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <div className="max-h-64 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-800 sticky top-0">
                      <tr>
                        <th className="text-left px-4 py-2 text-xs font-semibold text-slate-400">Product</th>
                        <th className="text-left px-4 py-2 text-xs font-semibold text-slate-400">Type</th>
                        <th className="text-left px-4 py-2 text-xs font-semibold text-slate-400">Platform</th>
                        <th className="text-left px-4 py-2 text-xs font-semibold text-slate-400">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {generatedProducts.slice(0, 20).map((product, idx) => (
                        <tr key={product.id} className="hover:bg-slate-800/50">
                          <td className="px-4 py-2 text-slate-300">{product.name}</td>
                          <td className="px-4 py-2 text-slate-400">
                            {product.type === 'tshirt' ? '👕 T-Shirt' : '🧥 Hoodie'}
                          </td>
                          <td className="px-4 py-2 text-slate-400">{product.platform}</td>
                          <td className="px-4 py-2">
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-900/30 text-emerald-400 rounded text-xs">
                              <CheckCircle2 size={12} /> Published
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Bottom Area: Logs */}
        <div className="h-64 p-4 border-t border-slate-800 bg-slate-900/30">
          <Terminal logs={logs} onClear={() => setLogs([])} />
        </div>
      </div>
    </div>
  );
}
