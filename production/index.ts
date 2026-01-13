/**
 * Production POD Engine
 * Main entry point - exports all components
 */

// Core Engine
export { ProductionPodEngine, EngineConfig, JobRequest, EngineStats } from './ProductionPodEngine'

// Job Queue
export { JobQueue, JobData, JobResult, JobStatus, QueueConfig } from './JobQueue'

// Database
export {
  IDatabaseClient,
  InMemoryDatabaseClient,
  PostgresDatabaseClient,
  createDatabaseClient,
  Job,
  Image,
  Product,
  Worker,
  Metric,
  Log
} from './DatabaseClient'

// Worker Pool
export { WorkerPool, WorkerPoolConfig, WorkerInfo } from './WorkerPool'

// API Server
export { ApiServer, ApiServerConfig, API_DOCS } from './ApiServer'

// Monitoring
export {
  MetricsCollector,
  HealthChecker,
  PerformanceMonitor,
  AlertManager,
  DashboardProvider,
  MetricValue,
  AggregatedMetric,
  HealthStatus,
  Alert,
  DashboardData
} from './Monitoring'

/**
 * Version information
 */
export const VERSION = '1.0.0'

/**
 * Quick start helper
 */
export async function createProductionEngine(config: EngineConfig) {
  const { ProductionPodEngine } = await import('./ProductionPodEngine')
  return new ProductionPodEngine(config)
}

/**
 * Quick start worker pool helper
 */
export async function createWorkerPool(config: WorkerPoolConfig, db: IDatabaseClient) {
  const { WorkerPool } = await import('./WorkerPool')
  return new WorkerPool(config, db)
}
