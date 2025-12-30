import { useState, useEffect } from 'react';
import { Sparkles, Image as ImageIcon, Video, Music, BookOpen, ShoppingBag, Zap, Menu, X } from 'lucide-react';
import { useStore } from '../lib/store';
import { makerAPI, rewardsAPI, printify, type GenerateRequest } from '../lib/api';
import { AdMob } from '@capacitor-community/admob';
import { Haptics, ImpactStyle } from '@capacitor/haptics';

export default function Home() {
  const { tokenBalance, setTokenBalance, user, printifyShopId } = useStore();
  const [activeTab, setActiveTab] = useState<'image' | 'video' | 'music' | 'book' | 'print'>('image');
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  // Load balance on mount
  useEffect(() => {
    loadBalance();
  }, []);

  const loadBalance = async () => {
    try {
      const res = await rewardsAPI.getBalance();
      setTokenBalance(res.data);
    } catch (err) {
      console.error('Failed to load balance:', err);
    }
  };

  const generate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      await Haptics.impact({ style: ImpactStyle.Light });

      const req: GenerateRequest = { prompt };
      let response;

      switch (activeTab) {
        case 'image':
          response = await makerAPI.generateImage(req);
          break;
        case 'video':
          response = await makerAPI.generateVideo(req);
          break;
        case 'music':
          response = await makerAPI.generateMusic(req);
          break;
        case 'book':
          response = await makerAPI.generateBook(req);
          break;
        default:
          return;
      }

      const jobId = response.data.job_id;

      // Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const job = await makerAPI.getJob(jobId);

          if (job.data.status === 'completed') {
            clearInterval(pollInterval);
            setResult(job.data);
            setLoading(false);
            loadBalance();
            await Haptics.impact({ style: ImpactStyle.Medium });
          } else if (job.data.status === 'failed') {
            clearInterval(pollInterval);
            setLoading(false);
            alert('Generation failed: ' + job.data.error_message);
          }
        } catch (err) {
          console.error('Poll error:', err);
        }
      }, 2000);

      // Timeout after 2 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (loading) {
          setLoading(false);
          alert('Generation timeout - check your queue');
        }
      }, 120000);

    } catch (err: any) {
      setLoading(false);
      const errorMsg = err.response?.data?.detail?.message || 'Generation failed';
      alert(errorMsg);
    }
  };

  const watchAd = async () => {
    try {
      await Haptics.impact({ style: ImpactStyle.Light });

      // Check availability first
      const avail = await rewardsAPI.getAdAvailability();
      if (!avail.data.available) {
        alert(`Daily ad limit reached. ${avail.data.remaining} ads remaining today.`);
        return;
      }

      // Show ad
      await AdMob.prepareRewardVideoAd({
        adId: 'ca-app-pub-3940256099942544/5224354917', // Test ad ID
      });

      const result = await AdMob.showRewardVideoAd();

      if (result) {
        // Reward tokens
        const reward = await rewardsAPI.completeAd('admob', 'test-ad-unit');
        await Haptics.impact({ style: ImpactStyle.Heavy });
        alert(`🎁 Earned ${reward.data.tokens_awarded} tokens!`);
        loadBalance();
      }

    } catch (err) {
      console.error('Ad error:', err);
      alert('Ad not available. Try again later.');
    }
  };

  const createPrint = async () => {
    if (!result?.output_url) {
      alert('Generate an image first!');
      return;
    }

    if (!printifyShopId) {
      alert('Connect your Printify shop first in Settings');
      return;
    }

    try {
      setLoading(true);

      // 1. Upload image to Printify
      const upload = await printify.uploadImageFromUrl(
        printifyShopId,
        result.output_url,
        `maker_${Date.now()}.png`
      );

      const imageId = upload.data.id;

      // 2. Create product (e.g., poster)
      const product = await printify.createProduct(printifyShopId, {
        title: prompt || 'AI Generated Art',
        description: `AI-generated artwork: ${prompt}`,
        blueprint_id: 3, // Poster
        print_provider_id: 1,
        variants: [
          { id: 17887, price: 1999, is_enabled: true }, // 12x16 poster
        ],
        print_areas: [{
          variant_ids: [17887],
          placeholders: [{
            position: 'front',
            images: [{
              id: imageId,
              x: 0.5,
              y: 0.5,
              scale: 1,
              angle: 0
            }]
          }]
        }]
      });

      // 3. Publish to store
      await printify.publishProduct(printifyShopId, product.data.id);

      alert('✓ Print created and published to your store!');
      await Haptics.impact({ style: ImpactStyle.Heavy });
      setLoading(false);

    } catch (err: any) {
      console.error('Printify error:', err);
      alert('Failed to create print: ' + (err.response?.data?.message || err.message));
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'image', icon: ImageIcon, label: 'Image', cost: 1 },
    { id: 'video', icon: Video, label: 'Video', cost: 5 },
    { id: 'music', icon: Music, label: 'Music', cost: 2 },
    { id: 'book', icon: BookOpen, label: 'Book', cost: 15 },
    { id: 'print', icon: ShoppingBag, label: 'Sell Print', cost: 0 },
  ];

  const currentTab = tabs.find(t => t.id === activeTab);

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-300 via-dark-200 to-dark-400">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-dark-200/80 backdrop-blur-xl border-b border-primary-700/20">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary-500" />
            <h1 className="text-xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
              StaticWaves Maker
            </h1>
          </div>

          {/* Token Balance */}
          <div className="hidden sm:flex items-center gap-4">
            <div className="bg-dark-100 px-4 py-2 rounded-lg border border-primary-700/30">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-yellow-400" />
                <span className="font-mono font-bold">{tokenBalance?.balance || 0}</span>
                <span className="text-xs text-gray-400">tokens</span>
              </div>
            </div>

            <button
              onClick={watchAd}
              className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-4 py-2 rounded-lg font-semibold text-sm hover:scale-105 transition-transform"
            >
              🎁 Watch Ad (+5)
            </button>
          </div>

          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="sm:hidden p-2"
          >
            {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="sm:hidden bg-dark-100 border-t border-primary-700/20 p-4">
            <div className="flex flex-col gap-3">
              <div className="bg-dark-200 px-4 py-3 rounded-lg">
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  <span className="font-mono font-bold text-lg">{tokenBalance?.balance || 0}</span>
                  <span className="text-sm text-gray-400">tokens</span>
                </div>
              </div>
              <button
                onClick={() => { watchAd(); setMenuOpen(false); }}
                className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-4 py-3 rounded-lg font-semibold hover:scale-105 transition-transform"
              >
                🎁 Watch Ad for 5 Tokens
              </button>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => { setActiveTab(tab.id as any); setResult(null); }}
              className={`
                flex items-center gap-2 px-4 py-3 rounded-lg font-semibold whitespace-nowrap transition-all
                ${activeTab === tab.id
                  ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/50'
                  : 'bg-dark-100 text-gray-400 hover:bg-dark-50'
                }
              `}
            >
              <tab.icon className="w-5 h-5" />
              <span>{tab.label}</span>
              {tab.cost > 0 && (
                <span className="text-xs opacity-70">({tab.cost} token{tab.cost > 1 ? 's' : ''})</span>
              )}
            </button>
          ))}
        </div>

        {/* Generator Card */}
        <div className="bg-dark-100 rounded-2xl p-6 border border-primary-700/20 shadow-2xl">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            {currentTab && <currentTab.icon className="w-7 h-7 text-primary-500" />}
            Generate {currentTab?.label}
          </h2>

          {activeTab !== 'print' ? (
            <>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder={`Describe your ${activeTab}... (e.g., "cyberpunk neon cityscape")`}
                className="w-full bg-dark-200 text-white rounded-lg px-4 py-3 mb-4 min-h-[120px] resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 border border-primary-700/20"
                disabled={loading}
              />

              <button
                onClick={generate}
                disabled={loading || !prompt.trim()}
                className="w-full bg-gradient-to-r from-primary-600 to-primary-700 text-white py-4 rounded-lg font-bold text-lg hover:scale-[1.02] transition-transform disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Generating...
                  </div>
                ) : (
                  `Generate ${currentTab?.label} (${currentTab?.cost} token${currentTab?.cost! > 1 ? 's' : ''})`
                )}
              </button>

              {/* Result */}
              {result && (
                <div className="mt-6 p-4 bg-dark-200 rounded-lg border border-primary-700/30">
                  <h3 className="font-semibold mb-3 text-green-400">✓ Generated successfully!</h3>

                  {activeTab === 'image' && result.output_url && (
                    <div className="space-y-3">
                      <img
                        src={result.output_url}
                        alt="Generated"
                        className="w-full rounded-lg"
                      />
                      <button
                        onClick={createPrint}
                        className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 rounded-lg font-semibold hover:scale-[1.02] transition-transform"
                      >
                        <ShoppingBag className="w-5 h-5 inline mr-2" />
                        Create & Sell as Print
                      </button>
                    </div>
                  )}

                  {activeTab === 'video' && result.output_url && (
                    <video src={result.output_url} controls className="w-full rounded-lg" />
                  )}

                  {activeTab === 'music' && result.output_url && (
                    <audio src={result.output_url} controls className="w-full" />
                  )}

                  {activeTab === 'book' && result.output_url && (
                    <a
                      href={result.output_url}
                      download
                      className="block w-full bg-blue-600 text-white text-center py-3 rounded-lg font-semibold hover:bg-blue-700"
                    >
                      Download {result.output_format?.toUpperCase() || 'PDF'}
                    </a>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <ShoppingBag className="w-16 h-16 text-primary-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Sell Your Creations</h3>
              <p className="text-gray-400 mb-6">
                Generate an image first, then click "Create & Sell as Print" to add it to your Printify store.
              </p>
              <button
                onClick={() => setActiveTab('image')}
                className="bg-primary-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-primary-700"
              >
                Generate Image
              </button>
            </div>
          )}
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8">
          <div className="bg-dark-100 p-4 rounded-lg border border-primary-700/20">
            <div className="text-3xl font-bold text-primary-500">{tokenBalance?.balance || 0}</div>
            <div className="text-sm text-gray-400">Tokens Available</div>
          </div>
          <div className="bg-dark-100 p-4 rounded-lg border border-primary-700/20">
            <div className="text-3xl font-bold text-green-500">{tokenBalance?.total_earned || 0}</div>
            <div className="text-sm text-gray-400">Tokens Earned</div>
          </div>
          <div className="bg-dark-100 p-4 rounded-lg border border-primary-700/20">
            <div className="text-3xl font-bold text-orange-500">{tokenBalance?.total_spent || 0}</div>
            <div className="text-sm text-gray-400">Tokens Spent</div>
          </div>
        </div>
      </main>
    </div>
  );
}
