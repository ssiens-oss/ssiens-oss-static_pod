'use client'

import Link from 'next/link'
import { useState } from 'react'

export default function Home() {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-6xl w-full space-y-12">
        {/* Hero Section */}
        <div className="text-center space-y-6">
          <h1 className="text-7xl font-bold bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            StaticWaves Forge
          </h1>
          <p className="text-2xl text-gray-400 max-w-3xl mx-auto">
            AI-Powered 3D Asset + Animation Engine
          </p>
          <p className="text-lg text-gray-500 max-w-2xl mx-auto">
            One prompt → full game-ready asset pipeline. Generate meshes, UVs, textures, rigs, and animations in seconds.
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex gap-4 justify-center">
          <Link
            href="/generate"
            className="px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-lg text-lg font-semibold transition-colors"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            Start Generating →
          </Link>
          <Link
            href="/packs"
            className="px-8 py-4 bg-gray-800 hover:bg-gray-700 rounded-lg text-lg font-semibold transition-colors"
          >
            Browse Asset Packs
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
          <FeatureCard
            icon="🎮"
            title="Game-Ready Assets"
            description="Optimized topology, clean UVs, and engine-native exports"
          />
          <FeatureCard
            icon="🦴"
            title="Auto-Rig + Animate"
            description="Zero-touch character rigging with procedural animations"
          />
          <FeatureCard
            icon="📦"
            title="One-Click Packs"
            description="Bundle assets into marketplace-ready packages instantly"
          />
          <FeatureCard
            icon="⚡"
            title="LOD Generation"
            description="Automatic level-of-detail optimization for performance"
          />
          <FeatureCard
            icon="🎨"
            title="Multiple Styles"
            description="Low-poly, realistic, stylized, voxel, and more"
          />
          <FeatureCard
            icon="🚀"
            title="Multi-Engine Export"
            description="Unity, Unreal, Roblox, Godot - all in one click"
          />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-8 mt-16 text-center">
          <Stat number="1000+" label="Assets Generated" />
          <Stat number="50+" label="Asset Packs" />
          <Stat number="<30s" label="Avg Generation Time" />
        </div>
      </div>
    </main>
  )
}

function FeatureCard({ icon, title, description }: { icon: string, title: string, description: string }) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6 hover:border-blue-500/50 transition-colors">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  )
}

function Stat({ number, label }: { number: string, label: string }) {
  return (
    <div>
      <div className="text-4xl font-bold text-blue-500">{number}</div>
      <div className="text-gray-400 mt-1">{label}</div>
    </div>
  )
}
