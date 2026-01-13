/**
 * Monitoring and Metrics System
 * Provides observability for production pod engine
 */

import { EventEmitter } from 'events'
import { IDatabaseClient } from './DatabaseClient'

export interface MetricValue {
  value: number
  timestamp: Date
  labels?: Record<string, string | number>
}

export interface AggregatedMetric {
  name: string
  type: string
  count: number
  sum: number
  avg: number
  min: number
  max: number
  p50: number
  p95: number
  p99: number
  period: {
    start: Date
    end: Date
  }
}

/**
 * Metrics Collector
 */
export class MetricsCollector extends EventEmitter {
  private db: IDatabaseClient
  private metrics: Map<string, MetricValue[]> = new Map()
  private maxMetricsPerType: number = 10000

  constructor(db: IDatabaseClient) {
    super()
    this.db = db
  }

  /**
   * Record a counter metric (incremental)
   */
  async counter(name: string, value: number = 1, labels?: Record<string, string | number>): Promise<void> {
    await this.record(name, value, 'counter', labels)
  }

  /**
   * Record a gauge metric (point-in-time value)
   */
  async gauge(name: string, value: number, labels?: Record<string, string | number>): Promise<void> {
    await this.record(name, value, 'gauge', labels)
  }

  /**
   * Record a histogram metric (for distributions)
   */
  async histogram(name: string, value: number, labels?: Record<string, string | number>): Promise<void> {
    await this.record(name, value, 'histogram', labels)
  }

  /**
   * Record a timing metric (in milliseconds)
   */
  async timing(name: string, durationMs: number, labels?: Record<string, string | number>): Promise<void> {
    await this.record(`${name}_duration_ms`, durationMs, 'histogram', labels)
  }

  /**
   * Time a function execution
   */
  async time<T>(name: string, fn: () => Promise<T>, labels?: Record<string, string | number>): Promise<T> {
    const start = Date.now()
    try {
      const result = await fn()
      const duration = Date.now() - start
      await this.timing(name, duration, { ...labels, status: 'success' })
      return result
    } catch (error) {
      const duration = Date.now() - start
      await this.timing(name, duration, { ...labels, status: 'error' })
      throw error
    }
  }

  /**
   * Record a metric
   */
  private async record(
    name: string,
    value: number,
    type: string,
    labels?: Record<string, string | number>
  ): Promise<void> {
    const metric: MetricValue = {
      value,
      timestamp: new Date(),
      labels
    }

    // Store in memory
    if (!this.metrics.has(name)) {
      this.metrics.set(name, [])
    }
    const values = this.metrics.get(name)!
    values.push(metric)

    // Limit memory usage
    if (values.length > this.maxMetricsPerType) {
      values.shift()
    }

    // Store in database
    try {
      await this.db.recordMetric({
        metric_type: type,
        metric_name: name,
        metric_value: value,
        labels
      })
    } catch (error) {
      console.error('[Metrics] Failed to record metric:', error)
    }

    this.emit('metric', { name, value, type, labels })
  }

  /**
   * Get aggregated metrics for a time period
   */
  async getAggregated(
    name: string,
    period: { start: Date; end: Date }
  ): Promise<AggregatedMetric | null> {
    try {
      const metrics = await this.db.getMetrics('histogram', period)
      const filtered = metrics.filter(m => m.metric_name === name)

      if (filtered.length === 0) {
        return null
      }

      const values = filtered.map(m => m.metric_value).sort((a, b) => a - b)
      const sum = values.reduce((acc, v) => acc + v, 0)
      const count = values.length

      return {
        name,
        type: 'histogram',
        count,
        sum,
        avg: sum / count,
        min: values[0],
        max: values[values.length - 1],
        p50: this.percentile(values, 50),
        p95: this.percentile(values, 95),
        p99: this.percentile(values, 99),
        period
      }
    } catch (error) {
      console.error('[Metrics] Failed to get aggregated metrics:', error)
      return null
    }
  }

  /**
   * Calculate percentile
   */
  private percentile(sortedValues: number[], p: number): number {
    if (sortedValues.length === 0) return 0
    const index = Math.ceil((p / 100) * sortedValues.length) - 1
    return sortedValues[Math.max(0, index)]
  }

  /**
   * Get recent metrics from memory
   */
  getRecent(name: string, limit: number = 100): MetricValue[] {
    const values = this.metrics.get(name) || []
    return values.slice(-limit)
  }

  /**
   * Clear all metrics
   */
  clear(): void {
    this.metrics.clear()
  }
}

/**
 * Health Check System
 */
export interface HealthStatus {
  healthy: boolean
  checks: Record<string, {
    healthy: boolean
    message?: string
    timestamp: Date
  }>
}

export class HealthChecker {
  private checks: Map<string, () => Promise<boolean>> = new Map()

  /**
   * Register a health check
   */
  register(name: string, check: () => Promise<boolean>): void {
    this.checks.set(name, check)
  }

  /**
   * Run all health checks
   */
  async check(): Promise<HealthStatus> {
    const results: HealthStatus = {
      healthy: true,
      checks: {}
    }

    for (const [name, check] of this.checks.entries()) {
      try {
        const healthy = await check()
        results.checks[name] = {
          healthy,
          timestamp: new Date()
        }

        if (!healthy) {
          results.healthy = false
        }
      } catch (error) {
        results.checks[name] = {
          healthy: false,
          message: error instanceof Error ? error.message : String(error),
          timestamp: new Date()
        }
        results.healthy = false
      }
    }

    return results
  }

