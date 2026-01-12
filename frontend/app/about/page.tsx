'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-slate-100">
      <Header isBackendOnline={null} />
      
      <main className="pt-24 pb-20 px-4">
        <div className="max-w-6xl mx-auto">
          {/* Hero */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6">
              About SITARA
            </h1>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Situational Risk Intelligence Platform for Women's Safety in India
            </p>
          </motion.div>

          {/* Problem Statement */}
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="mb-16"
          >
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-slate-200 shadow-xl">
              <h2 className="text-3xl font-bold text-slate-900 mb-6">The Problem</h2>
              <p className="text-lg text-slate-700 mb-4">
                Women's safety solutions today are largely reactive, fragmented, and poorly contextualized for Indian environments.
              </p>
              <div className="grid md:grid-cols-2 gap-6 mt-8">
                <div>
                  <h3 className="font-semibold text-slate-900 mb-3">Existing Systems</h3>
                  <ul className="space-y-2 text-slate-600">
                    <li className="flex items-start">
                      <span className="text-red-500 mr-2">✗</span>
                      <span>Depend on manual panic actions</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-red-500 mr-2">✗</span>
                      <span>Trigger loud alerts that escalate danger</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-red-500 mr-2">✗</span>
                      <span>Treat safety as binary: safe vs unsafe</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-red-500 mr-2">✗</span>
                      <span>Ignore environmental risk accumulation</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-3">SITARA Approach</h3>
                  <ul className="space-y-2 text-slate-600">
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span>Continuous situational observation</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span>Silent, proportional interventions</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span>Gradual risk awareness</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span>Preventive decision support</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </motion.section>

          {/* Core Insight */}
          <motion.section
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="mb-16"
          >
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl p-8 md:p-12 text-white shadow-2xl">
              <h2 className="text-3xl font-bold mb-4">Core Insight</h2>
              <p className="text-xl mb-4">
                Women don't need another panic button. They need situational awareness and early decision support.
              </p>
              <p className="text-lg opacity-90">
                Risk rarely appears suddenly. It builds gradually. Yet no widely adopted system continuously reasons about situational risk as it evolves.
              </p>
            </div>
          </motion.section>

          {/* India-First Design */}
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="mb-16"
          >
            <h2 className="text-3xl font-bold text-slate-900 mb-8 text-center">India-First Design</h2>
            
            <div className="grid md:grid-cols-3 gap-6">
              {[
                {
                  title: 'Urban Context',
                  items: ['Dense but poorly lit localities', 'Narrow gullies and dead ends', 'Mixed land-use zones']
                },
                {
                  title: 'Infrastructure',
                  items: ['Informal settlements', 'Rapid transit hubs', 'Construction zones']
                },
                {
                  title: 'Cultural Fit',
                  items: ['Discreet assistance', 'Privacy-preserving', 'User dignity maintained']
                }
              ].map((section, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 + index * 0.1, duration: 0.5 }}
                  className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 shadow-lg"
                >
                  <h3 className="text-xl font-bold text-slate-900 mb-4">{section.title}</h3>
                  <ul className="space-y-2 text-slate-600">
                    {section.items.map((item, i) => (
                      <li key={i} className="flex items-start">
                        <span className="text-blue-500 mr-2">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Technology Stack */}
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.8 }}
            className="mb-16"
          >
            <h2 className="text-3xl font-bold text-slate-900 mb-8 text-center">Technology Stack</h2>
            
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-slate-200 shadow-xl">
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-4">Frontend</h3>
                  <ul className="space-y-2 text-slate-600">
                    <li>Next.js 14 (React Framework)</li>
                    <li>TypeScript for type safety</li>
                    <li>Tailwind CSS + Framer Motion</li>
                    <li>Leaflet for interactive maps</li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-4">Backend</h3>
                  <ul className="space-y-2 text-slate-600">
                    <li>FastAPI (Python)</li>
                    <li>PostgreSQL + Prisma ORM</li>
                    <li>OpenStreetMap (osmnx)</li>
                    <li>scikit-learn ML models</li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-4">Machine Learning</h3>
                  <ul className="space-y-2 text-slate-600">
                    <li>Random Forest Classifier</li>
                    <li>94-96% accuracy target</li>
                    <li>26 engineered features</li>
                    <li>Real-time inference</li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-4">Data Sources</h3>
                  <ul className="space-y-2 text-slate-600">
                    <li>78 Indian crime datasets</li>
                    <li>Real-time OSM queries</li>
                    <li>District-level statistics</li>
                    <li>Temporal context features</li>
                  </ul>
                </div>
              </div>
            </div>
          </motion.section>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2, duration: 0.6 }}
            className="text-center"
          >
            <Link href="/" className="inline-block px-8 py-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl mr-4">
              Try Live Demo
            </Link>
            <Link href="/how-it-works" className="inline-block px-8 py-4 bg-slate-200 text-slate-900 font-semibold rounded-xl hover:bg-slate-300 transition-colors">
              How It Works
            </Link>
          </motion.div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
