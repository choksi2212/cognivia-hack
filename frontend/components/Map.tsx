'use client'

import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import { assessRisk } from '@/lib/api'

// Fix for default marker icons
import 'leaflet/dist/leaflet.css'

const icon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

export default function Map() {
  const [position, setPosition] = useState<[number, number]>([28.6139, 77.2090]) // Delhi
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null)

  useEffect(() => {
    // Get user location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const coords: [number, number] = [pos.coords.latitude, pos.coords.longitude]
          setUserLocation(coords)
          setPosition(coords)
        },
        (error) => {
          console.log('Location access denied or error:', error)
          // Default to Delhi if location access denied
        }
      )
    }
  }, [])

  const handleMapClick = async (lat: number, lng: number) => {
    try {
      const result = await assessRisk({
        location: {
          latitude: lat,
          longitude: lng,
        },
      })
      
      console.log('Risk assessment:', result)
      // Update marker position
      setPosition([lat, lng])
    } catch (error) {
      console.error('Risk assessment failed:', error)
    }
  }

  return (
    <div className="w-full h-[600px] relative">
      <MapContainer
        center={position}
        zoom={13}
        className="w-full h-full rounded-xl"
        style={{ zIndex: 0 }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapClickHandler onClick={handleMapClick} />
        
        {userLocation && (
          <Marker position={userLocation} icon={icon}>
            <Popup>
              <div className="text-center">
                <strong>Your Location</strong>
                <br />
                Click on map to assess risk
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
      
      <div className="absolute top-4 left-4 z-[1000] glass-card rounded-lg p-3 max-w-xs">
        <p className="text-sm text-gray-700">
          <strong>Interactive Map:</strong> Click anywhere to assess risk for that location.
        </p>
      </div>
    </div>
  )
}

function MapClickHandler({ onClick }: { onClick: (lat: number, lng: number) => void }) {
  const map = useMap()
  
  useEffect(() => {
    const handleClick = (e: L.LeafletMouseEvent) => {
      onClick(e.latlng.lat, e.latlng.lng)
    }
    
    map.on('click', handleClick)
    
    return () => {
      map.off('click', handleClick)
    }
  }, [map, onClick])
  
  return null
}
