'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'

export default function Home() {
  const [currentExample, setCurrentExample] = useState(0)

  const examples = [
    { prompt: "A low-poly medieval sword", type: "Weapon", time: "18s" },
    { prompt: "Stylized fantasy dragon", type: "Creature", time: "42s" },
    { prompt: "Cyberpunk vending machine", type: "Prop", time: "24s" }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentExample((prev) => (prev + 1) % examples.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-900 via-black to-gray-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500 rounded-full filter blur-3xl animate-pulse" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500 rounded-full filter blur-3xl animate-pulse delay-1000" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32">
          <div className="text-center space-y-8">
            <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent animate-gradient">
              StaticWaves Forge
            </h1>
            <p className="text-2xl md:text-3xl text-gray-300 max-w-3xl mx-auto">
              AI-Powered 3D Asset Generation
            </p>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              One prompt → production-ready game assets. Generate meshes, UVs, textures, rigs, and animations in seconds.
            </p>

            {/* Example Carousel */}
            <div className="max-w-md mx-auto bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              <div className="text-sm text-gray-500 mb-2">Example:</div>
              <div className="text-lg font-medium mb-1">"{examples[currentExample].prompt}"</div>
              <div className="flex items-center justify-between text-sm text-gray-400">
                <span>{examples[currentExample].type}</span>
                <span className="text-green-400">{examples[currentExample].time}</span>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Link
                href="/generate"
                className="group px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg text-lg font-semibold transition-all transform hover:scale-105"
              >
                <span className="flex items-center justify-center gap-2">
                  Start Generating
                  <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </Link>
              <Link
                href="/dashboard"
                className="px-8 py-4 bg-gray-800 hover:bg-gray-700 rounded-lg text-lg font-semibold transition-colors border border-gray-700"
              >
                View Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Everything You Need</h2>
          <p className="text-xl text-gray-400">Complete 3D asset pipeline in one platform</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
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
      </div>

      {/* Stats Section */}
      <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border-y border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <Stat number="1000+" label="Assets Generated" />
            <Stat number="50+" label="Asset Packs" />
            <Stat number="<30s" label="Avg Generation Time" />
            <Stat number="5+" label="Export Formats" />
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-2xl p-12 text-center">
          <h2 className="text-4xl font-bold mb-4">Ready to Start Creating?</h2>
          <p className="text-xl text-gray-400 mb-8">
            Join thousands of game developers using StaticWaves Forge
          </p>
          <Link
            href="/generate"
            className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-lg text-lg font-semibold transition-all transform hover:scale-105"
          >
            Generate Your First Asset
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>
      </div>
    </main>
  )
}

function FeatureCard({ icon, title, description }: { icon: string, title: string, description: string }) {
  return (
    <div className="group bg-gray-900/50 border border-gray-800 rounded-xl p-6 hover:border-blue-500/50 hover:bg-gray-900/70 transition-all">
      <div className="text-5xl mb-4 group-hover:scale-110 transition-transform">{icon}</div>
      <h3 className="text-xl font-semibold mb-2 group-hover:text-blue-400 transition-colors">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  )
}

function Stat({ number, label }: { number: string, label: string }) {
  return (
    <div className="group">
      <div className="text-5xl font-bold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent group-hover:scale-110 transition-transform">
        {number}
      </div>
      <div className="text-gray-400 mt-2">{label}</div>
    </div>
  )
}
