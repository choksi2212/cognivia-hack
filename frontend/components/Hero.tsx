'use client'

import { motion } from 'framer-motion'

interface HeroProps {
  onExplore: () => void
}

export default function Hero({ onExplore }: HeroProps) {
  return (
    <section className="relative py-20 px-4 overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-secondary-50 opacity-50"></div>
      
      <div className="relative max-w-7xl mx-auto">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold text-dark-900 mb-6">
              Safety Through
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-secondary-600">
                Situational Intelligence
              </span>
            </h1>
          </motion.div>
          
          <motion.p
            className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            SITARA is not a panic-response app. It's an agentic situational intelligence system 
            designed to help women make safer decisions before risk escalates.
          </motion.p>
          
          <motion.div
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <button
              onClick={onExplore}
              className="btn-primary text-lg px-8 py-4"
            >
              Explore Live Demo
            </button>
            <button className="btn-secondary text-lg px-8 py-4">
              Learn More
            </button>
          </motion.div>
          
          <motion.div
            className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <StatCard number=">98%" label="ML Model Accuracy" />
            <StatCard number="Real-time" label="Risk Assessment" />
            <StatCard number="India-First" label="Design Philosophy" />
          </motion.div>
        </div>
      </div>
    </section>
  )
}

function StatCard({ number, label }: { number: string; label: string }) {
  return (
    <div className="glass-card rounded-xl p-6">
      <div className="text-3xl font-bold text-primary-600 mb-2">{number}</div>
      <div className="text-gray-600">{label}</div>
    </div>
  )
}
