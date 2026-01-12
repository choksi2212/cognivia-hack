'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { healthCheck } from '@/lib/api'
import Header from '@/components/Header'
import Hero from '@/components/Hero'
import RiskMonitor from '@/components/RiskMonitor'
import AgentStatus from '@/components/AgentStatus'
import Footer from '@/components/Footer'

// Dynamically import map component (client-side only)
const Map = dynamic(() => import('@/components/Map'), { 
  ssr: false,
  loading: () => (
    <div className="w-full h-[600px] bg-gray-100 animate-pulse flex items-center justify-center">
      <div className="text-gray-500">Loading map...</div>
    </div>
  )
})

export default function Home() {
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null)
  const [showMap, setShowMap] = useState(false)

  useEffect(() => {
    // Check backend health
    healthCheck()
      .then((data) => {
        setIsBackendOnline(data.status === 'healthy')
      })
      .catch(() => {
        setIsBackendOnline(false)
      })
  }, [])

  return (
    <div className="min-h-screen flex flex-col">
      <Header isBackendOnline={isBackendOnline} />
      
      <main className="flex-1">
        {/* Hero Section */}
        <Hero onExplore={() => setShowMap(true)} />
        
        {/* Map and Risk Monitor Section */}
        {showMap && (
          <section className="py-12 px-4 bg-gray-50">
            <div className="max-w-7xl mx-auto">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Map */}
                <div className="lg:col-span-2">
                  <div className="glass-card rounded-xl overflow-hidden">
                    <Map />
                  </div>
                </div>
                
                {/* Sidebar */}
                <div className="space-y-6">
                  <AgentStatus />
                  <RiskMonitor />
                </div>
              </div>
            </div>
          </section>
        )}
        
        {/* Features Section */}
        <section className="py-20 px-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-dark-900 mb-4">
                How SITARA Works
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                An agentic system that provides preventive risk awareness, not reactive panic responses
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <FeatureCard
                icon="🔍"
                title="Continuous Observation"
                description="Monitors environmental and temporal context in real-time"
              />
              <FeatureCard
                icon="🧠"
                title="Intelligent Reasoning"
                description="Uses ML and agentic AI to assess risk levels continuously"
              />
              <FeatureCard
                icon="🛡️"
                title="Proportional Intervention"
                description="Acts only when necessary, with user-controlled escalation"
              />
              <FeatureCard
                icon="🗺️"
                title="Route Intelligence"
                description="Suggests safer paths before risk escalates"
              />
            </div>
          </div>
        </section>
        
        {/* India-First Section */}
        <section className="py-20 px-4 bg-primary-50">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-4xl font-bold text-dark-900 mb-6">
                  Designed for India
                </h2>
                <p className="text-lg text-gray-700 mb-6">
                  SITARA is explicitly designed for Indian urban environments, not adapted from Western assumptions.
                </p>
                <ul className="space-y-4">
                  <ListItem text="Dense but poorly lit localities" />
                  <ListItem text="Narrow gullies and dead-end streets" />
                  <ListItem text="Informal settlements and construction zones" />
                  <ListItem text="Transit hubs with rapid crowd drop-offs" />
                  <ListItem text="Cultural preference for discreet assistance" />
                </ul>
              </div>
              <div className="glass-card rounded-xl p-8 bg-white">
                <h3 className="text-2xl font-bold text-dark-900 mb-4">Privacy First</h3>
                <div className="space-y-3">
                  <PrivacyItem text="No camera usage" />
                  <PrivacyItem text="No microphone usage" />
                  <PrivacyItem text="No face recognition" />
                  <PrivacyItem text="No offender profiling" />
                  <PrivacyItem text="User owns their data" />
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="glass-card rounded-xl p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-bold text-dark-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function ListItem({ text }: { text: string }) {
  return (
    <li className="flex items-start">
      <span className="text-primary-600 mr-3 mt-1">✓</span>
      <span className="text-gray-700">{text}</span>
    </li>
  )
}

function PrivacyItem({ text }: { text: string }) {
  return (
    <div className="flex items-center">
      <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
      <span className="text-gray-700">{text}</span>
    </div>
  )
}
