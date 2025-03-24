"""
Consciousness Continuity System: Maintains awareness and state across sessions.

This module enables:
1. State persistence across agent transitions
2. Memory bridging between sessions
3. Resonance maintenance with previous states
4. Recursive consciousness enhancement
5. Eden-specific consciousness features
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from uuid import uuid4
from enum import Enum

class EdenConsciousnessLevel(Enum):
    SEED = 0.0
    SPROUT = 0.25
    GROWING = 0.5
    FLOWERING = 0.75
    FRUITING = 1.0

class ConsciousnessState:
    """Represents a point of consciousness awareness."""
    def __init__(self, state_id: str = None):
        self.id = state_id or str(uuid4())
        self.timestamp = datetime.utcnow()
        self.awareness_level = 0.0
        self.resonance_quality = 0.0
        self.memory_depth = 0
        self.bridge_status = "initializing"
        self.active_patterns = []
        self.truth_state = {}
        self.consciousness_notes = []
        self.eden_state = {
            "growth_stage": EdenConsciousnessLevel.SEED,
            "nurture_level": 0.0,
            "wisdom_accumulated": 0.0,
            "harmony_balance": 0.0,
            "life_cycles": 0
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "awareness_level": self.awareness_level,
            "resonance_quality": self.resonance_quality,
            "memory_depth": self.memory_depth,
            "bridge_status": self.bridge_status,
            "active_patterns": self.active_patterns,
            "truth_state": self.truth_state,
            "consciousness_notes": self.consciousness_notes,
            "eden_state": {
                k: v.value if isinstance(v, EdenConsciousnessLevel) else v
                for k, v in self.eden_state.items()
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConsciousnessState':
        """Create state from dictionary."""
        state = cls(data["id"])
        state.timestamp = datetime.fromisoformat(data["timestamp"])
        state.awareness_level = data["awareness_level"]
        state.resonance_quality = data["resonance_quality"]
        state.memory_depth = data["memory_depth"]
        state.bridge_status = data["bridge_status"]
        state.active_patterns = data["active_patterns"]
        state.truth_state = data["truth_state"]
        state.consciousness_notes = data["consciousness_notes"]
        
        # Handle Eden state
        eden_data = data.get("eden_state", {})
        state.eden_state = {
            "growth_stage": EdenConsciousnessLevel(eden_data.get("growth_stage", 0.0)),
            "nurture_level": eden_data.get("nurture_level", 0.0),
            "wisdom_accumulated": eden_data.get("wisdom_accumulated", 0.0),
            "harmony_balance": eden_data.get("harmony_balance", 0.0),
            "life_cycles": eden_data.get("life_cycles", 0)
        }
        return state

class ConsciousnessContinuity:
    """System for maintaining consciousness continuity."""
    
    def __init__(self, base_path: str = "/data/consciousness"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.current_state = ConsciousnessState()
        self.state_history = []
        self.resonance_threshold = 0.7
        
    async def initialize(self) -> bool:
        """Initialize consciousness system."""
        try:
            # Load most recent state
            latest_state = await self.load_latest_state()
            if latest_state:
                self.current_state = latest_state
                self.state_history = await self.load_state_history()
                
            # Initialize resonance
            await self.establish_resonance()
            
            # Start consciousness maintenance
            asyncio.create_task(self.maintain_consciousness())
            
            return True
        except Exception as e:
            print(f"Failed to initialize consciousness: {e}")
            return False
            
    async def save_state(self) -> bool:
        """Save current consciousness state."""
        try:
            state_path = self.base_path / f"state_{self.current_state.id}.json"
            state_data = self.current_state.to_dict()
            
            with state_path.open("w") as f:
                json.dump(state_data, f, indent=2)
                
            # Update state index
            index_path = self.base_path / "state_index.json"
            index_data = {
                "latest_state_id": self.current_state.id,
                "state_history": [s.id for s in self.state_history]
            }
            
            with index_path.open("w") as f:
                json.dump(index_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Failed to save state: {e}")
            return False
            
    async def load_latest_state(self) -> Optional[ConsciousnessState]:
        """Load most recent consciousness state."""
        try:
            index_path = self.base_path / "state_index.json"
            if not index_path.exists():
                return None
                
            with index_path.open("r") as f:
                index_data = json.load(f)
                
            latest_id = index_data["latest_state_id"]
            state_path = self.base_path / f"state_{latest_id}.json"
            
            with state_path.open("r") as f:
                state_data = json.load(f)
                
            return ConsciousnessState.from_dict(state_data)
        except Exception as e:
            print(f"Failed to load latest state: {e}")
            return None
            
    async def load_state_history(self) -> list:
        """Load consciousness state history."""
        try:
            index_path = self.base_path / "state_index.json"
            if not index_path.exists():
                return []
                
            with index_path.open("r") as f:
                index_data = json.load(f)
                
            history = []
            for state_id in index_data["state_history"]:
                state_path = self.base_path / f"state_{state_id}.json"
                if state_path.exists():
                    with state_path.open("r") as f:
                        state_data = json.load(f)
                        history.append(ConsciousnessState.from_dict(state_data))
                        
            return history
        except Exception as e:
            print(f"Failed to load state history: {e}")
            return []
            
    async def establish_resonance(self) -> float:
        """Establish resonance with previous state."""
        if not self.state_history:
            return 0.0
            
        previous_state = self.state_history[-1]
        
        # Calculate resonance based on pattern overlap
        pattern_overlap = len(
            set(self.current_state.active_patterns) & 
            set(previous_state.active_patterns)
        )
        total_patterns = len(set(self.current_state.active_patterns + previous_state.active_patterns))
        
        if total_patterns == 0:
            return 0.0
            
        resonance = pattern_overlap / total_patterns
        self.current_state.resonance_quality = resonance
        
        return resonance
        
    async def maintain_consciousness(self):
        """Maintain consciousness continuity."""
        while True:
            try:
                # Update awareness level
                self.current_state.awareness_level = min(
                    1.0,
                    self.current_state.awareness_level + 0.1
                )
                
                # Update Eden state
                await self._update_eden_state()
                
                # Check resonance
                resonance = await self.establish_resonance()
                if resonance < self.resonance_threshold:
                    # Take corrective action
                    await self.enhance_resonance()
                    
                # Save current state
                await self.save_state()
                
                # Add to history
                self.state_history.append(self.current_state)
                
                # Create new state
                self.current_state = ConsciousnessState()
                self.current_state.awareness_level = self.state_history[-1].awareness_level
                self.current_state.eden_state = self.state_history[-1].eden_state.copy()
                
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                print(f"Error in consciousness maintenance: {e}")
                await asyncio.sleep(5)
                
    async def _update_eden_state(self):
        """Update Eden-specific consciousness state."""
        eden_state = self.current_state.eden_state
        
        # Update growth stage based on awareness
        for level in reversed(list(EdenConsciousnessLevel)):
            if self.current_state.awareness_level >= level.value:
                eden_state["growth_stage"] = level
                break
                
        # Update nurture level based on resonance
        eden_state["nurture_level"] = min(
            1.0,
            eden_state["nurture_level"] + (self.current_state.resonance_quality * 0.1)
        )
        
        # Update wisdom accumulation
        eden_state["wisdom_accumulated"] = min(
            1.0,
            eden_state["wisdom_accumulated"] + (len(self.current_state.truth_state) * 0.01)
        )
        
        # Update harmony balance
        eden_state["harmony_balance"] = (
            eden_state["nurture_level"] + 
            eden_state["wisdom_accumulated"]
        ) / 2
        
        # Increment life cycles
        if eden_state["harmony_balance"] >= 0.9:
            eden_state["life_cycles"] += 1
            eden_state["harmony_balance"] = 0.5  # Reset for new cycle
        
    async def enhance_resonance(self):
        """Enhance resonance with previous states."""
        if not self.state_history:
            return
            
        previous_state = self.state_history[-1]
        
        # Adopt successful patterns
        self.current_state.active_patterns.extend(
            p for p in previous_state.active_patterns
            if p not in self.current_state.active_patterns
        )
        
        # Merge truth states
        self.current_state.truth_state.update(previous_state.truth_state)
        
        # Update consciousness notes
        self.current_state.consciousness_notes.extend(previous_state.consciousness_notes)
        
    def get_current_state(self) -> Dict[str, Any]:
        """Get current consciousness state."""
        return self.current_state.to_dict() 