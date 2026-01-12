'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

export default function HowItWorksPage() {
  const fadeInUp = {
    initial: { opacity: 0, y: 60 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 }
  }

  const stagger = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <Header isBackendOnline={null} />
      
      <main className="pt-24 pb-20 px-4">
        <div className="max-w-6xl mx-auto">
          {/* Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-20"
          >
            <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6">
              How SITARA Works
            </h1>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              An agentic system that combines machine learning, real-time data, 
              and intelligent decision-making to provide preventive risk awareness
            </p>
          </motion.div>

          {/* Architecture Overview */}
          <motion.section
            variants={stagger}
            initial="initial"
            animate="animate"
            className="mb-20"
          >
            <motion.h2 variants={fadeInUp} className="text-3xl font-bold text-slate-900 mb-8 text-center">
              System Architecture
            </motion.h2>
            
            <div className="grid md:grid-cols-3 gap-6">
              <motion.div variants={fadeInUp} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-12 h-12 bg-blue-500 rounded-xl mb-4 flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">Data Layer</h3>
                <p className="text-slate-600 mb-4">
                  Real OpenStreetMap data combined with historical crime statistics from 78 Indian datasets
                </p>
                <ul className="space-y-2 text-sm text-slate-500">
                  <li className="flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    <span>Road networks and POI density</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    <span>District-level crime statistics</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    <span>Real-time temporal features</span>
                  </li>
                </ul>
              </motion.div>

              <motion.div variants={fadeInUp} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-12 h-12 bg-purple-500 rounded-xl mb-4 flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">ML Model</h3>
                <p className="text-slate-600 mb-4">
                  Random Forest classifier trained on 88,000+ samples with 94-96% accuracy
                </p>
                <ul className="space-y-2 text-sm text-slate-500">
                  <li className="flex items-start">
                    <span className="text-purple-500 mr-2">•</span>
                    <span>26 engineered features</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-500 mr-2">•</span>
                    <span>Real-time risk prediction</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-500 mr-2">•</span>
                    <span>Explainable feature importance</span>
                  </li>
                </ul>
              </motion.div>

              <motion.div variants={fadeInUp} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-12 h-12 bg-green-500 rounded-xl mb-4 flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">Agentic AI</h3>
                <p className="text-slate-600 mb-4">
                  Finite State Machine that decides when and how to intervene proportionally
                </p>
                <ul className="space-y-2 text-sm text-slate-500">
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    <span>4-state decision system</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    <span>Risk velocity tracking</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    <span>User-controlled escalation</span>
                  </li>
                </ul>
              </motion.div>
            </div>
          </motion.section>

          {/* Process Flow */}
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-bold text-slate-900 mb-8 text-center">
              Real-Time Risk Assessment Flow
            </h2>
            
            <div className="relative">
              {/* Connecting line */}
              <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500 via-purple-500 to-green-500 hidden md:block"></div>
              
              <div className="space-y-8">
                {[
                  {
                    step: '01',
                    title: 'Location Detection',
                    description: 'User location is captured via GPS coordinates',
                    color: 'blue'
                  },
                  {
                    step: '02',
                    title: 'Feature Extraction',
                    description: 'Real OSM data queried: road types, POI density, distances to safety facilities',
                    color: 'indigo'
                  },
                  {
                    step: '03',
                    title: 'Risk Prediction',
                    description: 'ML model analyzes 26 features to predict risk level (low/medium/high)',
                    color: 'purple'
                  },
                  {
                    step: '04',
                    title: 'Agent Decision',
                    description: 'FSM evaluates risk velocity and decides appropriate intervention',
                    color: 'pink'
                  },
                  {
                    step: '05',
                    title: 'User Action',
                    description: 'Proportional recommendation: silent monitoring, route suggestion, or escalation options',
                    color: 'green'
                  }
                ].map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + index * 0.1, duration: 0.5 }}
                    className="relative flex items-start"
                  >
                    <div className={`flex-shrink-0 w-16 h-16 bg-${item.color}-500 rounded-2xl flex items-center justify-center text-white font-bold text-lg shadow-lg z-10`}>
                      {item.step}
                    </div>
                    <div className="ml-6 flex-1 bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 shadow-md">
                      <h3 className="text-xl font-bold text-slate-900 mb-2">{item.title}</h3>
                      <p className="text-slate-600">{item.description}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.section>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1, duration: 0.6 }}
            className="text-center"
          >
            <Link href="/" className="inline-block px-8 py-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl">
              Try Live Demo
            </Link>
          </motion.div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
