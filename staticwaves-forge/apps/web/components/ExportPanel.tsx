'use client'

import { useState } from 'react'

export default function ExportPanel() {
  const [selectedFormats, setSelectedFormats] = useState<string[]>(['glb', 'fbx'])

  const formats = [
    { id: 'glb', name: 'GLB', desc: 'Universal format' },
    { id: 'fbx', name: 'FBX', desc: 'Unity/Unreal' },
    { id: 'obj', name: 'OBJ', desc: 'Static mesh' },
    { id: 'gltf', name: 'GLTF', desc: 'Web-ready' },
  ]

  const toggleFormat = (formatId: string) => {
    setSelectedFormats(prev =>
      prev.includes(formatId)
        ? prev.filter(f => f !== formatId)
        : [...prev, formatId]
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold mb-4">Export Options</h2>

        {/* Format Selection */}
        <div className="space-y-2">
          <label className="text-sm text-gray-400">Export Formats</label>
          <div className="space-y-2">
            {formats.map(format => (
              <label
                key={format.id}
                className="flex items-center gap-3 p-3 bg-gray-900 border border-gray-700 rounded-lg cursor-pointer hover:border-blue-500/50 transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selectedFormats.includes(format.id)}
                  onChange={() => toggleFormat(format.id)}
                  className="w-4 h-4 rounded"
                />
                <div className="flex-1">
                  <div className="font-medium">{format.name}</div>
                  <div className="text-xs text-gray-500">{format.desc}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Download Button */}
        <button
          disabled
          className="w-full mt-4 py-3 bg-gray-700 cursor-not-allowed rounded-lg font-semibold"
        >
          No Asset to Download
        </button>
      </div>

      {/* Quick Actions */}
      <div>
        <h3 className="text-sm font-semibold mb-3">Quick Actions</h3>
        <div className="space-y-2">
          <button className="w-full py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors">
            📦 Add to Pack
          </button>
          <button className="w-full py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors">
            🔄 Generate Variations
          </button>
          <button className="w-full py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors">
            ⚙️ Optimize for Mobile
          </button>
        </div>
      </div>

      {/* Asset Info */}
      <div className="p-4 bg-gray-900 border border-gray-700 rounded-lg">
        <h3 className="text-sm font-semibold mb-2">Asset Info</h3>
        <div className="text-xs space-y-1 text-gray-400">
          <div>Polygons: -</div>
          <div>Vertices: -</div>
          <div>File Size: -</div>
          <div>Animations: -</div>
        </div>
      </div>
    </div>
  )
}
