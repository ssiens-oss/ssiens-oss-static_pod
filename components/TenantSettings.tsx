import React, { useState } from 'react';
import { Settings, Key, Palette, Zap, ShoppingCart, DollarSign } from 'lucide-react';
import { Tenant, TenantSettings } from '../types';

interface TenantSettingsProps {
  tenant: Tenant;
  onUpdateSettings?: (settings: Partial<TenantSettings>) => void;
  onUpgradePlan?: (plan: 'free' | 'starter' | 'pro' | 'enterprise') => void;
}

export const TenantSettingsPanel: React.FC<TenantSettingsProps> = ({
  tenant,
  onUpdateSettings,
  onUpgradePlan
}) => {
  const [activeTab, setActiveTab] = useState<'general' | 'integrations' | 'plan'>('general');
  const [settings, setSettings] = useState(tenant.settings);

  const handleBrandingChange = (key: string, value: string) => {
    const newSettings = {
      ...settings,
      branding: { ...settings.branding, [key]: value }
    };
    setSettings(newSettings);
    onUpdateSettings?.(newSettings);
  };

  const handleIntegrationChange = (key: string, value: string) => {
    const newSettings = {
      ...settings,
      integrations: { ...settings.integrations, [key]: value }
    };
    setSettings(newSettings);
    onUpdateSettings?.(newSettings);
  };

  const planFeatures = {
    free: ['10 Products', 'Basic Analytics', 'Email Support'],
    starter: ['100 Products', 'Auto-Linking', 'Basic Analytics', 'Email Support'],
    pro: ['1000 Products', 'Auto-Linking', 'Price Lock-In', 'Multi-Region Feeds', 'Priority Support'],
    enterprise: ['Unlimited Products', 'All Features', 'White-Label', 'Dedicated Support', 'Custom Integrations']
  };

  const planPrices = {
    free: 0,
    starter: 29,
    pro: 99,
    enterprise: 299
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-4">
        <Settings className="text-purple-400" size={20} />
        <h3 className="text-lg font-bold text-slate-100">Tenant Settings</h3>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4 border-b border-slate-800">
        {[
          { id: 'general', label: 'General' },
          { id: 'integrations', label: 'Integrations' },
          { id: 'plan', label: 'Plan' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 text-sm font-semibold transition-colors ${
              activeTab === tab.id
                ? 'text-indigo-400 border-b-2 border-indigo-400'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* General Tab */}
      {activeTab === 'general' && (
        <div className="space-y-4">
          {/* API Key */}
          <div>
            <label className="text-xs text-slate-400 mb-2 flex items-center gap-1">
              <Key size={12} />
              API Key
            </label>
            <div className="flex gap-2">
              <input
                type="password"
                value={tenant.apiKey}
                readOnly
                className="flex-1 bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm font-mono"
              />
              <button className="bg-slate-700 hover:bg-slate-600 text-white px-3 py-2 rounded text-xs">
                Copy
              </button>
            </div>
          </div>

          {/* Branding */}
          <div>
            <label className="text-xs text-slate-400 mb-2 flex items-center gap-1">
              <Palette size={12} />
              Branding
            </label>
            <div className="space-y-2">
              <input
                type="text"
                placeholder="Company Name"
                value={settings.branding.companyName}
                onChange={(e) => handleBrandingChange('companyName', e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
              />
              <div className="flex gap-2 items-center">
                <input
                  type="color"
                  value={settings.branding.primaryColor}
                  onChange={(e) => handleBrandingChange('primaryColor', e.target.value)}
                  className="h-10 w-20 bg-slate-800 border border-slate-700 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={settings.branding.primaryColor}
                  onChange={(e) => handleBrandingChange('primaryColor', e.target.value)}
                  className="flex-1 bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm font-mono"
                />
              </div>
            </div>
          </div>

          {/* Features */}
          <div>
            <label className="text-xs text-slate-400 mb-2 block">Enabled Features</label>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(settings.features).map(([key, value]) => {
                if (key === 'maxProducts') return null;
                return (
                  <div key={key} className="bg-slate-800 rounded p-2 flex items-center justify-between">
                    <span className="text-xs text-slate-300 capitalize">
                      {key.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${
                        value ? 'bg-emerald-600 text-white' : 'bg-slate-700 text-slate-400'
                      }`}
                    >
                      {value ? 'ON' : 'OFF'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Integrations Tab */}
      {activeTab === 'integrations' && (
        <div className="space-y-4">
          {/* Shopify */}
          <div>
            <label className="text-xs text-slate-400 mb-2 flex items-center gap-1">
              <ShoppingCart size={12} />
              Shopify Integration
            </label>
            <div className="space-y-2">
              <input
                type="text"
                placeholder="yourstore.myshopify.com"
                value={settings.integrations.shopifyDomain || ''}
                onChange={(e) => handleIntegrationChange('shopifyDomain', e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
              />
              <input
                type="password"
                placeholder="Shopify Access Token"
                value={settings.integrations.shopifyAccessToken || ''}
                onChange={(e) => handleIntegrationChange('shopifyAccessToken', e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
              />
            </div>
          </div>

          {/* Gumroad */}
          <div>
            <label className="text-xs text-slate-400 mb-2 flex items-center gap-1">
              <DollarSign size={12} />
              Gumroad Integration
            </label>
            <input
              type="password"
              placeholder="Gumroad API Key"
              value={settings.integrations.gumroadApiKey || ''}
              onChange={(e) => handleIntegrationChange('gumroadApiKey', e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
            />
          </div>

          {/* TikTok */}
          <div>
            <label className="text-xs text-slate-400 mb-2 flex items-center gap-1">
              <Zap size={12} />
              TikTok Integration
            </label>
            <input
              type="password"
              placeholder="TikTok Access Token"
              value={settings.integrations.tiktokAccessToken || ''}
              onChange={(e) => handleIntegrationChange('tiktokAccessToken', e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
            />
          </div>

          {/* Printify */}
          <div>
            <label className="text-xs text-slate-400 mb-2 block">Printify API Key</label>
            <input
              type="password"
              placeholder="Printify API Key"
              value={settings.integrations.printifyApiKey || ''}
              onChange={(e) => handleIntegrationChange('printifyApiKey', e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
            />
          </div>
        </div>
      )}

      {/* Plan Tab */}
      {activeTab === 'plan' && (
        <div className="space-y-4">
          <div className="bg-indigo-600/20 border border-indigo-500 rounded p-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-bold text-slate-100 capitalize">{tenant.plan} Plan</div>
                <div className="text-xs text-slate-400 mt-1">
                  {tenant.settings.features.maxProducts === Infinity
                    ? 'Unlimited'
                    : tenant.settings.features.maxProducts}{' '}
                  Products
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-indigo-400">
                  ${planPrices[tenant.plan]}
                </div>
                <div className="text-xs text-slate-400">/month</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3">
            {(['free', 'starter', 'pro', 'enterprise'] as const).map(plan => {
              const isCurrentPlan = tenant.plan === plan;
              const canUpgrade = planPrices[plan] > planPrices[tenant.plan];

              return (
                <div
                  key={plan}
                  className={`border rounded-lg p-4 ${
                    isCurrentPlan
                      ? 'border-indigo-500 bg-indigo-500/10'
                      : 'border-slate-700 bg-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-100 capitalize">{plan}</span>
                      {isCurrentPlan && (
                        <span className="text-xs bg-indigo-600 text-white px-2 py-0.5 rounded">
                          Current
                        </span>
                      )}
                    </div>
                    <span className="text-lg font-bold text-slate-100">
                      ${planPrices[plan]}
                      <span className="text-xs text-slate-400">/mo</span>
                    </span>
                  </div>

                  <ul className="space-y-1 mb-3">
                    {planFeatures[plan].map((feature, idx) => (
                      <li key={idx} className="text-xs text-slate-300 flex items-center gap-1">
                        <span className="text-emerald-400">✓</span>
                        {feature}
                      </li>
                    ))}
                  </ul>

                  {canUpgrade && !isCurrentPlan && (
                    <button
                      onClick={() => onUpgradePlan?.(plan)}
                      className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded text-sm font-semibold"
                    >
                      Upgrade
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
