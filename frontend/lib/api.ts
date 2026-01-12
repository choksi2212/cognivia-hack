/**
 * API Client for SITARA Backend
 */

import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000, // Increased to 30 seconds for OSM queries
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Types
export interface LocationInput {
  latitude: number
  longitude: number
  timestamp?: string
  speed?: number
  heading?: number
}

export interface ContextFeatures {
  hour?: number
  day_of_week?: number
  road_type?: string
  poi_density?: number
  police_station_distance?: number
  hospital_distance?: number
  intersection_count?: number
  dead_end_nearby?: number
  lighting_score?: number
  crowd_density?: number
}

export interface RiskAssessmentRequest {
  location: LocationInput
  context?: ContextFeatures
}

export interface AgentDecision {
  action: string
  state: string
  risk_score: number
  message: string
  priority: number
  suggested_routes?: any[]
  escalation_options?: string[]
}

export interface RiskAssessmentResponse {
  risk_score: number
  risk_level: string
  agent_decision: AgentDecision
  timestamp: string
  location: {
    latitude: number
    longitude: number
  }
}

export interface RoutePoint {
  latitude: number
  longitude: number
  risk_score?: number
}

export interface RouteRequest {
  start: LocationInput
  end: LocationInput
  waypoints?: RoutePoint[]
}

export interface RouteResponse {
  route_risk_score: number
  risk_level: string
  safe_segments: any[]
  risky_segments: any[]
  alternative_routes?: any[]
}

// API Functions

/**
 * Assess risk for a location
 */
export async function assessRisk(
  request: RiskAssessmentRequest
): Promise<RiskAssessmentResponse> {
  const response = await apiClient.post<RiskAssessmentResponse>(
    '/api/assess-risk',
    request
  )
  return response.data
}

/**
 * Analyze route safety
 */
export async function analyzeRoute(
  request: RouteRequest
): Promise<RouteResponse> {
  const response = await apiClient.post<RouteResponse>(
    '/api/analyze-route',
    request
  )
  return response.data
}

/**
 * Get agent state
 */
export async function getAgentState(): Promise<any> {
  const response = await apiClient.get('/api/agent/state')
  return response.data
}

/**
 * Reset agent
 */
export async function resetAgent(): Promise<any> {
  const response = await apiClient.post('/api/agent/reset')
  return response.data
}

/**
 * Get model info
 */
export async function getModelInfo(): Promise<any> {
  const response = await apiClient.get('/api/model/info')
  return response.data
}

/**
 * Health check
 */
export async function healthCheck(): Promise<any> {
  const response = await apiClient.get('/health')
  return response.data
}

export default apiClient
