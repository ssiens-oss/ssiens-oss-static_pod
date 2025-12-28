import React, { useState } from 'react';
import { Globe, Download, FileText, Code, Table } from 'lucide-react';
import { Product, Region, RegionalFeed } from '../types';

interface FeedManagerProps {
  products: Product[];
  onGenerateFeed?: (region: Region, format: 'xml' | 'json' | 'csv') => void;
}

export const FeedManagerPanel: React.FC<FeedManagerProps> = ({
  products,
  onGenerateFeed
}) => {
  const [selectedRegions, setSelectedRegions] = useState<Region[]>([Region.US]);
  const [format, setFormat] = useState<'xml' | 'json' | 'csv'>('json');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedFeeds, setGeneratedFeeds] = useState<RegionalFeed[]>([]);

  const toggleRegion = (region: Region) => {
    setSelectedRegions(prev =>
      prev.includes(region)
        ? prev.filter(r => r !== region)
        : [...prev, region]
    );
  };

  const handleGenerateFeeds = async () => {
    setIsGenerating(true);

    // Simulate feed generation
    setTimeout(() => {
      const feeds: RegionalFeed[] = selectedRegions.map(region => ({
        region,
        products: products.map(p => ({ ...p })),
        currency: region === Region.US ? 'USD' : region === Region.EU ? 'EUR' : 'GBP',
        generatedAt: new Date().toISOString(),
        format
      }));

      setGeneratedFeeds(feeds);
      setIsGenerating(false);

      selectedRegions.forEach(region => {
        onGenerateFeed?.(region, format);
      });
    }, 2000);
  };

  const getFormatIcon = (fmt: string) => {
    switch (fmt) {
      case 'xml':
        return <Code size={16} />;
      case 'csv':
        return <Table size={16} />;
      default:
        return <FileText size={16} />;
    }
  };

  const getCurrencySymbol = (region: Region) => {
    return region === Region.US ? '$' : region === Region.EU ? '€' : '£';
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-4">
        <Globe className="text-blue-400" size={20} />
        <h3 className="text-lg font-bold text-slate-100">Multi-Region Feed Generator</h3>
      </div>

      <div className="space-y-4">
        {/* Region Selection */}
        <div>
          <label className="text-xs text-slate-400 mb-2 block">Select Regions</label>
          <div className="flex gap-2">
            {[Region.US, Region.EU, Region.UK].map(region => (
              <button
                key={region}
                onClick={() => toggleRegion(region)}
                className={`flex-1 py-2 px-3 rounded font-semibold text-sm transition-colors ${
                  selectedRegions.includes(region)
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
              >
                {region}
              </button>
            ))}
          </div>
        </div>

        {/* Format Selection */}
        <div>
          <label className="text-xs text-slate-400 mb-2 block">Output Format</label>
          <div className="grid grid-cols-3 gap-2">
            {(['json', 'xml', 'csv'] as const).map(fmt => (
              <button
                key={fmt}
                onClick={() => setFormat(fmt)}
                className={`flex items-center justify-center gap-1 py-2 rounded font-semibold text-sm transition-colors ${
                  format === fmt
                    ? 'bg-emerald-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
              >
                {getFormatIcon(fmt)}
                {fmt.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Product Count */}
        <div className="bg-slate-800 rounded p-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Products to Export:</span>
            <span className="text-sm font-bold text-slate-100">{products.length}</span>
          </div>
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-slate-400">Total Feeds:</span>
            <span className="text-sm font-bold text-indigo-400">
              {selectedRegions.length} region{selectedRegions.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerateFeeds}
          disabled={isGenerating || selectedRegions.length === 0}
          className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download size={16} />
          {isGenerating ? 'Generating Feeds...' : 'Generate Feeds'}
        </button>

        {/* Generated Feeds */}
        {generatedFeeds.length > 0 && (
          <div className="space-y-2">
            <label className="text-xs text-slate-400">Generated Feeds</label>
            {generatedFeeds.map(feed => (
              <div
                key={feed.region}
                className="bg-slate-800 rounded p-3 flex items-center justify-between"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-slate-100">{feed.region}</span>
                    <span className="text-xs bg-slate-700 px-2 py-0.5 rounded">
                      {feed.format.toUpperCase()}
                    </span>
                    <span className="text-xs text-slate-400">
                      {feed.products.length} products
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Currency: {feed.currency} | Generated: {new Date(feed.generatedAt).toLocaleTimeString()}
                  </div>
                </div>
                <button
                  className="flex items-center gap-1 bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1 rounded text-xs"
                >
                  <Download size={12} />
                  Download
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Pricing Preview */}
        {selectedRegions.length > 0 && products.length > 0 && (
          <div className="bg-slate-800 rounded p-3">
            <div className="text-xs text-slate-400 mb-2">Regional Pricing Preview</div>
            <div className="space-y-1">
              {products.slice(0, 2).map(product => (
                <div key={product.id} className="text-xs">
                  <span className="text-slate-300">{product.name}:</span>
                  <div className="flex gap-2 mt-1">
                    {selectedRegions.map(region => (
                      <span key={region} className="bg-slate-900 px-2 py-0.5 rounded">
                        <span className="text-slate-400">{region}:</span>{' '}
                        <span className="text-emerald-400 font-semibold">
                          {getCurrencySymbol(region)}
                          {product.regionalPricing[region].toFixed(2)}
                        </span>
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
