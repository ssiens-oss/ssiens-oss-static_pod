'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Navigation() {
  const pathname = usePathname()

  const isActive = (path: string) => {
    return pathname === path ? 'bg-blue-600' : 'hover:bg-gray-800'
  }

  return (
    <nav className="border-b border-gray-800 bg-gray-900/95 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">S</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
              StaticWaves Forge
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            <Link
              href="/generate"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive('/generate')}`}
            >
              Generate
            </Link>
            <Link
              href="/library"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive('/library')}`}
            >
              Library
            </Link>
            <Link
              href="/packs"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive('/packs')}`}
            >
              Packs
            </Link>
            <Link
              href="/dashboard"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive('/dashboard')}`}
            >
              Dashboard
            </Link>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-3">
            <Link
              href="/settings"
              className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
              title="Settings"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </Link>

            <div className="h-8 w-px bg-gray-700" />

            <Link
              href="/generate"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-semibold transition-colors"
            >
              New Asset
            </Link>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden border-t border-gray-800">
        <div className="grid grid-cols-4 gap-1 p-2">
          <Link
            href="/generate"
            className={`px-3 py-2 rounded-lg text-xs font-medium text-center transition-colors ${isActive('/generate')}`}
          >
            Generate
          </Link>
          <Link
            href="/library"
            className={`px-3 py-2 rounded-lg text-xs font-medium text-center transition-colors ${isActive('/library')}`}
          >
            Library
          </Link>
          <Link
            href="/packs"
            className={`px-3 py-2 rounded-lg text-xs font-medium text-center transition-colors ${isActive('/packs')}`}
          >
            Packs
          </Link>
          <Link
            href="/dashboard"
            className={`px-3 py-2 rounded-lg text-xs font-medium text-center transition-colors ${isActive('/dashboard')}`}
          >
            Dashboard
          </Link>
        </div>
      </div>
    </nav>
  )
}
