'use client'

import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface PromptPanelProps {
  onJobCreated: (jobId: string) => void
}

export default function PromptPanel({ onJobCreated }: PromptPanelProps) {
  const [prompt, setPrompt] = useState('')
  const [assetType, setAssetType] = useState('prop')
  const [style, setStyle] = useState('low-poly')
  const [targetEngine, setTargetEngine] = useState('unity')
  const [polyBudget, setPolyBudget] = useState(10000)
  const [includeRig, setIncludeRig] = useState(false)
  const [includeAnimations, setIncludeAnimations] = useState<string[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      alert('Please enter a prompt')
      return
    }

    setIsGenerating(true)

    try {
      const response = await axios.post(`${API_URL}/api/generate/`, {
        prompt,
        asset_type: assetType,
        style,
        target_engine: targetEngine,
        export_formats: ['glb', 'fbx'],
        poly_budget: polyBudget,
        include_rig: includeRig,
        include_animations: includeAnimations,
        generate_lods: true
      })

      onJobCreated(response.data.job_id)
    } catch (error) {
      console.error('Generation error:', error)
      alert('Failed to start generation. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const toggleAnimation = (anim: string) => {
    setIncludeAnimations(prev =>
      prev.includes(anim)
        ? prev.filter(a => a !== anim)
        : [...prev, anim]
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-lg font-semibold mb-4">Asset Configuration</h2>

        {/* Prompt */}
        <div className="space-y-2">
          <label className="text-sm text-gray-400">Describe your asset</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., A stylized fantasy sword with glowing runes..."
            className="w-full h-32 bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:border-blue-500 focus:outline-none resize-none"
          />
        </div>

        {/* Asset Type */}
        <div className="space-y-2 mt-4">
          <label className="text-sm text-gray-400">Asset Type</label>
          <select
            value={assetType}
            onChange={(e) => setAssetType(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="creature">Creature</option>
            <option value="character">Character</option>
            <option value="prop">Prop</option>
            <option value="weapon">Weapon</option>
            <option value="building">Building</option>
            <option value="environment">Environment</option>
            <option value="vehicle">Vehicle</option>
          </select>
        </div>

        {/* Style */}
        <div className="space-y-2 mt-4">
          <label className="text-sm text-gray-400">Style</label>
          <select
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="low-poly">Low Poly</option>
            <option value="realistic">Realistic</option>
            <option value="stylized">Stylized</option>
            <option value="voxel">Voxel</option>
            <option value="toon">Toon</option>
            <option value="roblox-safe">Roblox-Safe</option>
          </select>
        </div>

        {/* Target Engine */}
        <div className="space-y-2 mt-4">
          <label className="text-sm text-gray-400">Target Engine</label>
          <select
            value={targetEngine}
            onChange={(e) => setTargetEngine(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="unity">Unity</option>
            <option value="unreal">Unreal Engine</option>
            <option value="roblox">Roblox</option>
            <option value="godot">Godot</option>
            <option value="generic">Generic</option>
          </select>
        </div>

        {/* Poly Budget */}
        <div className="space-y-2 mt-4">
          <label className="text-sm text-gray-400">Poly Budget: {polyBudget.toLocaleString()}</label>
          <input
            type="range"
            min="1000"
            max="100000"
            step="1000"
            value={polyBudget}
            onChange={(e) => setPolyBudget(parseInt(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>1K</span>
            <span>50K</span>
            <span>100K</span>
          </div>
        </div>

        {/* Rigging */}
        <div className="mt-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={includeRig}
              onChange={(e) => setIncludeRig(e.target.checked)}
              className="w-4 h-4 rounded"
            />
            <span className="text-sm">Include Auto-Rig</span>
          </label>
        </div>

        {/* Animations */}
        {includeRig && (
          <div className="space-y-2 mt-4">
            <label className="text-sm text-gray-400">Animations</label>
            <div className="space-y-2">
              {['idle', 'walk', 'run', 'jump', 'attack'].map(anim => (
                <label key={anim} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeAnimations.includes(anim)}
                    onChange={() => toggleAnimation(anim)}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-sm capitalize">{anim}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="w-full mt-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-semibold transition-colors"
        >
          {isGenerating ? 'Generating...' : 'Generate Asset'}
        </button>
      </div>
    </div>
  )
}
