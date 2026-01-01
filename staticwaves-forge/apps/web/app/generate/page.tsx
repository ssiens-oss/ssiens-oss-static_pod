'use client'

import { useState } from 'react'
import PromptPanel from '@/components/PromptPanel'
import Viewport3D from '@/components/Viewport3D'
import ExportPanel from '@/components/ExportPanel'
import JobStatus from '@/components/JobStatus'

export default function GeneratePage() {
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)
  const [previewModel, setPreviewModel] = useState<string | null>(null)

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Asset Generator</h1>
            <p className="text-sm text-gray-400">Create production-ready 3D assets from prompts</p>
          </div>
          <div className="flex gap-3">
            <button className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
              Examples
            </button>
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
              View History
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 grid grid-cols-12 gap-0">
        {/* Left Panel - Prompt & Controls */}
        <div className="col-span-3 border-r border-gray-800 overflow-y-auto">
          <PromptPanel onJobCreated={setCurrentJobId} />
        </div>

        {/* Center - 3D Viewport */}
        <div className="col-span-6 relative bg-black">
          <Viewport3D modelPath={previewModel} />
        </div>

        {/* Right Panel - Export & Status */}
        <div className="col-span-3 border-l border-gray-800 overflow-y-auto">
          <div className="p-6 space-y-6">
            {currentJobId && (
              <JobStatus
                jobId={currentJobId}
                onComplete={(result) => {
                  // Set preview model when generation completes
                  if (result.output_files?.glb) {
                    setPreviewModel(result.output_files.glb)
                  }
                }}
              />
            )}
            <ExportPanel />
          </div>
        </div>
      </div>
    </div>
  )
}
