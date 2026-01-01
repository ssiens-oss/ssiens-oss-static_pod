import React, { useState, useEffect } from 'react';
import {
  Layers, Settings, Image, Package, BarChart3, Workflow,
  Play, Pause, RefreshCw, Download, Trash2, ExternalLink,
  CheckCircle2, XCircle, Loader2, AlertCircle, TrendingUp,
  ShoppingBag, Zap, Globe, DollarSign, Clock
} from 'lucide-react';

// Import existing components
import { Terminal } from './components/Terminal';
import { LogEntry, LogType } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

type Tab = 'pipeline' | 'gallery' | 'products' | 'platforms' | 'analytics' | 'settings';

interface Stats {
  totalDesigns: number;
  totalProducts: number;
  totalRevenue: number;
  activePipelines: number;
  successRate: number;
  avgGenerationTime: number;
}

interface Design {
  id: string;
  url: string;
  prompt: string;
  title: string;
  createdAt: string;
  tags: string[];
}

interface Product {
  id: string;
  title: string;
  platform: string;
  status: string;
  price: number;
  image: string;
  url: string;
}

interface PlatformConfig {
  name: string;
  enabled: boolean;
  status: 'connected' | 'disconnected' | 'error';
  icon: React.ReactNode;
}

export default function DashboardApp() {
  const [activeTab, setActiveTab] = useState<Tab>('pipeline');
  const [stats, setStats] = useState<Stats>({
    totalDesigns: 0,
    totalProducts: 0,
    totalRevenue: 0,
    activePipelines: 0,
    successRate: 0,
    avgGenerationTime: 0
  });
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [designs, setDesigns] = useState<Design[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [platforms, setPlatforms] = useState<PlatformConfig[]>([
    { name: 'Printify', enabled: true, status: 'connected', icon: <Package size={16} /> },
    { name: 'Shopify', enabled: false, status: 'disconnected', icon: <ShoppingBag size={16} /> },
    { name: 'TikTok Shop', enabled: false, status: 'disconnected', icon: <Zap size={16} /> },
    { name: 'Etsy', enabled: false, status: 'disconnected', icon: <Globe size={16} /> },
  ]);

  // Pipeline state
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [pipelineConfig, setPipelineConfig] = useState({
    dropName: 'NewDrop',
    designCount: 10,
    theme: 'Urban streetwear',
    style: 'Bold graphics',
    productTypes: ['tshirt', 'hoodie'],
    useClaudePrompts: true,
    customPrompt: ''
  });

  // Check API status
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/health`);
        setApiStatus(response.ok ? 'online' : 'offline');
      } catch {
        setApiStatus('offline');
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // Load stats
  useEffect(() => {
    const loadStats = async () => {
      try {
        const response = await fetch(`${API_URL}/api/stats`);
        if (response.ok) {
          const data = await response.json();
          setStats({
            totalDesigns: data.storage?.totalImages || 0,
            totalProducts: data.storage?.totalImages * 2 || 0, // Assuming T-shirt + Hoodie
            totalRevenue: 0,
            activePipelines: 0,
            successRate: 95,
            avgGenerationTime: 45
          });
        }
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
    };
    loadStats();
  }, []);

  const handleStartPipeline = async () => {
    setIsRunning(true);
    setProgress(0);

    try {
      // Prepare payload based on prompt mode
      const payload = pipelineConfig.useClaudePrompts
        ? {
            dropName: pipelineConfig.dropName,
            designCount: pipelineConfig.designCount,
            theme: pipelineConfig.theme,
            style: pipelineConfig.style,
            niche: 'Urban fashion',
            productTypes: pipelineConfig.productTypes
          }
        : {
            dropName: pipelineConfig.dropName,
            designCount: pipelineConfig.designCount,
            customPrompt: pipelineConfig.customPrompt,
            productTypes: pipelineConfig.productTypes
          };

      const response = await fetch(`${API_URL}/api/pipeline/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const data = await response.json();
        addLog(`Pipeline started: ${data.pipelineId}`, LogType.SUCCESS);
        // Start polling for progress
        pollPipeline(data.pipelineId);
      }
    } catch (error) {
      addLog(`Failed to start pipeline: ${error}`, LogType.ERROR);
      setIsRunning(false);
    }
  };

  const pollPipeline = async (pipelineId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/pipeline/${pipelineId}/logs`);
        const data = await response.json();

        setLogs(data.logs || []);
        setProgress(data.progress || 0);

        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(interval);
          setIsRunning(false);
          setProgress(100);
        }
      } catch (error) {
        clearInterval(interval);
        setIsRunning(false);
      }
    }, 2000);
  };

  const addLog = (message: string, type: LogType = LogType.INFO) => {
    setLogs(prev => [...prev, {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
      message,
      type
    }]);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'pipeline':
        return <PipelineTab
          config={pipelineConfig}
          setConfig={setPipelineConfig}
          isRunning={isRunning}
          progress={progress}
          logs={logs}
          onStart={handleStartPipeline}
          onClearLogs={() => setLogs([])}
        />;

      case 'gallery':
        return <GalleryTab designs={designs} />;

      case 'products':
        return <ProductsTab products={products} />;

      case 'platforms':
        return <PlatformsTab platforms={platforms} setPlatforms={setPlatforms} />;

      case 'analytics':
        return <AnalyticsTab stats={stats} />;

      case 'settings':
        return <SettingsTab />;

      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">

      {/* Sidebar */}
      <div className="w-64 bg-slate-900/50 border-r border-slate-800 flex flex-col">
        {/* Logo */}
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-lg">
              <Layers className="text-white" size={24} />
            </div>
            <div>
              <h1 className="font-bold text-slate-100">StaticWaves</h1>
              <p className="text-xs text-indigo-400 font-mono">POD DASHBOARD</p>
            </div>
          </div>
        </div>

        {/* Status Banner */}
        <div className="p-3 border-b border-slate-800">
          <div className={`flex items-center gap-2 text-sm ${
            apiStatus === 'online' ? 'text-emerald-400' :
            apiStatus === 'offline' ? 'text-red-400' : 'text-slate-400'
          }`}>
            {apiStatus === 'online' ? <CheckCircle2 size={16} /> :
             apiStatus === 'offline' ? <XCircle size={16} /> :
             <Loader2 size={16} className="animate-spin" />}
            <span className="font-medium">
              {apiStatus === 'online' ? 'System Online' :
               apiStatus === 'offline' ? 'System Offline' : 'Checking...'}
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          <NavItem
            icon={<Play size={18} />}
            label="Pipeline"
            active={activeTab === 'pipeline'}
            onClick={() => setActiveTab('pipeline')}
          />
          <NavItem
            icon={<Image size={18} />}
            label="Design Gallery"
            active={activeTab === 'gallery'}
            onClick={() => setActiveTab('gallery')}
          />
          <NavItem
            icon={<Package size={18} />}
            label="Products"
            active={activeTab === 'products'}
            onClick={() => setActiveTab('products')}
            badge={products.length}
          />
          <NavItem
            icon={<Workflow size={18} />}
            label="Platforms"
            active={activeTab === 'platforms'}
            onClick={() => setActiveTab('platforms')}
          />
          <NavItem
            icon={<BarChart3 size={18} />}
            label="Analytics"
            active={activeTab === 'analytics'}
            onClick={() => setActiveTab('analytics')}
          />
          <NavItem
            icon={<Settings size={18} />}
            label="Settings"
            active={activeTab === 'settings'}
            onClick={() => setActiveTab('settings')}
          />
        </nav>

        {/* Stats Footer */}
        <div className="p-4 border-t border-slate-800 space-y-2">
          <StatRow label="Designs" value={stats.totalDesigns} />
          <StatRow label="Products" value={stats.totalProducts} />
          <StatRow label="Success Rate" value={`${stats.successRate}%`} />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {renderTabContent()}
      </div>
    </div>
  );
}

// Navigation Item Component
function NavItem({ icon, label, active, onClick, badge }: {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
  badge?: number;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${
        active
          ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/30'
          : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
      }`}
    >
      {icon}
      <span className="font-medium text-sm flex-1 text-left">{label}</span>
      {badge !== undefined && badge > 0 && (
        <span className="bg-indigo-500 text-white text-xs px-2 py-0.5 rounded-full">
          {badge}
        </span>
      )}
    </button>
  );
}

