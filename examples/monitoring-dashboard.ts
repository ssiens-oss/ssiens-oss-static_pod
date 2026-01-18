/**
 * Monitoring Dashboard for POD Pipeline
 *
 * Provides real-time monitoring of circuit breakers, cache stats,
 * and pipeline health metrics.
 */

import { Orchestrator } from '../services/orchestrator';

interface DashboardMetrics {
  timestamp: string;
  pipeline: {
    totalRuns: number;
    successRate: string;
    totalProducts: number;
    totalErrors: number;
  };
  circuitBreakers: Record<string, {
    state: string;
    healthy: boolean;
    failureCount: number;
  }>;
  services: {
    comfyui: {
      healthy: boolean;
      timeout: number;
      maxRetries: number;
    };
    printify: {
      enabled: boolean;
      cacheSize: number;
      cacheHitRate?: number;
    };
  };
}

export class MonitoringDashboard {
  private orchestrator: Orchestrator;
  private metricsHistory: DashboardMetrics[] = [];
  private maxHistoryLength = 100;

  constructor(orchestrator: Orchestrator) {
    this.orchestrator = orchestrator;
  }

  /**
   * Collect current metrics
   */
  async collectMetrics(): Promise<DashboardMetrics> {
    const stats = await this.orchestrator.getStats();

    const metrics: DashboardMetrics = {
      timestamp: new Date().toISOString(),
      pipeline: {
        totalRuns: stats.pipeline.totalRuns,
        successRate: stats.pipeline.successRate,
        totalProducts: stats.pipeline.totalProducts,
        totalErrors: stats.pipeline.totalErrors
      },
      circuitBreakers: stats.circuitBreakers,
      services: {
        comfyui: {
          healthy: stats.services.comfyui.healthy,
          timeout: stats.services.comfyui.metrics?.config?.timeout || 0,
          maxRetries: stats.services.comfyui.metrics?.config?.maxRetries || 0
        },
        printify: {
          enabled: stats.services.printify.enabled,
          cacheSize: stats.services.printify.metrics?.cache?.size || 0
        }
      }
    };

    // Store in history
    this.metricsHistory.push(metrics);
    if (this.metricsHistory.length > this.maxHistoryLength) {
      this.metricsHistory.shift();
    }

    return metrics;
  }

  /**
   * Display dashboard in terminal
   */
  async displayDashboard(): Promise<void> {
    const metrics = await this.collectMetrics();

    console.clear();
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║              POD Pipeline Monitoring Dashboard             ║');
    console.log('╠════════════════════════════════════════════════════════════╣');

    // Pipeline Stats
    console.log('║  📊 PIPELINE STATISTICS                                    ║');
    console.log('╠════════════════════════════════════════════════════════════╣');
    console.log(`║  Total Runs:        ${String(metrics.pipeline.totalRuns).padEnd(40)} ║`);
    console.log(`║  Success Rate:      ${metrics.pipeline.successRate.padEnd(40)} ║`);
    console.log(`║  Products Created:  ${String(metrics.pipeline.totalProducts).padEnd(40)} ║`);
    console.log(`║  Total Errors:      ${String(metrics.pipeline.totalErrors).padEnd(40)} ║`);

    // Circuit Breakers
    console.log('╠════════════════════════════════════════════════════════════╣');
    console.log('║  🔌 CIRCUIT BREAKERS                                       ║');
    console.log('╠════════════════════════════════════════════════════════════╣');

    Object.entries(metrics.circuitBreakers).forEach(([service, status]) => {
      const icon = status.healthy ? '✅' : '❌';
      const state = status.state.padEnd(10);
      console.log(`║  ${icon} ${service.padEnd(12)} ${state} (fails: ${status.failureCount})${' '.repeat(10)} ║`);
    });

    // Services
    console.log('╠════════════════════════════════════════════════════════════╣');
    console.log('║  🔧 SERVICES                                               ║');
    console.log('╠════════════════════════════════════════════════════════════╣');

    const comfyIcon = metrics.services.comfyui.healthy ? '✅' : '❌';
    console.log(`║  ${comfyIcon} ComfyUI:       ${metrics.services.comfyui.healthy ? 'HEALTHY' : 'UNHEALTHY'.padEnd(35)} ║`);
    console.log(`║     Timeout:       ${String(metrics.services.comfyui.timeout / 1000)}s${' '.repeat(32)} ║`);
    console.log(`║     Max Retries:   ${String(metrics.services.comfyui.maxRetries).padEnd(40)} ║`);

    const printifyIcon = metrics.services.printify.enabled ? '✅' : '⚪';
    console.log(`║  ${printifyIcon} Printify:     ${metrics.services.printify.enabled ? 'ENABLED' : 'DISABLED'.padEnd(35)} ║`);
    console.log(`║     Cache Size:    ${String(metrics.services.printify.cacheSize).padEnd(40)} ║`);

    console.log('╚════════════════════════════════════════════════════════════╝');
    console.log(`\n Last updated: ${metrics.timestamp}`);
  }

