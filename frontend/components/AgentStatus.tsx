'use client'

import { useState, useEffect } from 'react'
import { getAgentState } from '@/lib/api'

interface AgentState {
  current_state: string
  risk_score: number
  risk_velocity: number
  alert_count: number
  location_history_count: number
}

export default function AgentStatus() {
  const [state, setState] = useState<AgentState | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchState = async () => {
      try {
        const data = await getAgentState()
        setState(data)
      } catch (error) {
        console.error('Error fetching agent state:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchState()
    
    // Refresh every 10 seconds
    const interval = setInterval(fetchState, 10000)
    
    return () => clearInterval(interval)
  }, [])

  const getStateColor = (stateName: string) => {
    switch (stateName) {
      case 'safe':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'caution':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'elevated_risk':
        return 'text-orange-600 bg-orange-50 border-orange-200'
      case 'high_risk':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getStateIcon = (stateName: string) => {
    switch (stateName) {
      case 'safe':
        return '🛡️'
      case 'caution':
        return '👀'
      case 'elevated_risk':
        return '⚠️'
      case 'high_risk':
        return '🚨'
      default:
        return '•'
    }
  }

  const getStateLabel = (stateName: string) => {
    return stateName
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  if (loading) {
    return (
      <div className="glass-card rounded-xl p-6">
        <div className="animate-shimmer h-32 rounded-lg"></div>
      </div>
    )
  }

  if (!state) {
    return (
      <div className="glass-card rounded-xl p-6">
        <p className="text-gray-500 text-center">Agent state unavailable</p>
      </div>
    )
  }

  return (
    <div className="glass-card rounded-xl p-6">
      <h3 className="text-lg font-bold text-dark-900 mb-4">Agent Status</h3>
      
      <div className="space-y-4">
        {/* Current State */}
        <div className={`rounded-lg border-2 p-4 ${getStateColor(state.current_state)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-2xl mr-3">{getStateIcon(state.current_state)}</span>
              <div>
                <p className="text-xs font-medium opacity-75">Current State</p>
                <p className="text-lg font-bold">{getStateLabel(state.current_state)}</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Metrics */}
        <div className="grid grid-cols-2 gap-3">
          <MetricCard
            label="Risk Score"
            value={`${(state.risk_score * 100).toFixed(0)}%`}
          />
          <MetricCard
            label="Velocity"
            value={state.risk_velocity.toFixed(3)}
          />
          <MetricCard
            label="Alerts"
            value={state.alert_count.toString()}
          />
          <MetricCard
            label="Locations"
            value={state.location_history_count.toString()}
          />
        </div>
        
        {/* Status Indicator */}
        <div className="flex items-center justify-center pt-2">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-gray-600">Agent Active</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
      <p className="text-xs text-gray-600 mb-1">{label}</p>
      <p className="text-lg font-bold text-dark-900">{value}</p>
    </div>
  )
}
