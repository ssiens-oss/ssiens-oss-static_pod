'use client'

import { useState } from 'react'
import { X, ChevronRight, ChevronLeft, Check, Plus, Trash2 } from 'lucide-react'

interface PackCreationWizardProps {
  isOpen: boolean
  onClose: () => void
  onComplete: (packData: PackData) => void
}

interface PackData {
  name: string
  description: string
  price: number
  category: string
  assets: string[]
  settings: {
    includeAnimations: boolean
    includeLODs: boolean
    formats: string[]
  }
}

export default function PackCreationWizard({
  isOpen,
  onClose,
  onComplete
}: PackCreationWizardProps) {
  const [step, setStep] = useState(1)
  const [packData, setPackData] = useState<PackData>({
    name: '',
    description: '',
    price: 29,
    category: 'fantasy',
    assets: [],
    settings: {
      includeAnimations: true,
      includeLODs: true,
      formats: ['GLB', 'FBX']
    }
  })

  if (!isOpen) return null

  const totalSteps = 4

  const handleNext = () => {
    if (step < totalSteps) setStep(step + 1)
  }

  const handlePrevious = () => {
    if (step > 1) setStep(step - 1)
  }

  const handleComplete = () => {
    onComplete(packData)
    onClose()
  }

  const canProceed = () => {
    switch (step) {
      case 1:
        return packData.name.length > 0 && packData.description.length > 0
      case 2:
        return packData.assets.length > 0
      case 3:
        return packData.settings.formats.length > 0
      case 4:
        return true
      default:
        return false
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl max-w-3xl w-full shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <div>
            <h2 className="text-2xl font-bold mb-1">Create Asset Pack</h2>
            <p className="text-sm text-gray-400">Step {step} of {totalSteps}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 pt-6">
          <div className="flex items-center gap-2">
            {[1, 2, 3, 4].map((s) => (
              <div key={s} className="flex-1 flex items-center gap-2">
                <div className={`h-2 flex-1 rounded-full transition-colors ${
                  s <= step ? 'bg-blue-600' : 'bg-gray-800'
                }`} />
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 min-h-[400px]">
          {step === 1 && <Step1BasicInfo packData={packData} setPackData={setPackData} />}
          {step === 2 && <Step2SelectAssets packData={packData} setPackData={setPackData} />}
          {step === 3 && <Step3ExportSettings packData={packData} setPackData={setPackData} />}
          {step === 4 && <Step4Review packData={packData} />}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-800">
          <button
            onClick={handlePrevious}
            disabled={step === 1}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              step === 1
                ? 'text-gray-600 cursor-not-allowed'
                : 'bg-gray-800 hover:bg-gray-700'
            }`}
          >
            <ChevronLeft className="w-5 h-5" />
            Previous
          </button>

          {step < totalSteps ? (
            <button
              onClick={handleNext}
              disabled={!canProceed()}
              className={`flex items-center gap-2 px-6 py-2 rounded-lg font-semibold transition-colors ${
                canProceed()
                  ? 'bg-blue-600 hover:bg-blue-700'
                  : 'bg-gray-800 text-gray-600 cursor-not-allowed'
              }`}
            >
              Next
              <ChevronRight className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={handleComplete}
              className="flex items-center gap-2 px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition-colors"
            >
              <Check className="w-5 h-5" />
              Create Pack
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function Step1BasicInfo({ packData, setPackData }: {
  packData: PackData
  setPackData: (data: PackData) => void
}) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold mb-4">Basic Information</h3>
        <p className="text-gray-400 text-sm mb-6">
          Let's start with the basics about your asset pack
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Pack Name *</label>
        <input
          type="text"
          value={packData.name}
          onChange={(e) => setPackData({ ...packData, name: e.target.value })}
          placeholder="e.g., Medieval Weapons Collection"
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Description *</label>
        <textarea
          value={packData.description}
          onChange={(e) => setPackData({ ...packData, description: e.target.value })}
          placeholder="Describe what's included in this pack..."
          rows={4}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:border-blue-500 focus:outline-none resize-none"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Category</label>
          <select
            value={packData.category}
            onChange={(e) => setPackData({ ...packData, category: e.target.value })}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:border-blue-500 focus:outline-none"
          >
            <option value="fantasy">Fantasy</option>
            <option value="sci-fi">Sci-Fi</option>
            <option value="medieval">Medieval</option>
            <option value="modern">Modern</option>
            <option value="nature">Nature</option>
            <option value="architecture">Architecture</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Price (USD)</label>
          <input
            type="number"
            value={packData.price}
            onChange={(e) => setPackData({ ...packData, price: Number(e.target.value) })}
            min={0}
            step={1}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:border-blue-500 focus:outline-none"
          />
        </div>
      </div>
    </div>
  )
}

function Step2SelectAssets({ packData, setPackData }: {
  packData: PackData
  setPackData: (data: PackData) => void
}) {
  const [newAsset, setNewAsset] = useState('')

  const availableAssets = [
    { id: '1', name: 'Medieval Sword', type: 'weapon' },
    { id: '2', name: 'Fantasy Dragon', type: 'creature' },
    { id: '3', name: 'Treasure Chest', type: 'prop' },
    { id: '4', name: 'Battle Axe', type: 'weapon' },
    { id: '5', name: 'Sci-Fi Console', type: 'prop' }
  ]

  const toggleAsset = (assetId: string) => {
    if (packData.assets.includes(assetId)) {
      setPackData({
        ...packData,
        assets: packData.assets.filter(id => id !== assetId)
      })
    } else {
      setPackData({
        ...packData,
        assets: [...packData.assets, assetId]
      })
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold mb-4">Select Assets</h3>
        <p className="text-gray-400 text-sm mb-6">
          Choose which assets to include in this pack ({packData.assets.length} selected)
        </p>
      </div>

      <div className="bg-gray-800/50 rounded-lg p-4 max-h-96 overflow-y-auto space-y-2">
        {availableAssets.map((asset) => (
          <button
            key={asset.id}
            onClick={() => toggleAsset(asset.id)}
            className={`w-full flex items-center justify-between p-4 rounded-lg border-2 transition-all ${
              packData.assets.includes(asset.id)
                ? 'border-blue-500 bg-blue-500/10'
                : 'border-gray-700 hover:border-gray-600'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                packData.assets.includes(asset.id)
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-600'
              }`}>
                {packData.assets.includes(asset.id) && (
                  <Check className="w-3 h-3 text-white" />
                )}
              </div>
              <div className="text-left">
                <div className="font-medium">{asset.name}</div>
                <div className="text-sm text-gray-400">{asset.type}</div>
              </div>
            </div>
          </button>
        ))}
      </div>

      {packData.assets.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          Select at least one asset to continue
        </div>
      )}
    </div>
  )
}

function Step3ExportSettings({ packData, setPackData }: {
  packData: PackData
  setPackData: (data: PackData) => void
}) {
  const formats = ['GLB', 'FBX', 'OBJ', 'GLTF', 'USD']

  const toggleFormat = (format: string) => {
    const currentFormats = packData.settings.formats
    if (currentFormats.includes(format)) {
      setPackData({
        ...packData,
        settings: {
          ...packData.settings,
          formats: currentFormats.filter(f => f !== format)
        }
      })
    } else {
      setPackData({
        ...packData,
        settings: {
          ...packData.settings,
          formats: [...currentFormats, format]
        }
      })
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold mb-4">Export Settings</h3>
        <p className="text-gray-400 text-sm mb-6">
          Configure how assets will be exported in this pack
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium mb-3">Export Formats *</label>
        <div className="grid grid-cols-3 gap-3">
          {formats.map((format) => (
            <button
              key={format}
              onClick={() => toggleFormat(format)}
              className={`p-4 rounded-lg border-2 font-medium transition-all ${
                packData.settings.formats.includes(format)
                  ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              {format}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
          <div>
            <div className="font-medium mb-1">Include Animations</div>
            <div className="text-sm text-gray-400">Add rigged animations to compatible assets</div>
          </div>
          <button
            onClick={() => setPackData({
              ...packData,
              settings: {
                ...packData.settings,
                includeAnimations: !packData.settings.includeAnimations
              }
            })}
            className={`w-12 h-6 rounded-full transition-colors relative ${
              packData.settings.includeAnimations ? 'bg-blue-600' : 'bg-gray-700'
            }`}
          >
            <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform ${
              packData.settings.includeAnimations ? 'right-0.5' : 'left-0.5'
            }`} />
          </button>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
          <div>
            <div className="font-medium mb-1">Generate LODs</div>
            <div className="text-sm text-gray-400">Create multiple levels of detail</div>
          </div>
          <button
            onClick={() => setPackData({
              ...packData,
              settings: {
                ...packData.settings,
                includeLODs: !packData.settings.includeLODs
              }
            })}
            className={`w-12 h-6 rounded-full transition-colors relative ${
              packData.settings.includeLODs ? 'bg-blue-600' : 'bg-gray-700'
            }`}
          >
            <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform ${
              packData.settings.includeLODs ? 'right-0.5' : 'left-0.5'
            }`} />
          </button>
        </div>
      </div>
    </div>
  )
}

function Step4Review({ packData }: { packData: PackData }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold mb-4">Review & Confirm</h3>
        <p className="text-gray-400 text-sm mb-6">
          Review your pack configuration before creating
        </p>
      </div>

      <div className="space-y-4">
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Pack Name</div>
          <div className="text-lg font-semibold">{packData.name}</div>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Description</div>
          <div>{packData.description}</div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Category</div>
            <div className="font-semibold capitalize">{packData.category}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Price</div>
            <div className="font-semibold">${packData.price}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Assets</div>
            <div className="font-semibold">{packData.assets.length}</div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-2">Export Formats</div>
          <div className="flex flex-wrap gap-2">
            {packData.settings.formats.map((format) => (
              <span
                key={format}
                className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm font-medium"
              >
                {format}
              </span>
            ))}
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-2">Options</div>
          <div className="flex gap-4">
            {packData.settings.includeAnimations && (
              <span className="flex items-center gap-2 text-sm">
                <Check className="w-4 h-4 text-green-400" />
                Animations
              </span>
            )}
            {packData.settings.includeLODs && (
              <span className="flex items-center gap-2 text-sm">
                <Check className="w-4 h-4 text-green-400" />
                LODs
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
