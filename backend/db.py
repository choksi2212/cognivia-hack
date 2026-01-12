"""
Database utilities for SITARA backend
Handles logging of risk assessments, alerts, and routes to PostgreSQL
"""

import os
from typing import Optional, Dict, List
from datetime import datetime
import logging
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:niklaus2212@localhost:5432/sitara")

# SQLAlchemy setup
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    logger.error(f"Failed to connect to database: {e}")
    engine = None
    SessionLocal = None
    Base = None


# Database Models (matching Prisma schema)
class Location(Base):
    """Location tracking table"""
    __tablename__ = "locations"
    
    id = Column(String, primary_key=True)
    userId = Column(String, nullable=False, default="anonymous")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    riskScore = Column(Float, nullable=True)
    riskLevel = Column(String, nullable=True)
    agentState = Column(String, nullable=True)
    hour = Column(Integer, nullable=True)
    dayOfWeek = Column(Integer, nullable=True)
    roadType = Column(String, nullable=True)
    poiDensity = Column(Float, nullable=True)


class Alert(Base):
    """Alerts and notifications table"""
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True)
    userId = Column(String, nullable=False, default="anonymous")
    type = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    riskScore = Column(Float, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)


class Route(Base):
    """Route history table"""
    __tablename__ = "routes"
    
    id = Column(String, primary_key=True)
    startLat = Column(Float, nullable=False)
    startLng = Column(Float, nullable=False)
    endLat = Column(Float, nullable=False)
    endLng = Column(Float, nullable=False)
    waypoints = Column(JSON, nullable=True)
    riskScore = Column(Float, nullable=False)
    riskLevel = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class SystemLog(Base):
    """System logs for analytics"""
    __tablename__ = "system_logs"
    
    id = Column(String, primary_key=True)
    eventType = Column(String, nullable=False)
    event_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


# Database helper functions
def get_db() -> Optional[Session]:
    """Get database session"""
    if SessionLocal is None:
        logger.warning("Database not configured")
        return None
    
    try:
        db = SessionLocal()
        return db
    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        return None


def init_db():
    """Initialize database tables"""
    if Base is None or engine is None:
        logger.error("Cannot initialize database - connection failed")
        return False
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        return False


def log_location(
    lat: float,
    lng: float,
    risk_score: float,
    risk_level: str,
    agent_state: str,
    features: Dict,
    user_id: str = "anonymous"
) -> bool:
    """Log location assessment to database"""
    db = get_db()
    if db is None:
        return False
    
    try:
        import uuid
        location = Location(
            id=str(uuid.uuid4()),
            userId=user_id,
            latitude=lat,
            longitude=lng,
            riskScore=risk_score,
            riskLevel=risk_level,
            agentState=agent_state,
            hour=features.get('hour'),
            dayOfWeek=features.get('day_of_week'),
            roadType=features.get('road_type'),
            poiDensity=features.get('poi_density'),
            timestamp=datetime.utcnow()
        )
        db.add(location)
        db.commit()
        logger.info(f"Logged location: {lat}, {lng} - Risk: {risk_level}")
        return True
    except Exception as e:
        logger.error(f"Failed to log location: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def log_alert(
    user_id: str,
    alert_type: str,
    priority: int,
    message: str,
    risk_score: float,
    lat: Optional[float] = None,
    lng: Optional[float] = None
) -> bool:
    """Log alert to database"""
    db = get_db()
    if db is None:
        return False
    
    try:
        import uuid
        alert = Alert(
            id=str(uuid.uuid4()),
            userId=user_id,
            type=alert_type,
            priority=priority,
            message=message,
            riskScore=risk_score,
            latitude=lat,
            longitude=lng,
            timestamp=datetime.utcnow()
        )
        db.add(alert)
        db.commit()
        logger.info(f"Logged alert: {alert_type} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to log alert: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def log_route(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
    risk_score: float,
    risk_level: str,
    waypoints: Optional[List] = None
) -> bool:
    """Log route analysis to database"""
    db = get_db()
    if db is None:
        return False
    
    try:
        import uuid
        route = Route(
            id=str(uuid.uuid4()),
            startLat=start_lat,
            startLng=start_lng,
            endLat=end_lat,
            endLng=end_lng,
            riskScore=risk_score,
            riskLevel=risk_level,
            waypoints=waypoints,
            timestamp=datetime.utcnow()
        )
        db.add(route)
        db.commit()
        logger.info(f"Logged route: ({start_lat},{start_lng}) -> ({end_lat},{end_lng})")
        return True
    except Exception as e:
        logger.error(f"Failed to log route: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def log_system_event(event_type: str, metadata: Optional[Dict] = None) -> bool:
    """Log system event to database"""
    db = get_db()
    if db is None:
        return False
    
    try:
        import uuid
        log = SystemLog(
            id=str(uuid.uuid4()),
            eventType=event_type,
            event_metadata=metadata,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        logger.debug(f"Logged system event: {event_type}")
        return True
    except Exception as e:
        logger.error(f"Failed to log system event: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def get_recent_locations(user_id: str = "anonymous", limit: int = 10) -> List[Dict]:
    """Get recent location assessments"""
    db = get_db()
    if db is None:
        return []
    
    try:
        locations = db.query(Location)\
            .filter(Location.userId == user_id)\
            .order_by(Location.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return [{
            'id': loc.id,
            'latitude': loc.latitude,
            'longitude': loc.longitude,
            'riskScore': loc.riskScore,
            'riskLevel': loc.riskLevel,
            'agentState': loc.agentState,
            'timestamp': loc.timestamp.isoformat()
        } for loc in locations]
    except Exception as e:
        logger.error(f"Failed to get recent locations: {e}")
        return []
    finally:
        db.close()


def get_statistics() -> Dict:
    """Get database statistics"""
    db = get_db()
    if db is None:
        return {'connected': False}
    
    try:
        total_locations = db.query(Location).count()
        total_alerts = db.query(Alert).count()
        total_routes = db.query(Route).count()
        total_logs = db.query(SystemLog).count()
        
        return {
            'connected': True,
            'total_locations': total_locations,
            'total_alerts': total_alerts,
            'total_routes': total_routes,
            'total_logs': total_logs
        }
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return {'connected': False, 'error': str(e)}
    finally:
        db.close()
