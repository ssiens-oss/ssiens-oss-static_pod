import { Tenant, TenantSettings } from '../types';

/**
 * Multi-Tenant SaaS Manager
 * Handles tenant creation, management, and feature access control
 */
export class TenantManager {
  private tenants: Map<string, Tenant> = new Map();
  private apiKeyToTenant: Map<string, string> = new Map();

  /**
   * Create a new tenant
   */
  createTenant(
    name: string,
    owner: string,
    plan: 'free' | 'starter' | 'pro' | 'enterprise' = 'free'
  ): Tenant {
    const slug = this.generateSlug(name);
    const apiKey = this.generateApiKey();

    const tenant: Tenant = {
      id: this.generateId(),
      name,
      slug,
      plan,
      apiKey,
      settings: this.getDefaultSettings(plan),
      createdAt: new Date().toISOString(),
      owner
    };

    this.tenants.set(tenant.id, tenant);
    this.apiKeyToTenant.set(apiKey, tenant.id);

    return tenant;
  }

  /**
   * Get tenant by ID
   */
  getTenant(tenantId: string): Tenant | undefined {
    return this.tenants.get(tenantId);
  }

  /**
   * Get tenant by API key
   */
  getTenantByApiKey(apiKey: string): Tenant | undefined {
    const tenantId = this.apiKeyToTenant.get(apiKey);
    return tenantId ? this.tenants.get(tenantId) : undefined;
  }

  /**
   * Get tenant by slug
   */
  getTenantBySlug(slug: string): Tenant | undefined {
    return Array.from(this.tenants.values()).find(t => t.slug === slug);
  }

  /**
   * Update tenant settings
   */
  updateTenantSettings(tenantId: string, settings: Partial<TenantSettings>): Tenant | null {
    const tenant = this.tenants.get(tenantId);
    if (!tenant) return null;

    tenant.settings = {
      ...tenant.settings,
      ...settings,
      branding: { ...tenant.settings.branding, ...settings.branding },
      integrations: { ...tenant.settings.integrations, ...settings.integrations },
      features: { ...tenant.settings.features, ...settings.features }
    };

    return tenant;
  }

  /**
   * Update tenant plan
   */
  upgradePlan(
    tenantId: string,
    newPlan: 'free' | 'starter' | 'pro' | 'enterprise'
  ): Tenant | null {
    const tenant = this.tenants.get(tenantId);
    if (!tenant) return null;

    tenant.plan = newPlan;
    tenant.settings.features = this.getFeaturesByPlan(newPlan);

    return tenant;
  }

  /**
   * Check if tenant has access to a feature
   */
  hasFeatureAccess(tenantId: string, feature: keyof TenantSettings['features']): boolean {
    const tenant = this.tenants.get(tenantId);
    if (!tenant) return false;

    return tenant.settings.features[feature] as boolean;
  }

  /**
   * Regenerate API key for tenant
   */
  regenerateApiKey(tenantId: string): string | null {
    const tenant = this.tenants.get(tenantId);
    if (!tenant) return null;

    // Remove old API key mapping
    this.apiKeyToTenant.delete(tenant.apiKey);

    // Generate new API key
    const newApiKey = this.generateApiKey();
    tenant.apiKey = newApiKey;

    // Add new API key mapping
    this.apiKeyToTenant.set(newApiKey, tenantId);

    return newApiKey;
  }

  /**
   * Delete tenant
   */
  deleteTenant(tenantId: string): boolean {
    const tenant = this.tenants.get(tenantId);
    if (!tenant) return false;

    this.apiKeyToTenant.delete(tenant.apiKey);
    this.tenants.delete(tenantId);

    return true;
  }

  /**
   * Get all tenants
   */
  getAllTenants(): Tenant[] {
    return Array.from(this.tenants.values());
  }

  /**
   * Get default settings based on plan
   */
  private getDefaultSettings(plan: string): TenantSettings {
    return {
      branding: {
        primaryColor: '#6366f1',
        companyName: ''
      },
      integrations: {},
      features: this.getFeaturesByPlan(plan)
    };
  }

  /**
   * Get feature limits by plan
   */
  private getFeaturesByPlan(plan: string): TenantSettings['features'] {
    const plans = {
      free: {
        autoLinking: false,
        priceLockIn: false,
        multiRegion: false,
        maxProducts: 10
      },
      starter: {
        autoLinking: true,
        priceLockIn: false,
        multiRegion: false,
        maxProducts: 100
      },
      pro: {
        autoLinking: true,
        priceLockIn: true,
        multiRegion: true,
        maxProducts: 1000
      },
      enterprise: {
        autoLinking: true,
        priceLockIn: true,
        multiRegion: true,
        maxProducts: Infinity
      }
    };

    return plans[plan as keyof typeof plans] || plans.free;
  }

  /**
   * Generate a URL-friendly slug from tenant name
   */
  private generateSlug(name: string): string {
    let slug = name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');

    // Ensure uniqueness
    let counter = 1;
    let uniqueSlug = slug;
    while (this.getTenantBySlug(uniqueSlug)) {
      uniqueSlug = `${slug}-${counter}`;
      counter++;
    }

    return uniqueSlug;
  }

  /**
   * Generate a secure API key
   */
  private generateApiKey(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let key = 'sk_';
    for (let i = 0; i < 32; i++) {
      key += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return key;
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
  }

  /**
   * Validate tenant can perform action based on plan limits
   */
  validateAction(
    tenantId: string,
    action: 'add_product' | 'use_auto_linking' | 'use_price_lock_in' | 'use_multi_region',
    currentCount?: number
  ): { allowed: boolean; reason?: string } {
    const tenant = this.tenants.get(tenantId);
    if (!tenant) {
      return { allowed: false, reason: 'Tenant not found' };
    }

    switch (action) {
      case 'add_product':
        if (currentCount !== undefined && currentCount >= tenant.settings.features.maxProducts) {
          return {
            allowed: false,
            reason: `Product limit reached (${tenant.settings.features.maxProducts}). Upgrade your plan.`
          };
        }
        break;

      case 'use_auto_linking':
        if (!tenant.settings.features.autoLinking) {
          return {
            allowed: false,
            reason: 'Auto-linking not available on your plan. Upgrade to Starter or higher.'
          };
        }
        break;

      case 'use_price_lock_in':
        if (!tenant.settings.features.priceLockIn) {
          return {
            allowed: false,
            reason: 'Price lock-in not available on your plan. Upgrade to Pro or higher.'
          };
        }
        break;

      case 'use_multi_region':
        if (!tenant.settings.features.multiRegion) {
          return {
            allowed: false,
            reason: 'Multi-region feeds not available on your plan. Upgrade to Pro or higher.'
          };
        }
        break;
    }

    return { allowed: true };
  }
}
