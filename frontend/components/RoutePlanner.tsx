'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface RouteResult {
  route_risk_score: number
  risk_level: string
  safe_segments: Array<{
    index: number
    latitude: number
    longitude: number
    risk_score: number
    risk_level: string
  }>
  risky_segments: Array<{
    index: number
    latitude: number
    longitude: number
    risk_score: number
    risk_level: string
  }>
}

export default function RoutePlanner() {
  const [startLat, setStartLat] = useState('')
  const [startLng, setStartLng] = useState('')
  const [endLat, setEndLat] = useState('')
  const [endLng, setEndLng] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<RouteResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const popularLocations = [
    { name: 'Satellite, Ahmedabad', lat: 22.6823, lng: 72.8703 },
    { name: 'CG Road, Ahmedabad', lat: 23.0225, lng: 72.5714 },
    { name: 'Maninagar, Ahmedabad', lat: 22.9969, lng: 72.5993 },
    { name: 'Vastrapur, Ahmedabad', lat: 23.0352, lng: 72.5264 },
  ]

  const handleAnalyzeRoute = async () => {
    if (!startLat || !startLng || !endLat || !endLng) {
      setError('Please enter both start and end locations')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/api/analyze-route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start: {
            latitude: parseFloat(startLat),
            longitude: parseFloat(startLng)
          },
          end: {
            latitude: parseFloat(endLat),
            longitude: parseFloat(endLng)
          }
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err: any) {
      setError(err.message || 'Failed to analyze route')
    } finally {
      setLoading(false)
    }
  }

  const fillLocation = (type: 'start' | 'end', lat: number, lng: number) => {
    if (type === 'start') {
      setStartLat(lat.toString())
      setStartLng(lng.toString())
    } else {
      setEndLat(lat.toString())
      setEndLng(lng.toString())
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-50'
      case 'medium': return 'text-orange-600 bg-orange-50'
      case 'high': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getRiskBadgeColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-green-500'
      case 'medium': return 'bg-orange-500'
      case 'high': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-slate-200">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Route Planner</h2>
          <p className="text-sm text-slate-600">Find the safest path to your destination</p>
        </div>
      </div>

      {/* Input Form */}
      <div className="space-y-4 mb-6">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Starting Point
            </label>
            <div className="space-y-2">
              <input
                type="number"
                step="any"
                placeholder="Latitude (e.g., 22.6823)"
                value={startLat}
                onChange={(e) => setStartLat(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <input
                type="number"
                step="any"
                placeholder="Longitude (e.g., 72.8703)"
                value={startLng}
                onChange={(e) => setStartLng(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Destination
            </label>
            <div className="space-y-2">
              <input
                type="number"
                step="any"
                placeholder="Latitude (e.g., 23.0225)"
                value={endLat}
                onChange={(e) => setEndLat(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
              <input
                type="number"
                step="any"
                placeholder="Longitude (e.g., 72.5714)"
                value={endLng}
                onChange={(e) => setEndLng(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Quick Fill Buttons */}
        <div className="grid grid-cols-2 gap-2">
          {popularLocations.map((loc, idx) => (
            <div key={idx} className="flex gap-2">
              <button
                onClick={() => fillLocation('start', loc.lat, loc.lng)}
                className="flex-1 px-3 py-2 text-xs bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
              >
                From {loc.name.split(',')[0]}
              </button>
              <button
                onClick={() => fillLocation('end', loc.lat, loc.lng)}
                className="flex-1 px-3 py-2 text-xs bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors"
              >
                To {loc.name.split(',')[0]}
              </button>
            </div>
          ))}
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleAnalyzeRoute}
          disabled={loading}
          className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Analyzing Route...
            </span>
          ) : (
            'Analyze Route Safety'
          )}
        </motion.button>
      </div>

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg"
          >
            <p className="text-red-700 text-sm font-medium">{error}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="space-y-4"
          >
            {/* Overall Risk */}
            <div className={`p-6 rounded-xl border-2 ${getRiskColor(result.risk_level)}`}>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-bold">Overall Route Risk</h3>
                <span className={`px-4 py-1 rounded-full text-sm font-bold text-white ${getRiskBadgeColor(result.risk_level)}`}>
                  {result.risk_level.toUpperCase()}
                </span>
              </div>
              <div className="flex items-end gap-2">
                <span className="text-4xl font-bold">{(result.route_risk_score * 100).toFixed(1)}%</span>
                <span className="text-sm opacity-75 mb-2">risk score</span>
              </div>
              <div className="mt-4 bg-white/50 rounded-lg p-3">
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium">Risk Distribution:</span>
                  <span>{result.safe_segments.length + result.risky_segments.length} segments analyzed</span>
                </div>
                <div className="flex gap-2 h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-green-500"
                    style={{ width: `${(result.safe_segments.length / (result.safe_segments.length + result.risky_segments.length)) * 100}%` }}
                  />
                  <div 
                    className="bg-orange-500"
                    style={{ width: `${(result.risky_segments.length / (result.safe_segments.length + result.risky_segments.length)) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-xl border border-blue-200">
              <h3 className="font-bold text-slate-900 mb-2 flex items-center gap-2">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Recommendation
              </h3>
              <p className="text-sm text-slate-700">
                {result.risk_level === 'low' && '✓ This route is relatively safe. Proceed with normal caution.'}
                {result.risk_level === 'medium' && '⚠ This route has moderate risk. Consider alternative routes if available.'}
                {result.risk_level === 'high' && '⚠ High risk detected on this route. We strongly recommend choosing an alternative path or traveling during daylight hours.'}
              </p>
            </div>

            {/* Safe Segments */}
            {result.safe_segments.length > 0 && (
              <div className="bg-green-50 p-4 rounded-xl border border-green-200">
                <h3 className="font-bold text-green-900 mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  Safe Segments ({result.safe_segments.length})
                </h3>
                <div className="space-y-2">
                  {result.safe_segments.slice(0, 3).map((segment, idx) => (
                    <div key={idx} className="flex items-center justify-between text-sm bg-white/50 p-2 rounded-lg">
                      <span className="text-slate-700">
                        Segment {segment.index + 1}: {segment.latitude.toFixed(4)}, {segment.longitude.toFixed(4)}
                      </span>
                      <span className="text-green-600 font-medium">
                        Risk: {(segment.risk_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                  {result.safe_segments.length > 3 && (
                    <p className="text-xs text-green-700 italic">
                      +{result.safe_segments.length - 3} more safe segments
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Risky Segments */}
            {result.risky_segments.length > 0 && (
              <div className="bg-orange-50 p-4 rounded-xl border border-orange-200">
                <h3 className="font-bold text-orange-900 mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                  Risky Segments ({result.risky_segments.length})
                </h3>
                <div className="space-y-2">
                  {result.risky_segments.map((segment, idx) => (
                    <div key={idx} className="flex items-center justify-between text-sm bg-white/50 p-2 rounded-lg">
                      <span className="text-slate-700">
                        Segment {segment.index + 1}: {segment.latitude.toFixed(4)}, {segment.longitude.toFixed(4)}
                      </span>
                      <span className="text-orange-600 font-medium">
                        Risk: {(segment.risk_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
