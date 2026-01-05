/**
 * StaticWaves POD Engine - Main Application
 */

import React, { useState, useEffect } from 'react'
import Login from './Login'
import Register from './Register'
import Dashboard from './Dashboard'

type View = 'login' | 'register' | 'dashboard'

export default function App() {
  const [currentView, setCurrentView] = useState<View>('login')
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('token')
    if (token) {
      setIsAuthenticated(true)
      setCurrentView('dashboard')
    }
  }, [])

  const handleLogin = (token: string) => {
    setIsAuthenticated(true)
    setCurrentView('dashboard')
  }

  const handleRegister = () => {
    // Registration successful, will redirect to login
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
    setCurrentView('login')
  }

  if (currentView === 'login') {
    return (
      <Login
        onLogin={handleLogin}
        onSwitchToRegister={() => setCurrentView('register')}
      />
    )
  }

  if (currentView === 'register') {
    return (
      <Register
        onRegister={handleRegister}
        onSwitchToLogin={() => setCurrentView('login')}
      />
    )
  }

  if (currentView === 'dashboard' && isAuthenticated) {
    return <Dashboard />
  }

  // Fallback
  return (
    <Login
      onLogin={handleLogin}
      onSwitchToRegister={() => setCurrentView('register')}
    />
  )
}
