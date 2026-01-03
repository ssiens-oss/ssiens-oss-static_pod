'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface JobStatusProps {
  jobId: string
  onComplete?: (result: any) => void
}

export default function JobStatus({ jobId, onComplete }: JobStatusProps) {
  const [status, setStatus] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/jobs/${jobId}`)
        setStatus(response.data)

        // Call onComplete when job finishes
        if (response.data.status === 'completed' && onComplete) {
          onComplete(response.data)
        }

        // Stop polling if job is done
        if (['completed', 'failed', 'cancelled'].includes(response.data.status)) {
          return
        }

        // Continue polling
        setTimeout(pollStatus, 1000)
      } catch (err) {
        setError('Failed to fetch job status')
      }
    }

    pollStatus()
  }, [jobId, onComplete])

  if (error) {
    return (
      <div className="p-4 bg-red-900/20 border border-red-500/50 rounded-lg">
        <div className="text-red-400">{error}</div>
      </div>
    )
  }

  if (!status) {
    return (
      <div className="p-4 bg-gray-900 border border-gray-700 rounded-lg">
        <div className="text-gray-400">Loading...</div>
      </div>
    )
  }

  const getStatusColor = () => {
    switch (status.status) {
      case 'completed': return 'text-green-400'
      case 'failed': return 'text-red-400'
      case 'processing': return 'text-blue-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case 'completed': return '✅'
      case 'failed': return '❌'
      case 'processing': return '⏳'
      case 'queued': return '⏸️'
      default: return '⏸️'
    }
  }

  return (
    <div className="space-y-4">
      <div className="p-4 bg-gray-900 border border-gray-700 rounded-lg">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold">Generation Status</h3>
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {getStatusIcon()} {status.status}
          </span>
        </div>

        {/* Progress Bar */}
        {status.status === 'processing' && (
          <div className="space-y-2">
            <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-500 h-full transition-all duration-300 ease-out"
                style={{ width: `${status.progress * 100}%` }}
              />
            </div>
            <div className="text-xs text-gray-400 text-center">
              {Math.round(status.progress * 100)}% complete
            </div>
          </div>
        )}

        {/* Job ID */}
        <div className="mt-3 text-xs text-gray-500">
          Job ID: {jobId.slice(0, 8)}...
        </div>

        {/* Error Message */}
        {status.error_message && (
          <div className="mt-3 p-2 bg-red-900/20 border border-red-500/50 rounded text-xs text-red-400">
            {status.error_message}
          </div>
        )}

        {/* Asset Metadata */}
        {status.asset_metadata && (
          <div className="mt-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-400">Polygons:</span>
              <span>{status.asset_metadata.poly_count.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Vertices:</span>
              <span>{status.asset_metadata.vertex_count.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">File Size:</span>
              <span>{status.asset_metadata.file_size_mb.toFixed(2)} MB</span>
            </div>
            {status.asset_metadata.has_rig && (
              <div className="flex justify-between">
                <span className="text-gray-400">Rigged:</span>
                <span className="text-green-400">Yes</span>
              </div>
            )}
          </div>
        )}

        {/* Download Links */}
        {status.output_files && Object.keys(status.output_files).length > 0 && (
          <div className="mt-4">
            <div className="text-xs text-gray-400 mb-2">Downloads:</div>
            <div className="space-y-1">
              {Object.entries(status.output_files).map(([format, path]: [string, any]) => (
                <button
                  key={format}
                  className="w-full py-2 px-3 bg-blue-600 hover:bg-blue-700 rounded text-xs font-medium transition-colors"
                >
                  Download {format.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