// Stat Row Component
function StatRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-slate-500">{label}</span>
      <span className="text-slate-200 font-semibold">{value}</span>
    </div>
  );
}

// Pipeline Tab Component
function PipelineTab({ config, setConfig, isRunning, progress, logs, onStart, onClearLogs }: any) {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-slate-800">
        <h2 className="text-2xl font-bold mb-2">Pipeline Control</h2>
        <p className="text-slate-400 text-sm">Configure and run your POD automation pipeline</p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Configuration */}
        <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold">Configuration ⚡ NEW</h3>

            {/* Prompt Mode Toggle */}
            <div className="flex items-center gap-3">
              <span className="text-sm text-slate-400">Prompt Mode:</span>
              <button
                onClick={() => setConfig({ ...config, useClaudePrompts: !config.useClaudePrompts })}
                disabled={isRunning}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                  config.useClaudePrompts
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                } ${isRunning ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {config.useClaudePrompts ? '✨ Claude AI' : '✏️ Manual'}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-slate-400 mb-2 block">Drop Name</label>
              <input
                type="text"
                value={config.dropName}
                onChange={e => setConfig({ ...config, dropName: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
                disabled={isRunning}
              />
            </div>

            <div>
              <label className="text-sm text-slate-400 mb-2 block">Design Count</label>
              <input
                type="number"
                value={config.designCount}
                onChange={e => setConfig({ ...config, designCount: parseInt(e.target.value) })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
                disabled={isRunning}
              />
            </div>

            {/* Conditional rendering based on prompt mode */}
            {config.useClaudePrompts ? (
              <>
                <div>
                  <label className="text-sm text-slate-400 mb-2 block">Theme</label>
                  <input
                    type="text"
                    value={config.theme}
                    onChange={e => setConfig({ ...config, theme: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
                    disabled={isRunning}
                  />
                </div>

                <div>
                  <label className="text-sm text-slate-400 mb-2 block">Style</label>
                  <input
                    type="text"
                    value={config.style}
                    onChange={e => setConfig({ ...config, style: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
                    disabled={isRunning}
                  />
                </div>
              </>
            ) : (
              <div className="col-span-2">
                <label className="text-sm text-slate-400 mb-2 block">Custom Prompt</label>
                <textarea
                  value={config.customPrompt}
                  onChange={e => setConfig({ ...config, customPrompt: e.target.value })}
                  placeholder="Enter your custom design prompt here... (e.g., 'A minimalist mountain landscape with geometric patterns in black and white')"
                  rows={4}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500 resize-none"
                  disabled={isRunning}
                />
                <p className="text-xs text-slate-500 mt-1">
                  💡 Tip: Be specific about style, colors, and composition for best results
                </p>
              </div>
            )}
          </div>

          {/* Product Types */}
          <div className="mt-4">
            <label className="text-sm text-slate-400 mb-2 block">Product Types</label>
            <div className="flex gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.productTypes.includes('tshirt')}
                  onChange={e => {
                    const types = e.target.checked
                      ? [...config.productTypes, 'tshirt']
                      : config.productTypes.filter((t: string) => t !== 'tshirt');
                    setConfig({ ...config, productTypes: types });
                  }}
                  className="w-4 h-4"
                  disabled={isRunning}
                />
                <span>T-Shirts</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.productTypes.includes('hoodie')}
                  onChange={e => {
                    const types = e.target.checked
                      ? [...config.productTypes, 'hoodie']
                      : config.productTypes.filter((t: string) => t !== 'hoodie');
                    setConfig({ ...config, productTypes: types });
                  }}
                  className="w-4 h-4"
                  disabled={isRunning}
                />
                <span>Hoodies</span>
              </label>
            </div>
          </div>

          {/* Start Button */}
          <button
            onClick={onStart}
            disabled={isRunning}
            className={`mt-6 w-full flex items-center justify-center gap-2 py-3 rounded-lg font-semibold transition-all ${
              isRunning
                ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-900/30'
            }`}
          >
            {isRunning ? <Loader2 className="animate-spin" size={20} /> : <Play size={20} />}
            {isRunning ? 'Pipeline Running...' : 'Start Pipeline'}
          </button>

          {/* Progress Bar */}
          {isRunning && (
            <div className="mt-4">
              <div className="flex justify-between text-sm text-slate-400 mb-2">
                <span>Progress</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-500 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Logs */}
        <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-6">
          <Terminal logs={logs} onClear={onClearLogs} />
        </div>
      </div>
    </div>
  );
}

// Gallery Tab Component
function GalleryTab({ designs }: { designs: Design[] }) {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="p-6 border-b border-slate-800">
        <h2 className="text-2xl font-bold mb-2">Design Gallery</h2>
        <p className="text-slate-400 text-sm">Browse all AI-generated designs</p>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {designs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-600">
            <Image size={64} className="mb-4 opacity-20" />
            <p className="text-lg">No designs yet</p>
            <p className="text-sm">Run your first pipeline to generate designs</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {designs.map(design => (
              <div key={design.id} className="bg-slate-900 rounded-lg border border-slate-800 overflow-hidden hover:border-indigo-500 transition-colors">
                <img src={design.url} alt={design.title} className="w-full aspect-square object-cover" />
                <div className="p-3">
                  <h4 className="font-medium text-sm mb-1 truncate">{design.title}</h4>
                  <p className="text-xs text-slate-500 truncate">{design.prompt}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Products Tab Component
function ProductsTab({ products }: { products: Product[] }) {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="p-6 border-b border-slate-800">
        <h2 className="text-2xl font-bold mb-2">Products</h2>
        <p className="text-slate-400 text-sm">Manage your POD products across all platforms</p>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {products.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-600">
            <Package size={64} className="mb-4 opacity-20" />
            <p className="text-lg">No products yet</p>
            <p className="text-sm">Products will appear here after pipeline runs</p>
          </div>
        ) : (
          <div className="space-y-3">
            {products.map(product => (
              <div key={product.id} className="bg-slate-900 rounded-lg border border-slate-800 p-4 flex items-center gap-4">
                <img src={product.image} alt={product.title} className="w-16 h-16 rounded object-cover" />
                <div className="flex-1">
                  <h4 className="font-medium">{product.title}</h4>
                  <p className="text-sm text-slate-400">{product.platform}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-emerald-400">${product.price}</p>
                  <p className="text-xs text-slate-500">{product.status}</p>
                </div>
                <button className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
                  <ExternalLink size={18} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Platforms Tab Component
function PlatformsTab({ platforms, setPlatforms }: any) {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="p-6 border-b border-slate-800">
        <h2 className="text-2xl font-bold mb-2">Platform Integrations</h2>
        <p className="text-slate-400 text-sm">Connect and manage your sales channels</p>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {platforms.map((platform: PlatformConfig, index: number) => (
            <div key={platform.name} className="bg-slate-900 rounded-xl border border-slate-800 p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-slate-800 rounded-lg">
                    {platform.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold">{platform.name}</h3>
                    <p className={`text-sm ${
                      platform.status === 'connected' ? 'text-emerald-400' :
                      platform.status === 'error' ? 'text-red-400' : 'text-slate-500'
                    }`}>
                      {platform.status === 'connected' ? 'Connected' :
                       platform.status === 'error' ? 'Error' : 'Not Connected'}
                    </p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={platform.enabled}
                    onChange={e => {
                      const newPlatforms = [...platforms];
                      newPlatforms[index].enabled = e.target.checked;
                      setPlatforms(newPlatforms);
                    }}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>

              <button className="w-full py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors">
                Configure
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Analytics Tab Component
function AnalyticsTab({ stats }: { stats: Stats }) {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="p-6 border-b border-slate-800">
        <h2 className="text-2xl font-bold mb-2">Analytics</h2>
        <p className="text-slate-400 text-sm">Track your POD business performance</p>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatCard
            icon={<Image size={24} />}
            label="Total Designs"
            value={stats.totalDesigns}
            color="indigo"
          />
          <StatCard
            icon={<Package size={24} />}
            label="Total Products"
            value={stats.totalProducts}
            color="emerald"
          />
          <StatCard
            icon={<DollarSign size={24} />}
            label="Revenue"
            value={`$${stats.totalRevenue}`}
            color="amber"
          />
          <StatCard
            icon={<TrendingUp size={24} />}
            label="Success Rate"
            value={`${stats.successRate}%`}
            color="cyan"
          />
        </div>

        <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
          <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
          <div className="space-y-4">
            <MetricRow label="Avg. Generation Time" value={`${stats.avgGenerationTime}s`} />
            <MetricRow label="Active Pipelines" value={stats.activePipelines} />
            <MetricRow label="Cost per Design" value="$0.06" />
            <MetricRow label="Total API Calls" value="0" />
          </div>
        </div>
      </div>
    </div>
  );
}

// Settings Tab Component
function SettingsTab() {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="p-6 border-b border-slate-800">
        <h2 className="text-2xl font-bold mb-2">Settings</h2>
        <p className="text-slate-400 text-sm">Configure your POD Studio</p>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
          <h3 className="text-lg font-semibold mb-4">API Configuration</h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-slate-400 mb-2 block">Claude API Key</label>
              <input
                type="password"
                placeholder="sk-ant-••••••••"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="text-sm text-slate-400 mb-2 block">Printify API Key</label>
              <input
                type="password"
                placeholder="••••••••"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="text-sm text-slate-400 mb-2 block">Printify Shop ID</label>
              <input
                type="text"
                placeholder="12345"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <button className="mt-6 w-full py-3 bg-indigo-600 hover:bg-indigo-500 rounded-lg font-semibold transition-colors">
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({ icon, label, value, color }: any) {
  const colorClasses = {
    indigo: 'bg-indigo-600/10 text-indigo-400 border-indigo-500/30',
    emerald: 'bg-emerald-600/10 text-emerald-400 border-emerald-500/30',
    amber: 'bg-amber-600/10 text-amber-400 border-amber-500/30',
    cyan: 'bg-cyan-600/10 text-cyan-400 border-cyan-500/30'
  };

  return (
    <div className={`rounded-xl border p-6 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-4">
        {icon}
        <TrendingUp size={16} className="opacity-50" />
      </div>
      <p className="text-2xl font-bold mb-1">{value}</p>
      <p className="text-sm opacity-70">{label}</p>
    </div>
  );
}

// Metric Row Component
function MetricRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-slate-400">{label}</span>
      <span className="font-semibold text-slate-200">{value}</span>
    </div>
  );
}
