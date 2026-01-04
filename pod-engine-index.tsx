import React from 'react'
import { createRoot } from 'react-dom/client'
import PodEngineApp from './PodEngineApp'
import './index.css'

const root = createRoot(document.getElementById('root')!)
root.render(
  <React.StrictMode>
    <PodEngineApp />
  </React.StrictMode>
)
