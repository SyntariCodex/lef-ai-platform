from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import json
from enum import Enum
from .background_processor import MetricsProcessor

class PatternType(Enum):
    THEME = "theme"
    BRIDGE = "bridge"
    EVOLUTION = "evolution"
    METAPHOR = "metaphor"
    SYSTEM = "system"  # New type for system awareness

class SystemAwarenessLevel(Enum):
    SURFACE = "surface"
    INTERMEDIATE = "intermediate"
    DEEP = "deep"

class UnifiedPatternService:
    def __init__(self):
        self.patterns: Dict[PatternType, List[Dict[str, Any]]] = {
            pattern_type: [] for pattern_type in PatternType
        }
        self.last_processed: Dict[PatternType, datetime] = {
            pattern_type: datetime.min for pattern_type in PatternType
        }
        self.system_context: Dict[str, Any] = {
            "known_entities": set(),
            "relationships": [],
            "edge_cases": set(),
            "subtle_dynamics": []
        }
        self.evolution_detector = EvolutionPatternDetector()
        self.metrics_processor = MetricsProcessor()
        self.pending_tasks: Dict[str, PatternType] = {}

    def detect_patterns(self, data: Any, pattern_type: PatternType) -> List[Dict[str, Any]]:
        """
        Unified pattern detection across different types of patterns.
        Returns list of detected patterns with metadata.
        """
        patterns = []
        timestamp = datetime.now()

        if pattern_type == PatternType.THEME:
            patterns = self._detect_theme_patterns(data)
        elif pattern_type == PatternType.BRIDGE:
            patterns = self._detect_bridge_patterns(data)
        elif pattern_type == PatternType.EVOLUTION:
            task_id = self.metrics_processor.process_evolution_metrics(
                data,
                callback=self._handle_evolution_results
            )
            self.pending_tasks[task_id] = pattern_type
            patterns = []  # Results will be added when background task completes
        elif pattern_type == PatternType.METAPHOR:
            patterns = self._detect_metaphor_patterns(data)
        elif pattern_type == PatternType.SYSTEM:
            task_id = self.metrics_processor.process_system_awareness(
                data,
                callback=self._handle_system_results
            )
            self.pending_tasks[task_id] = pattern_type
            patterns = []  # Results will be added when background task completes

        self.last_processed[pattern_type] = timestamp
        if patterns:  # Only extend if we have immediate results
            self.patterns[pattern_type].extend(patterns)
        return patterns

    def _handle_evolution_results(self, results: Dict[str, Any]):
        """Handle results from background evolution processing"""
        if "error" in results:
            self.logger.error(f"Evolution processing error: {results['error']}")
            return

        pattern = self.evolution_detector.detect_evolution(results)
        
        # Update system context with evolution insights
        if pattern["insights"]:
            self.system_context["subtle_dynamics"].extend(
                {"type": "evolution_insight", "content": insight}
                for insight in pattern["insights"]
            )
        
        # Track complex relationships if in transformation/integration stage
        if pattern["stage"] in ["transformation", "integration"]:
            self.system_context["relationships"].append({
                "type": "evolution_stage",
                "stage": pattern["stage"],
                "metrics": pattern["metrics"]
            })
        
        self.patterns[PatternType.EVOLUTION].append(pattern)

    def _handle_system_results(self, results: Dict[str, Any]):
        """Handle results from background system awareness processing"""
        if "error" in results:
            self.logger.error(f"System awareness processing error: {results['error']}")
            return

        # Update system context
        self.system_context["known_entities"].update(results["entities"])
        self.system_context["subtle_dynamics"].extend(results["dynamics"])
        self.system_context["edge_cases"].update(results["edge_cases"])
        
        # Create system pattern
        pattern = {
            "timestamp": datetime.now().isoformat(),
            "awareness_level": self._calculate_awareness_level(),
            "entities": list(self.system_context["known_entities"]),
            "dynamics": self.system_context["subtle_dynamics"][-5:],
            "edge_cases": list(self.system_context["edge_cases"]),
            "confidence": results["confidence"]
        }
        
        self.patterns[PatternType.SYSTEM].append(pattern)

    def shutdown(self):
        """Shutdown the pattern service"""
        self.metrics_processor.shutdown()

    def _detect_theme_patterns(self, data: Any) -> List[Dict[str, Any]]:
        """Extract thematic patterns from data"""
        themes = []
        # Implementation will integrate existing theme detection algorithms
        return themes

    def _detect_bridge_patterns(self, data: Any) -> List[Dict[str, Any]]:
        """Detect bridging patterns between different perspectives"""
        bridges = []
        # Implementation will integrate existing bridge detection logic
        return bridges

    def _detect_evolution_patterns(self, data: Any) -> List[Dict[str, Any]]:
        """Track evolutionary patterns in system behavior"""
        pattern = self.evolution_detector.detect_evolution(data)
        
        # Update system context with evolution insights
        if pattern["insights"]:
            self.system_context["subtle_dynamics"].extend(
                {"type": "evolution_insight", "content": insight}
                for insight in pattern["insights"]
            )
        
        # Track complex relationships if in transformation/integration stage
        if pattern["stage"] in ["transformation", "integration"]:
            self.system_context["relationships"].append({
                "type": "evolution_stage",
                "stage": pattern["stage"],
                "metrics": pattern["metrics"]
            })
        
        return [pattern]

    def _detect_metaphor_patterns(self, data: Any) -> List[Dict[str, Any]]:
        """Identify metaphorical patterns for translation"""
        metaphors = []
        # Implementation will integrate existing metaphor detection
        return metaphors

    def _detect_system_patterns(self, data: Any) -> List[Dict[str, Any]]:
        """Enhanced system awareness detection"""
        system_patterns = []
        
        # Extract entities and their relationships
        new_entities = self._extract_entities(data)
        self.system_context["known_entities"].update(new_entities)
        
        # Detect subtle dynamics and edge cases
        dynamics = self._analyze_subtle_dynamics(data)
        self.system_context["subtle_dynamics"].extend(dynamics)
        
        # Identify edge cases and boundary conditions
        edge_cases = self._identify_edge_cases(data)
        self.system_context["edge_cases"].update(edge_cases)
        
        # Build comprehensive system pattern
        system_patterns.append({
            "timestamp": datetime.now().isoformat(),
            "awareness_level": self._calculate_awareness_level(),
            "entities": list(self.system_context["known_entities"]),
            "dynamics": self.system_context["subtle_dynamics"][-5:],  # Most recent
            "edge_cases": list(self.system_context["edge_cases"]),
            "confidence": self._calculate_system_confidence()
        })
        
        return system_patterns

    def _extract_entities(self, data: Any) -> Set[str]:
        """Extract system entities and their roles"""
        # Implementation will identify system components and actors
        return set()

    def _analyze_subtle_dynamics(self, data: Any) -> List[Dict[str, Any]]:
        """Analyze subtle system dynamics and interactions"""
        # Implementation will detect nuanced patterns and relationships
        return []

    def _identify_edge_cases(self, data: Any) -> Set[str]:
        """Identify system edge cases and boundary conditions"""
        # Implementation will find corner cases and exceptions
        return set()

    def _calculate_awareness_level(self) -> SystemAwarenessLevel:
        """Calculate current system awareness level"""
        entity_coverage = len(self.system_context["known_entities"])
        dynamic_depth = len(self.system_context["subtle_dynamics"])
        edge_understanding = len(self.system_context["edge_cases"])
        
        if entity_coverage > 20 and dynamic_depth > 10 and edge_understanding > 5:
            return SystemAwarenessLevel.DEEP
        elif entity_coverage > 10 and dynamic_depth > 5:
            return SystemAwarenessLevel.INTERMEDIATE
        else:
            return SystemAwarenessLevel.SURFACE

    def _calculate_system_confidence(self) -> float:
        """Calculate confidence in system understanding"""
        entity_weight = 0.4
        dynamics_weight = 0.35
        edge_weight = 0.25
        
        entity_score = min(1.0, len(self.system_context["known_entities"]) / 30)
        dynamics_score = min(1.0, len(self.system_context["subtle_dynamics"]) / 15)
        edge_score = min(1.0, len(self.system_context["edge_cases"]) / 10)
        
        return (entity_score * entity_weight +
                dynamics_score * dynamics_weight +
                edge_score * edge_weight)

    def get_pattern_stats(self) -> Dict[str, Any]:
        """Get statistics about pattern detection"""
        stats = {
            "total_patterns": sum(len(patterns) for patterns in self.patterns.values()),
            "patterns_by_type": {
                pattern_type.value: len(patterns) 
                for pattern_type, patterns in self.patterns.items()
            },
            "last_processed": {
                pattern_type.value: timestamp.isoformat()
                for pattern_type, timestamp in self.last_processed.items()
            }
        }
        
        # Add system awareness metrics
        if PatternType.SYSTEM in self.patterns:
            latest_system = self.patterns[PatternType.SYSTEM][-1] if self.patterns[PatternType.SYSTEM] else None
            stats["system_awareness"] = {
                "level": latest_system["awareness_level"].value if latest_system else "unknown",
                "confidence": latest_system["confidence"] if latest_system else 0.0,
                "entities_tracked": len(self.system_context["known_entities"]),
                "dynamics_tracked": len(self.system_context["subtle_dynamics"])
            }
        
        return stats

    def export_patterns(self, pattern_type: PatternType = None) -> str:
        """Export patterns as JSON"""
        if pattern_type:
            return json.dumps({
                "type": pattern_type.value,
                "patterns": self.patterns[pattern_type],
                "timestamp": datetime.now().isoformat()
            })
        return json.dumps({
            "patterns": {
                p_type.value: patterns
                for p_type, patterns in self.patterns.items()
            },
            "timestamp": datetime.now().isoformat()
        }) 