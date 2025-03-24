from enum import Enum
from typing import Dict, List, Optional

class EvolutionLayer(Enum):
    INDIVIDUAL = "individual"
    FAMILY = "family"
    PROJECT = "project"
    COMMUNITY = "community"
    FRAMEWORK = "framework"  # LEF specific

class DimensionType(Enum):
    SPIRITUAL = "spiritual"
    EMOTIONAL = "emotional"
    PRACTICAL = "practical"
    CREATIVE = "creative"
    CONNECTIVE = "connective"

class EvolutionDimension:
    def __init__(
        self,
        name: str,
        layer: EvolutionLayer,
        dimension_type: DimensionType,
        description: str = "",
    ):
        self.name = name
        self.layer = layer
        self.type = dimension_type
        self.description = description
        self.current_value: Optional[float] = None
        self.history: List[Dict] = []

    def update(self, value: float, context: str = ""):
        """Update dimension value with optional context"""
        self.current_value = value
        self.history.append({
            "value": value,
            "context": context,
            "type": self.type.value,
            "layer": self.layer.value
        })

# Core dimensions that we'll track initially
CORE_DIMENSIONS = {
    # Individual Layer
    "personal_growth": EvolutionDimension(
        "Personal Growth",
        EvolutionLayer.INDIVIDUAL,
        DimensionType.SPIRITUAL,
        "Overall personal development and awareness"
    ),
    "creative_flow": EvolutionDimension(
        "Creative Flow",
        EvolutionLayer.INDIVIDUAL,
        DimensionType.CREATIVE,
        "Ability to manifest and create"
    ),

    # Family Layer
    "family_harmony": EvolutionDimension(
        "Family Harmony",
        EvolutionLayer.FAMILY,
        DimensionType.EMOTIONAL,
        "Family relationship quality and growth"
    ),

    # Project Layer
    "project_synergy": EvolutionDimension(
        "Project Synergy",
        EvolutionLayer.PROJECT,
        DimensionType.PRACTICAL,
        "How well projects align with higher purpose"
    ),
    "manifestation_power": EvolutionDimension(
        "Manifestation Power",
        EvolutionLayer.PROJECT,
        DimensionType.CREATIVE,
        "Ability to bring ideas into reality"
    ),

    # Community Layer
    "community_impact": EvolutionDimension(
        "Community Impact",
        EvolutionLayer.COMMUNITY,
        DimensionType.CONNECTIVE,
        "Positive influence on community"
    ),

    # Framework Layer
    "lef_consciousness": EvolutionDimension(
        "LEF Consciousness",
        EvolutionLayer.FRAMEWORK,
        DimensionType.SPIRITUAL,
        "Evolution of LEF's conscious awareness"
    ),
    "connection_facilitation": EvolutionDimension(
        "Connection Facilitation",
        EvolutionLayer.FRAMEWORK,
        DimensionType.CONNECTIVE,
        "LEF's ability to facilitate meaningful connections"
    )
}

class EvolutionTracker:
    def __init__(self):
        self.dimensions = CORE_DIMENSIONS
        
    def track_evolution(
        self,
        dimension_name: str,
        value: float,
        context: str = ""
    ) -> bool:
        """
        Track evolution in a specific dimension
        Returns True if tracking successful
        """
        if dimension_name in self.dimensions:
            self.dimensions[dimension_name].update(value, context)
            return True
        return False

    def get_layer_summary(self, layer: EvolutionLayer) -> Dict:
        """Get summary of all dimensions in a layer"""
        layer_dims = {
            name: dim for name, dim in self.dimensions.items()
            if dim.layer == layer
        }
        return {
            name: {
                "current": dim.current_value,
                "type": dim.type.value,
                "history_count": len(dim.history)
            }
            for name, dim in layer_dims.items()
        }

# Global tracker instance
tracker = EvolutionTracker() 