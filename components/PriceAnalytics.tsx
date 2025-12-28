import React from 'react';
import { DollarSign, TrendingUp, TrendingDown, Lock, Eye } from 'lucide-react';
import { PriceBucket, Region } from '../types';

interface PriceAnalyticsProps {
  buckets: PriceBucket[];
  productId: string;
  onLockPrice?: (region: Region, price: number) => void;
}

export const PriceAnalyticsPanel: React.FC<PriceAnalyticsProps> = ({
  buckets,
  productId,
  onLockPrice
}) => {
  const productBuckets = buckets.filter(b => b.productId === productId);

  // Group by region
  const bucketsByRegion = productBuckets.reduce((acc, bucket) => {
    if (!acc[bucket.region]) acc[bucket.region] = [];
    acc[bucket.region].push(bucket);
    return acc;
  }, {} as Record<Region, PriceBucket[]>);

  const getBestBucket = (regionBuckets: PriceBucket[]) => {
    return regionBuckets.reduce((best, current) =>
      current.conversionRate > best.conversionRate ? current : best
    );
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-4">
        <DollarSign className="text-emerald-400" size={20} />
        <h3 className="text-lg font-bold text-slate-100">Winning Price Lock-In</h3>
      </div>

      <div className="space-y-4">
        {Object.entries(bucketsByRegion).map(([region, regionBuckets]) => {
          const bestBucket = getBestBucket(regionBuckets);
          const activeBuckets = regionBuckets.filter(b => b.isActive);

          return (
            <div key={region} className="bg-slate-800 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-slate-100">{region}</span>
                  <span className="text-xs bg-indigo-600/20 text-indigo-300 px-2 py-0.5 rounded">
                    {activeBuckets.length} active
                  </span>
                </div>
                {bestBucket && (
                  <button
                    onClick={() => onLockPrice?.(region as Region, bestBucket.price)}
                    className="flex items-center gap-1 bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1 rounded text-xs"
                  >
                    <Lock size={12} />
                    Lock Winner
                  </button>
                )}
              </div>

              <div className="space-y-2">
                {regionBuckets
                  .sort((a, b) => b.conversionRate - a.conversionRate)
                  .map(bucket => {
                    const isWinner = bucket.id === bestBucket.id;
                    const hasEnoughData = bucket.impressions >= 100;

                    return (
                      <div
                        key={bucket.id}
                        className={`p-3 rounded border ${
                          isWinner
                            ? 'border-emerald-500 bg-emerald-500/10'
                            : bucket.isActive
                            ? 'border-slate-700 bg-slate-900'
                            : 'border-red-500/30 bg-red-500/5'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-lg font-bold text-slate-100">
                              ${bucket.price.toFixed(2)}
                            </span>
                            {isWinner && (
                              <span className="text-xs bg-emerald-600 text-white px-2 py-0.5 rounded">
                                WINNER
                              </span>
                            )}
                            {!bucket.isActive && (
                              <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded">
                                DISABLED
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            {bucket.conversionRate > 0.03 ? (
                              <TrendingUp className="text-emerald-400" size={16} />
                            ) : (
                              <TrendingDown className="text-red-400" size={16} />
                            )}
                            <span
                              className={`text-sm font-semibold ${
                                bucket.conversionRate > 0.03
                                  ? 'text-emerald-400'
                                  : 'text-red-400'
                              }`}
                            >
                              {(bucket.conversionRate * 100).toFixed(2)}%
                            </span>
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div>
                            <div className="text-slate-400">Impressions</div>
                            <div className="flex items-center gap-1 text-slate-200">
                              <Eye size={12} />
                              {bucket.impressions.toLocaleString()}
                            </div>
                          </div>
                          <div>
                            <div className="text-slate-400">Conversions</div>
                            <div className="text-slate-200 font-semibold">
                              {bucket.conversions}
                            </div>
                          </div>
                          <div>
                            <div className="text-slate-400">Revenue</div>
                            <div className="text-slate-200 font-semibold">
                              ${bucket.revenue.toFixed(0)}
                            </div>
                          </div>
                        </div>

                        {!hasEnoughData && bucket.isActive && (
                          <div className="mt-2 text-xs text-amber-400 flex items-center gap-1">
                            <span>⚠️</span>
                            <span>Need {100 - bucket.impressions} more impressions to evaluate</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
