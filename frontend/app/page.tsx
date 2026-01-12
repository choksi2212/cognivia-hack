'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import dynamic from 'next/dynamic'
import { healthCheck } from '@/lib/api'
import Header from '@/components/Header'
import Hero from '@/components/Hero'
import RiskMonitor from '@/components/RiskMonitor'
import AgentStatus from '@/components/AgentStatus'
import RoutePlanner from '@/components/RoutePlanner'
import Footer from '@/components/Footer'

// Dynamically import map component (client-side only)
const Map = dynamic(() => import('@/components/Map'), { 
  ssr: false,
  loading: () => (
    <div className="w-full h-[600px] bg-gradient-to-br from-slate-100 to-slate-200 animate-pulse flex items-center justify-center rounded-xl">
      <div className="text-slate-500 text-lg font-medium">Loading interactive map...</div>
    </div>
  )
})

export default function Home() {
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null)
  const [showMap, setShowMap] = useState(false)

  useEffect(() => {
    // Check backend health
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (response.ok) {
          const data = await response.json()
          setIsBackendOnline(data.status === 'healthy')
        } else {
          setIsBackendOnline(false)
        }
      } catch (error) {
        console.error('Health check failed:', error)
        setIsBackendOnline(false)
      }
    }

    // Initial check
    checkHealth()

    // Check every 30 seconds
    const interval = setInterval(checkHealth, 30000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/30 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute top-1/3 -left-40 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.4, 0.6, 0.4],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1
          }}
        />
        <motion.div
          className="absolute bottom-20 right-1/4 w-72 h-72 bg-indigo-400/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2
          }}
        />
      </div>

      <div className="relative z-10">
        <Header isBackendOnline={isBackendOnline} />
        
        <main className="flex-1">
          {/* Hero Section */}
          <Hero onExplore={() => setShowMap(true)} />
        
          {/* Map and Risk Monitor Section */}
          {showMap && (
            <motion.section
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="py-12 px-4"
            >
              <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                  {/* Map */}
                  <motion.div 
                    className="lg:col-span-2"
                    initial={{ opacity: 0, x: -30 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2, duration: 0.5 }}
                  >
                    <div className="glass-card rounded-2xl overflow-hidden shadow-2xl">
                      <Map />
                    </div>
                  </motion.div>
                  
                  {/* Sidebar */}
                  <motion.div 
                    className="space-y-6"
                    initial={{ opacity: 0, x: 30 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4, duration: 0.5 }}
                  >
                    <AgentStatus />
                    <RiskMonitor />
                  </motion.div>
                </div>
                
                {/* Route Planner */}
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6, duration: 0.5 }}
                >
                  <RoutePlanner />
                </motion.div>
              </div>
            </motion.section>
          )}
        
          {/* Features Section */}
          <motion.section
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="py-20 px-4"
          >
            <div className="max-w-7xl mx-auto">
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
                className="text-center mb-16"
              >
                <h2 className="text-4xl md:text-5xl font-bold text-dark-900 mb-4">
                  How SITARA Works
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  An agentic system that provides preventive risk awareness, not reactive panic responses
                </p>
              </motion.div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                <FeatureCard
                  icon={<SearchIcon />}
                  title="Continuous Observation"
                  description="Monitors environmental and temporal context in real-time"
                  delay={0}
                />
                <FeatureCard
                  icon={<BrainIcon />}
                  title="Intelligent Reasoning"
                  description="Uses ML and agentic AI to assess risk levels continuously"
                  delay={0.1}
                />
                <FeatureCard
                  icon={<ShieldIcon />}
                  title="Proportional Intervention"
                  description="Acts only when necessary, with user-controlled escalation"
                  delay={0.2}
                />
                <FeatureCard
                  icon={<MapIcon />}
                  title="Route Intelligence"
                  description="Suggests safer paths before risk escalates"
                  delay={0.3}
                />
              </div>
            </div>
          </motion.section>
        
          {/* India-First Section */}
          <motion.section
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="py-20 px-4 bg-gradient-to-br from-blue-50/50 to-purple-50/50"
          >
            <div className="max-w-7xl mx-auto">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <motion.div
                  initial={{ opacity: 0, x: -30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.2, duration: 0.5 }}
                >
                  <h2 className="text-4xl md:text-5xl font-bold text-dark-900 mb-6">
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
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, x: 30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                  className="glass-card rounded-2xl p-8 bg-white/80 backdrop-blur-sm shadow-2xl"
                >
                  <h3 className="text-2xl font-bold text-dark-900 mb-6">Privacy First</h3>
                  <div className="space-y-3">
                    <PrivacyItem text="No camera usage" />
                    <PrivacyItem text="No microphone usage" />
                    <PrivacyItem text="No face recognition" />
                    <PrivacyItem text="No offender profiling" />
                    <PrivacyItem text="User owns their data" />
                  </div>
                </motion.div>
              </div>
            </div>
          </motion.section>
        </main>
        
        <Footer />
      </div>
    </div>
  )
}

function FeatureCard({ icon, title, description, delay }: { 
  icon: React.ReactNode; 
  title: string; 
  description: string;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ y: -8, scale: 1.02 }}
      className="group glass-card rounded-2xl p-6 hover:shadow-2xl transition-all duration-300 bg-white/80 backdrop-blur-sm"
    >
      <motion.div 
        className="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl mb-4 flex items-center justify-center text-white shadow-lg group-hover:shadow-xl transition-shadow"
        whileHover={{ rotate: 5, scale: 1.1 }}
        transition={{ duration: 0.2 }}
      >
        {icon}
      </motion.div>
      <h3 className="text-xl font-bold text-dark-900 mb-2">{title}</h3>
      <p className="text-gray-600 leading-relaxed">{description}</p>
    </motion.div>
  )
}

// Icon Components
function SearchIcon() {
  return (
    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  )
}

function BrainIcon() {
  return (
    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  )
}

function ShieldIcon() {
  return (
    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  )
}

function MapIcon() {
  return (
    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
    </svg>
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
