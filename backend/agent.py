"""
Agentic Decision Layer for SITARA
Finite State Machine for proportional risk intervention
"""

import json
import logging
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent states in finite state machine"""
    SAFE = "safe"
    CAUTION = "caution"
    ELEVATED_RISK = "elevated_risk"
    HIGH_RISK = "high_risk"


class ActionType(Enum):
    """Types of actions agent can recommend"""
    NONE = "none"
    MONITOR = "monitor"
    SUGGEST_ROUTE = "suggest_route"
    SILENT_CHECKIN = "silent_checkin"
    RECOMMEND_ESCALATION = "recommend_escalation"


@dataclass
class AgentContext:
    """Context maintained by agent over time"""
    current_state: str
    current_risk_score: float
    previous_risk_score: float
    risk_velocity: float  # Rate of risk change
    time_in_current_state: float  # seconds
    last_alert_time: Optional[datetime]
    alert_count: int
    location_history: List[Dict]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        if self.last_alert_time:
            data['last_alert_time'] = self.last_alert_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentContext':
        """Create from dictionary"""
        if data.get('last_alert_time'):
            data['last_alert_time'] = datetime.fromisoformat(data['last_alert_time'])
        return cls(**data)


@dataclass
class AgentDecision:
    """Decision made by agent"""
    action: str
    state: str
    risk_score: float
    message: str
    priority: int  # 0=none, 1=low, 2=medium, 3=high
    suggested_routes: Optional[List[Dict]] = None
    escalation_options: Optional[List[str]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class SafetyAgent:
    """
    Agentic Decision System for SITARA
    
    Uses Finite State Machine to:
    - Observe environment continuously
    - Track changes over time
    - Decide when to intervene
    - Act proportionally
    """
    
    # State transition thresholds
    THRESHOLDS = {
        'safe_to_caution': 0.35,
        'caution_to_elevated': 0.60,
        'elevated_to_high': 0.80,
        'high_to_elevated': 0.70,
        'elevated_to_caution': 0.50,
        'caution_to_safe': 0.30
    }
    
    # Alert cooldown periods (seconds)
    ALERT_COOLDOWNS = {
        AgentState.SAFE: 600,  # 10 minutes
        AgentState.CAUTION: 300,  # 5 minutes
        AgentState.ELEVATED_RISK: 120,  # 2 minutes
        AgentState.HIGH_RISK: 60  # 1 minute
    }
    
    # Risk velocity thresholds (change per update)
    VELOCITY_THRESHOLDS = {
        'rapid_increase': 0.2,
        'moderate_increase': 0.1,
        'slow_increase': 0.05
    }
    
    def __init__(self, state_file: Optional[Path] = None):
        self.state_file = state_file
        self.context = self._load_or_create_context()
    
    def _load_or_create_context(self) -> AgentContext:
        """Load existing context or create new one"""
        
        if self.state_file and self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return AgentContext.from_dict(data)
            except Exception as e:
                logger.warning(f"Could not load agent state: {e}")
        
        # Create new context
        return AgentContext(
            current_state=AgentState.SAFE.value,
            current_risk_score=0.0,
            previous_risk_score=0.0,
            risk_velocity=0.0,
            time_in_current_state=0.0,
            last_alert_time=None,
            alert_count=0,
            location_history=[]
        )
    
    def _save_context(self):
        """Persist agent context"""
        if self.state_file:
            try:
                with open(self.state_file, 'w') as f:
                    json.dump(self.context.to_dict(), f, indent=2)
            except Exception as e:
                logger.error(f"Could not save agent state: {e}")
    
    def _calculate_risk_velocity(self, new_risk: float) -> float:
        """Calculate rate of risk change"""
        velocity = new_risk - self.context.previous_risk_score
        return velocity
    
    def _determine_next_state(self, risk_score: float) -> AgentState:
        """
        Determine next state based on current state and risk score
        Uses hysteresis to prevent oscillation
        """
        
        current = AgentState(self.context.current_state)
        
        # State transitions with hysteresis
        if current == AgentState.SAFE:
            if risk_score >= self.THRESHOLDS['safe_to_caution']:
                return AgentState.CAUTION
        
        elif current == AgentState.CAUTION:
            if risk_score >= self.THRESHOLDS['caution_to_elevated']:
                return AgentState.ELEVATED_RISK
            elif risk_score < self.THRESHOLDS['caution_to_safe']:
                return AgentState.SAFE
        
        elif current == AgentState.ELEVATED_RISK:
            if risk_score >= self.THRESHOLDS['elevated_to_high']:
                return AgentState.HIGH_RISK
            elif risk_score < self.THRESHOLDS['elevated_to_caution']:
                return AgentState.CAUTION
        
        elif current == AgentState.HIGH_RISK:
            if risk_score < self.THRESHOLDS['high_to_elevated']:
                return AgentState.ELEVATED_RISK
        
        return current
    
    def _should_send_alert(self) -> bool:
        """Check if enough time has passed since last alert"""
        
        if self.context.last_alert_time is None:
            return True
        
        current_state = AgentState(self.context.current_state)
        cooldown = self.ALERT_COOLDOWNS[current_state]
        
        time_since_alert = (datetime.now() - self.context.last_alert_time).total_seconds()
        
        return time_since_alert >= cooldown
    
    def _create_decision(self, risk_score: float, state: AgentState) -> AgentDecision:
        """Create decision based on state and context"""
        
        velocity = self.context.risk_velocity
        
        # SAFE state - no action needed
        if state == AgentState.SAFE:
            return AgentDecision(
                action=ActionType.NONE.value,
                state=state.value,
                risk_score=risk_score,
                message="Environment appears safe. Continue monitoring.",
                priority=0
            )
        
        # CAUTION state - silent monitoring
        elif state == AgentState.CAUTION:
            if velocity > self.VELOCITY_THRESHOLDS['moderate_increase']:
                return AgentDecision(
                    action=ActionType.MONITOR.value,
                    state=state.value,
                    risk_score=risk_score,
                    message="Risk increasing. Monitoring situation.",
                    priority=1
                )
            else:
                return AgentDecision(
                    action=ActionType.NONE.value,
                    state=state.value,
                    risk_score=risk_score,
                    message="Slight caution advised. Remain aware.",
                    priority=1
                )
        
        # ELEVATED_RISK state - suggest route change
        elif state == AgentState.ELEVATED_RISK:
            if self._should_send_alert():
                return AgentDecision(
                    action=ActionType.SUGGEST_ROUTE.value,
                    state=state.value,
                    risk_score=risk_score,
                    message="Consider taking a safer route. Alternative routes available.",
                    priority=2,
                    suggested_routes=[]  # Populated by route engine
                )
            else:
                return AgentDecision(
                    action=ActionType.MONITOR.value,
                    state=state.value,
                    risk_score=risk_score,
                    message="Elevated risk detected. Monitoring closely.",
                    priority=2
                )
        
        # HIGH_RISK state - recommend escalation (user controlled)
        elif state == AgentState.HIGH_RISK:
            if self._should_send_alert():
                return AgentDecision(
                    action=ActionType.RECOMMEND_ESCALATION.value,
                    state=state.value,
                    risk_score=risk_score,
                    message="High risk environment detected. Consider safety actions.",
                    priority=3,
                    escalation_options=[
                        "Share location with trusted contact",
                        "Find nearest safe place",
                        "Call emergency contact"
                    ]
                )
            else:
                return AgentDecision(
                    action=ActionType.SUGGEST_ROUTE.value,
                    state=state.value,
                    risk_score=risk_score,
                    message="High risk area. Safer route strongly recommended.",
                    priority=3,
                    suggested_routes=[]
                )
    
    def process_risk_update(self, risk_score: float, location: Optional[Dict] = None) -> AgentDecision:
        """
        Main decision loop
        
        Args:
            risk_score: Current risk score from ML model (0-1)
            location: Optional location data
        
        Returns:
            AgentDecision with recommended action
        """
        
        # Calculate risk velocity
        velocity = self._calculate_risk_velocity(risk_score)
        
        # Determine next state
        next_state = self._determine_next_state(risk_score)
        
        # Update context
        self.context.previous_risk_score = self.context.current_risk_score
        self.context.current_risk_score = risk_score
        self.context.risk_velocity = velocity
        
        # Check for state transition
        if next_state.value != self.context.current_state:
            logger.info(f"State transition: {self.context.current_state} -> {next_state.value}")
            self.context.current_state = next_state.value
            self.context.time_in_current_state = 0.0
        
        # Create decision
        decision = self._create_decision(risk_score, next_state)
        
        # Update alert tracking if action taken
        if decision.action != ActionType.NONE.value:
            if self._should_send_alert():
                self.context.last_alert_time = datetime.now()
                self.context.alert_count += 1
        
        # Update location history
        if location:
            self.context.location_history.append({
                'timestamp': datetime.now().isoformat(),
                'location': location,
                'risk_score': risk_score,
                'state': next_state.value
            })
            
            # Keep only last 100 locations
            self.context.location_history = self.context.location_history[-100:]
        
        # Persist state
        self._save_context()
        
        logger.info(f"Decision: {decision.action} (priority={decision.priority})")
        
        return decision
    
    def reset_context(self):
        """Reset agent to initial state"""
        self.context = AgentContext(
            current_state=AgentState.SAFE.value,
            current_risk_score=0.0,
            previous_risk_score=0.0,
            risk_velocity=0.0,
            time_in_current_state=0.0,
            last_alert_time=None,
            alert_count=0,
            location_history=[]
        )
        self._save_context()
        logger.info("Agent context reset to initial state")
    
    def get_state_summary(self) -> Dict:
        """Get current state summary"""
        return {
            'current_state': self.context.current_state,
            'risk_score': self.context.current_risk_score,
            'risk_velocity': self.context.risk_velocity,
            'alert_count': self.context.alert_count,
            'location_history_count': len(self.context.location_history)
        }


def main():
    """Test agent behavior"""
    from config import AGENT_STATE_PATH
    
    agent = SafetyAgent(state_file=AGENT_STATE_PATH)
    
    # Simulate risk progression
    test_scenarios = [
        (0.2, "Safe environment"),
        (0.4, "Slight increase"),
        (0.65, "Elevated risk"),
        (0.85, "High risk"),
        (0.7, "Risk decreasing"),
        (0.3, "Back to safer area")
    ]
    
    print("\n" + "="*60)
    print("Agent Simulation")
    print("="*60 + "\n")
    
    for risk_score, description in test_scenarios:
        print(f"\nScenario: {description} (risk={risk_score})")
        decision = agent.process_risk_update(risk_score)
        print(f"State: {decision.state}")
        print(f"Action: {decision.action}")
        print(f"Message: {decision.message}")
        print(f"Priority: {decision.priority}")
        print("-" * 60)


if __name__ == "__main__":
    main()
