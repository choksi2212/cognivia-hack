'use client'

import { useState, useEffect } from 'react'
import { assessRisk, type RiskAssessmentResponse } from '@/lib/api'

export default function RiskMonitor() {
  const [assessment, setAssessment] = useState<RiskAssessmentResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const performAssessment = async () => {
    setLoading(true)
    
    try {
      // Get current location
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            const result = await assessRisk({
              location: {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
              },
            })
            
            setAssessment(result)
            setLoading(false)
          },
          (error) => {
            console.error('Location error:', error)
            // Use default location (Delhi)
            assessRisk({
              location: {
                latitude: 28.6139,
                longitude: 77.2090,
              },
            }).then((result) => {
              setAssessment(result)
              setLoading(false)
            })
          }
        )
      }
    } catch (error) {
      console.error('Assessment error:', error)
      setLoading(false)
    }
  }

  useEffect(() => {
    performAssessment()
  }, [])

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'high':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'low':
        return '✓'
      case 'medium':
        return '⚠'
      case 'high':
        return '⚠️'
      default:
        return '•'
    }
  }

  return (
    <div className="glass-card rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-dark-900">Risk Assessment</h3>
        <button
          onClick={performAssessment}
          disabled={loading}
          className="text-sm text-primary-600 hover:text-primary-700 disabled:opacity-50"
        >
          {loading ? 'Assessing...' : 'Refresh'}
        </button>
      </div>
      
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="spinner w-8 h-8"></div>
        </div>
      ) : assessment ? (
        <div className="space-y-4">
          {/* Risk Level Badge */}
          <div className={`inline-flex items-center px-4 py-2 rounded-lg border-2 font-semibold ${getRiskColor(assessment.risk_level)}`}>
            <span className="mr-2">{getRiskIcon(assessment.risk_level)}</span>
            <span className="uppercase">{assessment.risk_level} Risk</span>
          </div>
          
          {/* Risk Score */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Risk Score</span>
              <span className="text-sm font-semibold text-dark-900">
                {(assessment.risk_score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  assessment.risk_level === 'low'
                    ? 'bg-green-500'
                    : assessment.risk_level === 'medium'
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${assessment.risk_score * 100}%` }}
              ></div>
            </div>
          </div>
          
          {/* Agent Message */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <p className="text-sm text-gray-700">
              {assessment.agent_decision.message}
            </p>
          </div>
          
          {/* Escalation Options (if any) */}
          {assessment.agent_decision.escalation_options && 
           assessment.agent_decision.escalation_options.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-semibold text-dark-900">Recommended Actions:</p>
              <div className="space-y-2">
                {assessment.agent_decision.escalation_options.map((option, index) => (
                  <button
                    key={index}
                    className="w-full text-left px-4 py-2 bg-white border border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-sm"
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {/* Timestamp */}
          <div className="text-xs text-gray-500 text-center">
            Last updated: {new Date(assessment.timestamp).toLocaleTimeString()}
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          No assessment data available
        </div>
      )}
    </div>
  )
}
