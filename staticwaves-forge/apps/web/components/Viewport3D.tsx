'use client'

import { Suspense, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Grid, Environment, useGLTF } from '@react-three/drei'
import * as THREE from 'three'

interface Viewport3DProps {
  modelPath?: string | null
}

function Model({ path }: { path: string }) {
  const { scene } = useGLTF(path)
  const modelRef = useRef<THREE.Group>(null)

  // Auto-rotate
  useFrame((state, delta) => {
    if (modelRef.current) {
      modelRef.current.rotation.y += delta * 0.3
    }
  })

  return <primitive ref={modelRef} object={scene} />
}

function PlaceholderCube() {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += delta * 0.5
      meshRef.current.rotation.y += delta * 0.7
    }
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial
        color="#3b82f6"
        metalness={0.3}
        roughness={0.4}
      />
    </mesh>
  )
}

export default function Viewport3D({ modelPath }: Viewport3DProps) {
  return (
    <div className="w-full h-full relative">
      {/* Controls Overlay */}
      <div className="absolute top-4 left-4 z-10 bg-black/50 backdrop-blur-sm rounded-lg p-3 text-xs space-y-1">
        <div className="text-gray-400">Controls:</div>
        <div>🖱️ Drag to rotate</div>
        <div>🔍 Scroll to zoom</div>
        <div>⌘ Right-click to pan</div>
      </div>

      {/* Stats Overlay */}
      <div className="absolute top-4 right-4 z-10 bg-black/50 backdrop-blur-sm rounded-lg p-3 text-xs space-y-1">
        <div className="text-gray-400">Viewport</div>
        <div>FPS: 60</div>
        <div>Draw Calls: 1</div>
      </div>

      <Canvas
        camera={{ position: [5, 5, 5], fov: 50 }}
        gl={{ antialias: true }}
      >
        <Suspense fallback={null}>
          {/* Lighting */}
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <pointLight position={[-10, -10, -5]} intensity={0.5} />

          {/* Environment */}
          <Environment preset="studio" />

          {/* Grid */}
          <Grid
            args={[20, 20]}
            cellSize={1}
            cellThickness={0.5}
            cellColor="#6b7280"
            sectionSize={5}
            sectionThickness={1}
            sectionColor="#3b82f6"
            fadeDistance={30}
            fadeStrength={1}
            infiniteGrid
          />

          {/* Model or Placeholder */}
          {modelPath ? (
            <Model path={modelPath} />
          ) : (
            <PlaceholderCube />
          )}

          {/* Controls */}
          <OrbitControls
            enableDamping
            dampingFactor={0.05}
            minDistance={2}
            maxDistance={20}
          />
        </Suspense>
      </Canvas>

      {/* Placeholder Message */}
      {!modelPath && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 text-center text-gray-400 text-sm">
          <div className="mb-2">No asset loaded</div>
          <div className="text-xs text-gray-500">Generate an asset to preview it here</div>
        </div>
      )}
    </div>
  )
}
