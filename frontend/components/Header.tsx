'use client'

import Link from 'next/link'

interface HeaderProps {
  isBackendOnline: boolean | null
}

export default function Header({ isBackendOnline }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 glass-card border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="text-3xl">✨</div>
            <div>
              <h1 className="text-2xl font-bold text-dark-900">SITARA</h1>
              <p className="text-xs text-gray-600">Situational Risk Intelligence</p>
            </div>
          </Link>
          
          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="/" className="text-gray-700 hover:text-primary-600 transition-colors">
              Home
            </Link>
            <Link href="/about" className="text-gray-700 hover:text-primary-600 transition-colors">
              About
            </Link>
            <Link href="/how-it-works" className="text-gray-700 hover:text-primary-600 transition-colors">
              How It Works
            </Link>
          </nav>
          
          {/* Status Indicator */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  isBackendOnline === null
                    ? 'bg-gray-400 animate-pulse'
                    : isBackendOnline
                    ? 'bg-green-500'
                    : 'bg-red-500'
                }`}
              ></div>
              <span className="text-sm text-gray-600">
                {isBackendOnline === null
                  ? 'Connecting...'
                  : isBackendOnline
                  ? 'System Online'
                  : 'System Offline'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
