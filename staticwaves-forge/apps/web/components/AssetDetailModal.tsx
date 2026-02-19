'use client'

import { X, Download, Share2, Trash2, Copy, ExternalLink } from 'lucide-react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment, Grid, PerspectiveCamera } from '@react-three/drei'

interface Asset {
  id: string
  name: string
  type: string
  style: string
  created: string
  size: string
  polyCount: number
  downloads: number
  prompt?: string
  seed?: number
  exportFormats?: string[]
}

interface AssetDetailModalProps {
  asset: Asset
  isOpen: boolean
  onClose: () => void
  onDownload?: (format: string) => void
  onDelete?: () => void
  onShare?: () => void
}

export default function AssetDetailModal({
  asset,
  isOpen,
  onClose,
  onDownload,
  onDelete,
  onShare
}: AssetDetailModalProps) {
  if (!isOpen) return null

  const formats = asset.exportFormats || ['GLB', 'FBX', 'OBJ', 'GLTF']

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <div>
            <h2 className="text-2xl font-bold mb-1">{asset.name}</h2>
            <div className="flex items-center gap-3 text-sm text-gray-400">
              <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded">
                {asset.type}
              </span>
              <span>{asset.style}</span>
              <span>•</span>
              <span>{asset.created}</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          {/* 3D Viewport */}
          <div className="space-y-4">
            <div className="aspect-square bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl overflow-hidden border border-gray-700">
              <Canvas>
                <PerspectiveCamera makeDefault position={[3, 3, 3]} />
                <OrbitControls
                  enablePan={true}
                  enableZoom={true}
                  enableRotate={true}
                  minDistance={2}
                  maxDistance={10}
                />
                <ambientLight intensity={0.5} />
                <directionalLight position={[5, 5, 5]} intensity={1} />
                <Environment preset="studio" />
                <Grid args={[10, 10]} cellColor="#444" sectionColor="#666" />

                {/* Placeholder mesh - replace with actual model loader */}
                <mesh>
                  <boxGeometry args={[1, 1, 1]} />
                  <meshStandardMaterial color="#3b82f6" />
                </mesh>
              </Canvas>
            </div>

            {/* Viewport Controls */}
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <div className="px-3 py-1.5 bg-gray-800/50 rounded">
                🖱️ Left: Rotate
              </div>
              <div className="px-3 py-1.5 bg-gray-800/50 rounded">
                🖱️ Right: Pan
              </div>
              <div className="px-3 py-1.5 bg-gray-800/50 rounded">
                🖱️ Scroll: Zoom
              </div>
            </div>
          </div>

          {/* Details */}
          <div className="space-y-6">
            {/* Stats */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Asset Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-800/50 rounded-lg p-3">
                  <div className="text-sm text-gray-400 mb-1">Polygon Count</div>
                  <div className="text-xl font-bold">
                    {asset.polyCount.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-3">
                  <div className="text-sm text-gray-400 mb-1">File Size</div>
                  <div className="text-xl font-bold">{asset.size}</div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-3">
                  <div className="text-sm text-gray-400 mb-1">Downloads</div>
                  <div className="text-xl font-bold">{asset.downloads}</div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-3">
                  <div className="text-sm text-gray-400 mb-1">Style</div>
                  <div className="text-xl font-bold capitalize">{asset.style}</div>
                </div>
              </div>
            </div>

            {/* Generation Details */}
            {asset.prompt && (
              <div>
                <h3 className="text-lg font-semibold mb-3">Generation Details</h3>
                <div className="space-y-3">
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="text-sm text-gray-400 mb-2">Prompt</div>
                    <div className="text-sm font-medium">{asset.prompt}</div>
                  </div>
                  {asset.seed && (
                    <div className="bg-gray-800/50 rounded-lg p-4">
                      <div className="text-sm text-gray-400 mb-2">Seed</div>
                      <div className="flex items-center gap-2">
                        <code className="text-sm font-mono text-blue-400">
                          {asset.seed}
                        </code>
                        <button
                          onClick={() => navigator.clipboard.writeText(asset.seed!.toString())}
                          className="p-1 hover:bg-gray-700 rounded transition-colors"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Export Formats */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Available Formats</h3>
              <div className="grid grid-cols-2 gap-2">
                {formats.map((format) => (
                  <button
                    key={format}
                    onClick={() => onDownload?.(format)}
                    className="flex items-center justify-between px-4 py-3 bg-gray-800/50 hover:bg-gray-800 rounded-lg transition-colors group"
                  >
                    <span className="font-medium">{format}</span>
                    <Download className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4 border-t border-gray-800">
              <button
                onClick={() => onDownload?.('GLB')}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
              >
                <Download className="w-5 h-5" />
                Download
              </button>
              <button
                onClick={onShare}
                className="px-4 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <Share2 className="w-5 h-5" />
              </button>
              <button
                onClick={() => window.open(`/generate?prompt=${asset.prompt}`, '_blank')}
                className="px-4 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <ExternalLink className="w-5 h-5" />
              </button>
              <button
                onClick={onDelete}
                className="px-4 py-3 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
