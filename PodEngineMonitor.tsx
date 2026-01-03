/**
 * POD Engine Monitoring Dashboard
 * Real-time monitoring and control interface for the production POD engine
 */

import React, { useState, useEffect } from 'react'
import {
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  Play,
  Pause,
  AlertCircle,
  TrendingUp,
  Package,
  Zap
} from 'lucide-react'

interface Metrics {
  totalJobs: number
  pendingJobs: number
  runningJobs: number
  completedJobs: number
  failedJobs: number
  cancelledJobs: number
  successRate: number
  averageJobTime: number
  uptime: number
}

interface Job {
  id: string
  type: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  priority: string
  prompt?: string
  progress?: number
  createdAt: number
  startedAt?: number
  completedAt?: number
  error?: string
}

interface HealthStatus {
  status: 'healthy' | 'unhealthy'
  uptime: number
  timestamp: string
}

const API_BASE = 'http://localhost:3000'

export default function PodEngineMonitor() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [prompt, setPrompt] = useState('')
  const [priority, setPriority] = useState<'low' | 'normal' | 'high' | 'urgent'>('normal')
  const [submitting, setSubmitting] = useState(false)

  // Fetch data
  const fetchData = async () => {
    try {
      // Fetch metrics
      const metricsRes = await fetch(`${API_BASE}/api/metrics`)
      if (metricsRes.ok) {
        const metricsData = await metricsRes.json()
        setMetrics(metricsData)
      }

      // Fetch jobs
      const jobsRes = await fetch(`${API_BASE}/api/jobs?limit=50`)
      if (jobsRes.ok) {
        const jobsData = await jobsRes.json()
        setJobs(jobsData.jobs || [])
      }

      // Fetch health
      const healthRes = await fetch(`${API_BASE}/health`)
      if (healthRes.ok) {
        const healthData = await healthRes.json()
        setHealth(healthData)
      }
    } catch (error) {
      console.error('Failed to fetch data:', error)
    }
  }

  // Auto-refresh
  useEffect(() => {
    fetchData()

    if (autoRefresh) {
      const interval = setInterval(fetchData, 3000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  // Submit job
  const handleSubmitJob = async () => {
    if (!prompt.trim()) return

    setSubmitting(true)
    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt.trim(),
          productTypes: ['tshirt'],
          autoPublish: false,
          priority
        })
      })

      if (res.ok) {
        const data = await res.json()
        console.log('Job submitted:', data.jobId)
        setPrompt('')
        fetchData()
      }
    } catch (error) {
      console.error('Failed to submit job:', error)
    } finally {
      setSubmitting(false)
    }
  }

  // Format duration
  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`
    const seconds = Math.floor(ms / 1000)
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    return `${hours}h ${minutes % 60}m`
  }

  // Format timestamp
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Activity className="w-8 h-8 text-blue-400" />
              POD Engine Monitor
            </h1>
            <p className="text-gray-400 mt-1">Production Print-on-Demand Automation</p>
          </div>

          <div className="flex items-center gap-4">
            {/* Health Status */}
            {health && (
              <div className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                health.status === 'healthy'
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-red-500/20 text-red-400'
              }`}>
                {health.status === 'healthy' ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <AlertCircle className="w-5 h-5" />
                )}
                <span className="font-semibold">{health.status.toUpperCase()}</span>
              </div>
            )}

            {/* Auto-refresh toggle */}
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                autoRefresh
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              {autoRefresh ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {autoRefresh ? 'Live' : 'Paused'}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-6">
        {/* Metrics Cards */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total Jobs */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Jobs</p>
                  <p className="text-3xl font-bold mt-1">{metrics.totalJobs}</p>
                </div>
                <Package className="w-10 h-10 text-blue-400 opacity-50" />
              </div>
            </div>

            {/* Success Rate */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Success Rate</p>
                  <p className="text-3xl font-bold mt-1 text-green-400">
                    {metrics.successRate.toFixed(1)}%
                  </p>
                </div>
                <TrendingUp className="w-10 h-10 text-green-400 opacity-50" />
              </div>
            </div>

            {/* Running Jobs */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Running / Pending</p>
                  <p className="text-3xl font-bold mt-1">
                    {metrics.runningJobs} / {metrics.pendingJobs}
                  </p>
                </div>
                <Zap className="w-10 h-10 text-yellow-400 opacity-50" />
              </div>
            </div>

            {/* Avg Time */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Avg Job Time</p>
                  <p className="text-3xl font-bold mt-1">
                    {formatDuration(metrics.averageJobTime)}
                  </p>
                </div>
                <Clock className="w-10 h-10 text-purple-400 opacity-50" />
              </div>
            </div>

            {/* Completed */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <p className="text-gray-400 text-sm">Completed</p>
              <p className="text-2xl font-bold text-green-400 mt-1">{metrics.completedJobs}</p>
            </div>

            {/* Failed */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <p className="text-gray-400 text-sm">Failed</p>
              <p className="text-2xl font-bold text-red-400 mt-1">{metrics.failedJobs}</p>
            </div>

            {/* Cancelled */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <p className="text-gray-400 text-sm">Cancelled</p>
              <p className="text-2xl font-bold text-gray-400 mt-1">{metrics.cancelledJobs}</p>
            </div>

            {/* Uptime */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <p className="text-gray-400 text-sm">Uptime</p>
              <p className="text-2xl font-bold text-blue-400 mt-1">
                {formatDuration(metrics.uptime)}
              </p>
            </div>
          </div>
        )}

        {/* Job Submission */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold mb-4">Submit New Job</h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter design prompt..."
              className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleSubmitJob()}
            />
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as any)}
              className="px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
            >
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
            <button
              onClick={handleSubmitJob}
              disabled={submitting || !prompt.trim()}
              className="px-6 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold transition-colors"
            >
              {submitting ? 'Submitting...' : 'Submit Job'}
            </button>
          </div>
        </div>

        {/* Jobs List */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold mb-4">Recent Jobs</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {jobs.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No jobs yet</p>
            ) : (
              jobs.map((job) => (
                <div
                  key={job.id}
                  className="bg-gray-700 rounded-lg p-4 flex items-center justify-between hover:bg-gray-650 transition-colors"
                >
                  <div className="flex items-center gap-4 flex-1">
                    {/* Status Icon */}
                    <div>
                      {job.status === 'completed' && (
                        <CheckCircle className="w-6 h-6 text-green-400" />
                      )}
                      {job.status === 'failed' && (
                        <XCircle className="w-6 h-6 text-red-400" />
                      )}
                      {job.status === 'running' && (
                        <Activity className="w-6 h-6 text-blue-400 animate-pulse" />
                      )}
                      {job.status === 'pending' && (
                        <Clock className="w-6 h-6 text-yellow-400" />
                      )}
                      {job.status === 'cancelled' && (
                        <XCircle className="w-6 h-6 text-gray-400" />
                      )}
                    </div>

                    {/* Job Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm text-gray-400">
                          {job.id.slice(0, 20)}...
                        </span>
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                          job.priority === 'urgent' ? 'bg-red-500/20 text-red-400' :
                          job.priority === 'high' ? 'bg-orange-500/20 text-orange-400' :
                          job.priority === 'normal' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {job.priority}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                          job.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                          job.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                          job.status === 'running' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {job.status}
                        </span>
                      </div>
                      {job.prompt && (
                        <p className="text-sm text-gray-300 mt-1 truncate">
                          {job.prompt}
                        </p>
                      )}
                      {job.error && (
                        <p className="text-sm text-red-400 mt-1 truncate">
                          Error: {job.error}
                        </p>
                      )}
                    </div>

                    {/* Progress Bar */}
                    {job.status === 'running' && job.progress !== undefined && (
                      <div className="w-32">
                        <div className="bg-gray-600 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full transition-all"
                            style={{ width: `${job.progress}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-400 mt-1 text-center">
                          {job.progress}%
                        </p>
                      </div>
                    )}

                    {/* Time */}
                    <div className="text-right text-sm text-gray-400">
                      <p>{formatTime(job.createdAt)}</p>
                      {job.completedAt && job.startedAt && (
                        <p className="text-xs">
                          {formatDuration(job.completedAt - job.startedAt)}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