  /**
   * Check a specific component
   */
  async checkOne(name: string): Promise<boolean> {
    const check = this.checks.get(name)
    if (!check) {
      throw new Error(`Health check '${name}' not found`)
    }

    try {
      return await check()
    } catch (error) {
      return false
    }
  }
}

/**
 * Performance Monitor
 */
export class PerformanceMonitor {
  private metrics: MetricsCollector
  private timers: Map<string, number> = new Map()

  constructor(metrics: MetricsCollector) {
    this.metrics = metrics
  }

  /**
   * Start timing an operation
   */
  start(operationId: string): void {
    this.timers.set(operationId, Date.now())
  }

  /**
   * End timing and record metric
   */
  async end(operationId: string, metricName: string, labels?: Record<string, string | number>): Promise<number> {
    const startTime = this.timers.get(operationId)
    if (!startTime) {
      throw new Error(`No timer found for operation: ${operationId}`)
    }

    const duration = Date.now() - startTime
    this.timers.delete(operationId)

    await this.metrics.timing(metricName, duration, labels)

    return duration
  }

  /**
   * Measure function execution
   */
  async measure<T>(
    metricName: string,
    fn: () => Promise<T>,
    labels?: Record<string, string | number>
  ): Promise<T> {
    return await this.metrics.time(metricName, fn, labels)
  }
}

/**
 * Alert Manager
 */
export interface Alert {
  id: string
  name: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  message: string
  timestamp: Date
  metadata?: any
}

export class AlertManager extends EventEmitter {
  private alerts: Map<string, Alert> = new Map()
  private maxAlerts: number = 1000

  /**
   * Trigger an alert
   */
  trigger(
    name: string,
    severity: Alert['severity'],
    message: string,
    metadata?: any
  ): Alert {
    const alert: Alert = {
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name,
      severity,
      message,
      timestamp: new Date(),
      metadata
    }

    this.alerts.set(alert.id, alert)

    // Limit memory usage
    if (this.alerts.size > this.maxAlerts) {
      const oldest = Array.from(this.alerts.keys())[0]
      this.alerts.delete(oldest)
    }

    this.emit('alert', alert)
    console.log(`[Alert:${severity.toUpperCase()}] ${name}: ${message}`)

    return alert
  }

  /**
   * Get recent alerts
   */
  getRecent(limit: number = 100): Alert[] {
    const alerts = Array.from(this.alerts.values())
    alerts.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
    return alerts.slice(0, limit)
  }

  /**
   * Get alerts by severity
   */
  getBySeverity(severity: Alert['severity']): Alert[] {
    return Array.from(this.alerts.values())
      .filter(a => a.severity === severity)
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
  }

  /**
   * Clear all alerts
   */
  clear(): void {
    this.alerts.clear()
  }
}

/**
 * Dashboard Data Provider
 */
export interface DashboardData {
  overview: {
    totalJobs: number
    completedJobs: number
    failedJobs: number
    successRate: number
    avgProcessingTime: number
  }
  recent: {
    jobs: any[]
    alerts: Alert[]
    metrics: Record<string, MetricValue[]>
  }
  performance: {
    jobDuration: AggregatedMetric | null
    imageGeneration: AggregatedMetric | null
    productCreation: AggregatedMetric | null
  }
}

export class DashboardProvider {
  private db: IDatabaseClient
  private metrics: MetricsCollector
  private alerts: AlertManager

  constructor(db: IDatabaseClient, metrics: MetricsCollector, alerts: AlertManager) {
    this.db = db
    this.metrics = metrics
    this.alerts = alerts
  }

  /**
   * Get dashboard data
   */
  async getData(timeRange?: { start: Date; end: Date }): Promise<DashboardData> {
    const now = new Date()
    const range = timeRange || {
      start: new Date(now.getTime() - 24 * 60 * 60 * 1000), // Last 24 hours
      end: now
    }

    // Get job statistics
    const allJobs = await this.db.listJobs()
    const completedJobs = allJobs.filter(j => j.status === 'completed')
    const failedJobs = allJobs.filter(j => j.status === 'failed')

    // Calculate average processing time
    const processingTimes = completedJobs
      .filter(j => j.started_at && j.completed_at)
      .map(j => j.completed_at!.getTime() - j.started_at!.getTime())

    const avgProcessingTime = processingTimes.length > 0
      ? processingTimes.reduce((a, b) => a + b, 0) / processingTimes.length
      : 0

    // Get performance metrics
    const jobDuration = await this.metrics.getAggregated('job_duration', range)
    const imageGeneration = await this.metrics.getAggregated('image_generation_duration_ms', range)
    const productCreation = await this.metrics.getAggregated('product_creation_duration_ms', range)

    return {
      overview: {
        totalJobs: allJobs.length,
        completedJobs: completedJobs.length,
        failedJobs: failedJobs.length,
        successRate: allJobs.length > 0 ? (completedJobs.length / allJobs.length) * 100 : 0,
        avgProcessingTime
      },
      recent: {
        jobs: allJobs.slice(-10).reverse(),
        alerts: this.alerts.getRecent(20),
        metrics: {
          job_duration: this.metrics.getRecent('job_duration', 50),
          jobs_completed: this.metrics.getRecent('jobs_completed', 50),
          jobs_failed: this.metrics.getRecent('jobs_failed', 50)
        }
      },
      performance: {
        jobDuration,
        imageGeneration,
        productCreation
      }
    }
  }
}
