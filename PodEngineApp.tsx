/**
 * Pod Engine App
 * Entry point for the complete pod engine pipeline application
 */

import React from 'react'
import PodEngineGUI from './components/PodEngineGUI'

export default function PodEngineApp() {
  return (
    <div className="w-full h-screen">
      <PodEngineGUI />
    </div>
  )
}
