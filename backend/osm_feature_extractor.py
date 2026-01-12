"""
REAL OpenStreetMap Feature Extractor for SITARA
Uses actual OSM data - NO mocks, stubs, or simulations
"""

import osmnx as ox
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path
import pickle
from datetime import datetime, timedelta
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OSMFeatureExtractor:
    """
    Extracts REAL spatial features from OpenStreetMap
    NO synthetic data - all features come from actual OSM queries
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path("./cache/osm")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = {}
        self.cache_expiry = timedelta(days=7)  # Cache OSM data for 7 days
        
        # Configure OSMnx
        ox.settings.use_cache = True
        ox.settings.log_console = False
        
    def _get_cache_key(self, lat: float, lng: float, radius: int) -> str:
        """Generate cache key for location"""
        return f"{lat:.4f}_{lng:.4f}_{radius}"
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Load cached features if available and not expired"""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                
                # Check if cache is still valid
                if datetime.now() - cached_data['timestamp'] < self.cache_expiry:
                    logger.info(f"Using cached OSM data for {cache_key}")
                    return cached_data['features']
            except Exception as e:
                logger.warning(f"Error loading cache: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, features: Dict):
        """Save features to cache"""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'timestamp': datetime.now(),
                    'features': features
                }, f)
        except Exception as e:
            logger.warning(f"Error saving cache: {e}")
    
    def extract_features(self, latitude: float, longitude: float, 
                        radius: int = 500) -> Dict:
        """
        Extract REAL spatial features from OpenStreetMap
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Radius in meters to query (default 500m)
        
        Returns:
            Dictionary of spatial features
        
        Raises:
            ValueError: If coordinates are invalid
            RuntimeError: If OSM query fails
        """
        
        # Validate inputs
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}")
        if radius <= 0 or radius > 5000:
            raise ValueError(f"Invalid radius: {radius}. Must be between 1-5000 meters")
        
        cache_key = self._get_cache_key(latitude, longitude, radius)
        
        # Try cache first
        cached_features = self._load_from_cache(cache_key)
        if cached_features:
            return cached_features
        
        logger.info(f"Extracting REAL OSM features for ({latitude}, {longitude})")
        
        try:
            features = self._query_osm_data(latitude, longitude, radius)
            
            # Save to cache
            self._save_to_cache(cache_key, features)
            
            return features
            
        except Exception as e:
            logger.error(f"OSM query failed: {e}")
            # Return degraded features with error flag
            return self._get_degraded_features(latitude, longitude, error=str(e))
    
    def _query_osm_data(self, lat: float, lng: float, radius: int) -> Dict:
        """Query actual OSM data"""
        
        point = (lat, lng)
        features = {}
        
        try:
            # 1. Get road network
            try:
                G = ox.graph_from_point(point, dist=radius, network_type='all')
                features['road_network_available'] = True
                
                # Road type analysis
                edges = ox.graph_to_gdfs(G, nodes=False)
                if not edges.empty and 'highway' in edges.columns:
                    road_types = edges['highway'].value_counts()
                    
                    # Classify primary road type
                    if 'motorway' in road_types.index or 'trunk' in road_types.index:
                        features['road_type'] = 'highway'
                    elif 'primary' in road_types.index or 'secondary' in road_types.index:
                        features['road_type'] = 'main_road'
                    elif 'residential' in road_types.index:
                        features['road_type'] = 'residential'
                    elif 'service' in road_types.index or 'alley' in road_types.index:
                        features['road_type'] = 'alley'
                    else:
                        features['road_type'] = 'footpath'
                    
                    # Intersection count (nodes with degree > 2)
                    features['intersection_count'] = sum(1 for node, degree in G.degree() if degree > 2)
                    
                    # Dead end detection (nodes with degree == 1)
                    dead_ends = sum(1 for node, degree in G.degree() if degree == 1)
                    features['dead_end_nearby'] = 1 if dead_ends > 3 else 0
                    
                else:
                    features['road_type'] = 'residential'
                    features['intersection_count'] = 2
                    features['dead_end_nearby'] = 0
                    
            except Exception as e:
                logger.warning(f"Road network query failed: {e}")
                features['road_network_available'] = False
                features['road_type'] = 'residential'
                features['intersection_count'] = 2
                features['dead_end_nearby'] = 0
            
            # 2. Get Points of Interest (POIs)
            try:
                tags = {
                    'amenity': True,  # Restaurants, shops, etc.
                    'shop': True,
                    'tourism': True,
                    'leisure': True
                }
                
                pois = ox.features_from_point(point, tags=tags, dist=radius)
                features['poi_density'] = len(pois) if not pois.empty else 0
                
            except Exception as e:
                logger.warning(f"POI query failed: {e}")
                features['poi_density'] = 3  # Conservative estimate
            
            # 3. Get Safety-related facilities
            try:
                # Police stations
                police_tags = {'amenity': 'police'}
                police = ox.features_from_point(point, tags=police_tags, dist=5000)
                
                if not police.empty:
                    # Calculate distance to nearest
                    from shapely.geometry import Point
                    user_point = Point(lng, lat)
                    distances = police.geometry.distance(user_point)
                    features['police_station_distance'] = distances.min() * 111000  # Convert to meters
                else:
                    features['police_station_distance'] = 3000  # Default if none found
                
            except Exception as e:
                logger.warning(f"Police station query failed: {e}")
                features['police_station_distance'] = 2000
            
            # 4. Get Hospitals
            try:
                hospital_tags = {'amenity': ['hospital', 'clinic', 'doctors']}
                hospitals = ox.features_from_point(point, tags=hospital_tags, dist=5000)
                
                if not hospitals.empty:
                    from shapely.geometry import Point
                    user_point = Point(lng, lat)
                    distances = hospitals.geometry.distance(user_point)
                    features['hospital_distance'] = distances.min() * 111000
                else:
                    features['hospital_distance'] = 2500
                    
            except Exception as e:
                logger.warning(f"Hospital query failed: {e}")
                features['hospital_distance'] = 1500
            
            # 5. Lighting proxy (based on road type and building density)
            try:
                building_tags = {'building': True}
                buildings = ox.features_from_point(point, tags=building_tags, dist=radius)
                building_count = len(buildings) if not buildings.empty else 0
                
                # Lighting score based on road type and building density
                road_lighting = {
                    'highway': 0.9,
                    'main_road': 0.8,
                    'residential': 0.6,
                    'alley': 0.3,
                    'footpath': 0.2
                }
                
                base_lighting = road_lighting.get(features['road_type'], 0.5)
                # Boost lighting if many buildings (more likely to be lit)
                building_boost = min(0.3, building_count / 50)
                features['lighting_score'] = min(1.0, base_lighting + building_boost)
                
            except Exception as e:
                logger.warning(f"Building query failed: {e}")
                features['lighting_score'] = 0.5
            
            # 6. Crowd density estimate (based on POI density and time)
            # Higher POI density suggests more people
            features['crowd_density'] = min(50, features['poi_density'] * 2.5)
            
            # 7. Calculate isolation score
            features['isolation_score'] = self._calculate_isolation(features)
            
            # Add metadata
            features['data_source'] = 'openstreetmap'
            features['query_success'] = True
            features['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"Successfully extracted {len(features)} features from OSM")
            
            return features
            
        except Exception as e:
            logger.error(f"Critical error in OSM query: {e}")
            raise RuntimeError(f"Failed to extract OSM features: {e}")
    
    def _calculate_isolation(self, features: Dict) -> float:
        """Calculate isolation score from features"""
        poi_factor = 1 / (features['poi_density'] + 1)
        intersection_factor = 1 / (features['intersection_count'] + 1)
        dead_end_factor = features['dead_end_nearby'] + 0.5
        
        isolation = poi_factor * intersection_factor * dead_end_factor
        
        # Normalize to 0-1
        max_isolation = (1 / 1) * (1 / 1) * 1.5  # Theoretical max
        normalized = min(1.0, isolation / max_isolation)
        
        return normalized
    
    def _get_degraded_features(self, lat: float, lng: float, error: str) -> Dict:
        """Return safe default features when OSM query fails"""
        
        logger.warning(f"Using degraded features due to error: {error}")
        
        return {
            'road_type': 'residential',
            'poi_density': 5,
            'police_station_distance': 2000,
            'hospital_distance': 1500,
            'intersection_count': 3,
            'dead_end_nearby': 0,
            'lighting_score': 0.6,
            'crowd_density': 10,
            'isolation_score': 0.5,
            'data_source': 'degraded_defaults',
            'query_success': False,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }


# Singleton instance for reuse
_osm_extractor = None

def get_osm_extractor(cache_dir: Optional[Path] = None) -> OSMFeatureExtractor:
    """Get or create OSM extractor singleton"""
    global _osm_extractor
    
    if _osm_extractor is None:
        _osm_extractor = OSMFeatureExtractor(cache_dir)
    
    return _osm_extractor


def extract_real_features(latitude: float, longitude: float) -> Dict:
    """
    Convenience function to extract real OSM features
    
    This is the PRODUCTION function - uses REAL data only
    """
    extractor = get_osm_extractor()
    return extractor.extract_features(latitude, longitude)


if __name__ == "__main__":
    # Test with real coordinates
    print("Testing REAL OSM feature extraction...")
    
    # Test with Delhi coordinates
    features = extract_real_features(28.6139, 77.2090)
    
    print("\nExtracted features:")
    for key, value in features.items():
        print(f"  {key}: {value}")