  /**
   * Start auto-refresh dashboard
   */
  startAutoRefresh(intervalMs: number = 5000): () => void {
    const intervalId = setInterval(() => {
      this.displayDashboard().catch(console.error);
    }, intervalMs);

    // Initial display
    this.displayDashboard().catch(console.error);

    // Return stop function
    return () => clearInterval(intervalId);
  }

  /**
   * Export metrics to JSON
   */
  exportMetrics(filename: string): void {
    const fs = require('fs');
    fs.writeFileSync(
      filename,
      JSON.stringify({
        exported: new Date().toISOString(),
        current: this.metricsHistory[this.metricsHistory.length - 1],
        history: this.metricsHistory
      }, null, 2)
    );
    console.log(`✓ Metrics exported to ${filename}`);
  }

  /**
   * Get metrics summary
   */
  getSummary(): {
    avgSuccessRate: number;
    totalProducts: number;
    mostRecentErrors: number;
  } {
    if (this.metricsHistory.length === 0) {
      return { avgSuccessRate: 0, totalProducts: 0, mostRecentErrors: 0 };
    }

    const recent = this.metricsHistory[this.metricsHistory.length - 1];

    return {
      avgSuccessRate: parseFloat(recent.pipeline.successRate),
      totalProducts: recent.pipeline.totalProducts,
      mostRecentErrors: recent.pipeline.totalErrors
    };
  }

  /**
   * Check for alerts
   */
  async checkAlerts(): Promise<string[]> {
    const metrics = await this.collectMetrics();
    const alerts: string[] = [];

    // Check circuit breakers
    Object.entries(metrics.circuitBreakers).forEach(([service, status]) => {
      if (!status.healthy) {
        alerts.push(`⚠️  ${service} circuit breaker is OPEN`);
      }
    });

    // Check success rate
    const successRate = parseFloat(metrics.pipeline.successRate);
    if (successRate < 80 && metrics.pipeline.totalRuns > 5) {
      alerts.push(`⚠️  Success rate is low: ${metrics.pipeline.successRate}`);
    }

    // Check service health
    if (!metrics.services.comfyui.healthy) {
      alerts.push('⚠️  ComfyUI service is unhealthy');
    }

    return alerts;
  }
}

// ============================================================================
// Example Usage
// ============================================================================

export async function startMonitoring(orchestrator: Orchestrator) {
  const dashboard = new MonitoringDashboard(orchestrator);

  console.log('🔍 Starting POD Pipeline Monitoring...\n');

  // Display dashboard every 5 seconds
  const stopRefresh = dashboard.startAutoRefresh(5000);

  // Check for alerts every 10 seconds
  const alertInterval = setInterval(async () => {
    const alerts = await dashboard.checkAlerts();
    if (alerts.length > 0) {
      console.log('\n🚨 ALERTS:');
      alerts.forEach(alert => console.log(`   ${alert}`));
    }
  }, 10000);

  // Handle shutdown
  process.on('SIGINT', () => {
    console.log('\n\n📊 Exporting metrics before shutdown...');
    dashboard.exportMetrics('pipeline-metrics.json');
    stopRefresh();
    clearInterval(alertInterval);
    process.exit(0);
  });

  return dashboard;
}
