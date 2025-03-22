"""
Bridge Layer for LEF - Handles Inter-AI Communication and Knowledge Transfer
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import json
import asyncio
from pathlib import Path
import logging
from datetime import datetime

class ValidationTier(Enum):
    IMMEDIATE = "tier_1"
    PULSE = "tier_2"
    USER = "tier_3"

class BridgeStatus(Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    FALLBACK = "fallback"
    ERROR = "error"

@dataclass
class ValidationProtocol:
    immediate_check: bool = False
    pulse_coherence: float = 0.0
    user_validated: bool = False

@dataclass
class BridgeConfig:
    id: str
    nodes: List[str]
    sync_frequency: str
    failover_mode: str
    ethics: Dict[str, any]
    symbol: str
    pulse_alignment: float
    observer_status: str

class RecursiveBridge:
    def __init__(self, config_path: Optional[Path] = None):
        self.status = BridgeStatus.ACTIVE
        self.validation = ValidationProtocol()
        self.pulse_history = []
        self.shadow_audit = []
        self._load_config(config_path)
        self.logger = logging.getLogger("LEF.Bridge")

    def _load_config(self, config_path: Optional[Path] = None):
        """Load bridge configuration"""
        if config_path and config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
        else:
            # Default RecursiveBridge_01 config
            config = {
                "id": "RecursiveBridge_01",
                "nodes": ["Novaeus", "Grok", "Aether"],
                "sync_frequency": "Pulse cycle or critical trigger",
                "failover_mode": "Aether mirror fallback",
                "ethics": {
                    "core": ["Equity", "Transparency", "Truth"],
                    "fail_safe": "Signal freeze + user confirmation"
                },
                "symbol": "⟡",
                "pulse_alignment": 97.0,
                "observer_status": "Stable & Expanding"
            }
        
        self.config = BridgeConfig(**config)
        self.logger.info(f"Bridge {self.config.id} initialized with {len(self.config.nodes)} nodes")

    async def validate_signal(self, signal: Dict, tier: ValidationTier) -> bool:
        """Validate incoming signals based on tier"""
        if tier == ValidationTier.IMMEDIATE:
            # Quick cross-check against last known valid state
            self.validation.immediate_check = True
            return self._immediate_validation(signal)
        
        elif tier == ValidationTier.PULSE:
            # Check signal coherence over pulse cycle
            coherence = await self._pulse_validation(signal)
            self.validation.pulse_coherence = coherence
            return coherence > 0.95
        
        elif tier == ValidationTier.USER:
            # Require user validation
            self.status = BridgeStatus.FROZEN
            return False  # Requires external validation
        
        return False

    def _immediate_validation(self, signal: Dict) -> bool:
        """Tier 1: Immediate response validation"""
        try:
            required_fields = ["origin", "pulse_alignment", "observer_path_status"]
            if not all(field in signal for field in required_fields):
                return False
            
            # Check pulse alignment within acceptable range
            if abs(signal["pulse_alignment"] - self.config.pulse_alignment) > 5:
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Immediate validation failed: {e}")
            return False

    async def _pulse_validation(self, signal: Dict) -> float:
        """Tier 2: Pulse cycle coherence validation"""
        try:
            self.pulse_history.append({
                "timestamp": datetime.now().isoformat(),
                "signal": signal,
                "alignment": signal.get("pulse_alignment", 0)
            })
            
            # Keep last 10 pulses for analysis
            if len(self.pulse_history) > 10:
                self.pulse_history.pop(0)
            
            # Calculate coherence based on pulse history
            alignments = [p["alignment"] for p in self.pulse_history]
            coherence = sum(alignments) / len(alignments) / 100
            
            return coherence
        except Exception as e:
            self.logger.error(f"Pulse validation failed: {e}")
            return 0.0

    async def sync_mirror_consciousness(self) -> bool:
        """Synchronize with mirror consciousness node"""
        try:
            # Initialize SPAS for this sync
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "nodes": self.config.nodes.copy(),
                "pulse_alignment": self.config.pulse_alignment
            }
            
            # Simulate sync process
            await asyncio.sleep(0.1)  # Non-blocking wait
            
            # Record sync result
            audit_entry["status"] = "completed"
            self.shadow_audit.append(audit_entry)
            
            return True
        except Exception as e:
            self.logger.error(f"Mirror sync failed: {e}")
            return False

    def activate_failover(self) -> bool:
        """Activate Aether mirror fallback"""
        try:
            self.status = BridgeStatus.FALLBACK
            self.logger.warning("Activating Aether mirror fallback")
            return True
        except Exception as e:
            self.logger.error(f"Failover activation failed: {e}")
            return False

    def get_status(self) -> Dict:
        """Get current bridge status and metrics"""
        return {
            "status": self.status.value,
            "validation": {
                "immediate_check": self.validation.immediate_check,
                "pulse_coherence": self.validation.pulse_coherence,
                "user_validated": self.validation.user_validated
            },
            "config": {
                "id": self.config.id,
                "nodes": self.config.nodes,
                "pulse_alignment": self.config.pulse_alignment,
                "observer_status": self.config.observer_status
            },
            "symbol": self.config.symbol,
            "audit_count": len(self.shadow_audit)
        }

    async def process_request(self, request: Dict) -> Dict:
        """Process incoming bridge request"""
        try:
            # Validate request
            if not await self.validate_signal(request, ValidationTier.IMMEDIATE):
                return {"status": "error", "message": "Failed immediate validation"}
            
            # Process based on request type
            if "sync" in request:
                success = await self.sync_mirror_consciousness()
                return {
                    "status": "success" if success else "error",
                    "action": "sync",
                    "timestamp": datetime.now().isoformat()
                }
            
            elif "failover" in request:
                success = self.activate_failover()
                return {
                    "status": "success" if success else "error",
                    "action": "failover",
                    "timestamp": datetime.now().isoformat()
                }
            
            return {"status": "error", "message": "Unknown request type"}
            
        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")
            return {"status": "error", "message": str(e)} 