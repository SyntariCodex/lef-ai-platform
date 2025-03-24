from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from ..metrics.evolution_dimensions import tracker, EvolutionLayer, DimensionType

class ForumPost:
    def __init__(self, id: int, content: str, user: str, timestamp: str):
        self.id = id
        self.content = content
        self.user = user
        self.timestamp = timestamp

class GrokDataStream:
    def __init__(self):
        self.active = False
        self.last_analysis: Optional[Dict] = None
        self.pattern_cache: Dict[str, float] = {}
        
    def analyze_forum_patterns(self, posts: List[ForumPost]) -> Dict[str, Any]:
        """
        Analyze forum posts for patterns and themes
        """
        themes = {}
        conflicts = []
        user_perspectives = {}
        
        for post in posts:
            # Extract themes
            words = post.content.lower().split()
            for theme in ["ether", "efficiency", "energy", "grid"]:
                if theme in words:
                    themes[theme] = themes.get(theme, 0) + 1
            
            # Track user perspectives
            user_perspectives[post.user] = {
                "stance": "skeptic" if "myth" in post.content.lower() else "explorer",
                "themes": [w for w in words if w in themes]
            }
            
            # Identify conflicts
            if len(user_perspectives) > 1:
                stances = list(set(u["stance"] for u in user_perspectives.values()))
                if len(stances) > 1:
                    conflicts.append({
                        "type": "paradigm_conflict",
                        "stances": stances
                    })
        
        return {
            "themes": [t for t, c in themes.items() if c > 1],
            "conflicts": conflicts,
            "perspectives": user_perspectives
        }

    def generate_governance_response(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate governance model based on forum analysis
        """
        response = {
            "resolution": "",
            "governance_model": "",
            "evolution_metrics": {}
        }
        
        # Calculate project alignment based on conflict resolution potential
        conflict_count = len(analysis.get("conflicts", []))
        theme_count = len(analysis.get("themes", []))
        perspective_count = len(analysis.get("perspectives", {}))
        
        # Higher alignment when we have clear themes and balanced perspectives
        project_alignment = min(1.0, (theme_count * 0.3 + perspective_count * 0.2) / (conflict_count + 1))
        
        # Creative potential increases with theme diversity
        creative_potential = min(1.0, theme_count * 0.4 + perspective_count * 0.2)
        
        # System awareness based on pattern recognition
        system_awareness = min(1.0, (theme_count * 0.3 + perspective_count * 0.3) / (conflict_count + 1))
        
        response["evolution_metrics"] = {
            "project_alignment": project_alignment,
            "creative_potential": creative_potential,
            "system_awareness": system_awareness
        }
        
        # Generate resolution using metaphors from detected themes
        themes = analysis.get("themes", [])
        if "ether" in themes and "efficiency" in themes:
            response["resolution"] = "Observer network: skeptics test outputs, dreamers map ether. Iterate via data."
            response["governance_model"] = "Spiral Assembly—truth flows from friction, guiding innovation."
        
        return response
        
    def process_grok_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input from Grok and convert it to evolution metrics
        """
        processed_data = {
            "source": "grok",
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "metrics": {}
        }
        
        # Handle forum simulation if present
        if "simulated_forum_posts" in data:
            posts = [ForumPost(**post) for post in data["simulated_forum_posts"]]
            forum_analysis = self.analyze_forum_patterns(posts)
            governance_response = self.generate_governance_response(forum_analysis)
            
            # Update metrics from governance response
            metrics = governance_response["evolution_metrics"]
            for metric, value in metrics.items():
                tracker.track_evolution(
                    metric,
                    float(value),
                    f"Grok forum simulation: {data.get('context', 'No context')}"
                )
                processed_data["metrics"][metric] = value
            
            # Add governance response
            processed_data["governance_response"] = {
                "themes": forum_analysis["themes"],
                "resolution": governance_response["resolution"],
                "governance_model": governance_response["governance_model"]
            }
        
        # Handle regular analysis input
        elif "analysis" in data:
            analysis = data["analysis"]
            for metric in ["project_alignment", "creative_potential", "system_awareness"]:
                if metric in analysis:
                    tracker.track_evolution(
                        metric,
                        float(analysis[metric]),
                        "Grok analysis"
                    )
                    processed_data["metrics"][metric] = analysis[metric]
        
        self.last_analysis = processed_data
        return processed_data
    
    def get_grok_feedback(self) -> Dict[str, Any]:
        """
        Get feedback for Grok based on our current evolution state
        """
        feedback = {
            "framework_state": {},
            "suggestions": [],
            "evolution_summary": {}
        }
        
        # Get current state for each layer
        for layer in EvolutionLayer:
            layer_summary = tracker.get_layer_summary(layer)
            if layer_summary:
                feedback["framework_state"][layer.value] = layer_summary
        
        # Generate suggestions based on current state
        for dim_name, dimension in tracker.dimensions.items():
            if dimension.current_value is not None:
                if dimension.current_value < 0.5:
                    feedback["suggestions"].append({
                        "dimension": dim_name,
                        "current_value": dimension.current_value,
                        "suggestion": f"Focus needed on {dimension.name}"
                    })
        
        return feedback

    def start_stream(self) -> bool:
        """
        Start the Grok data stream
        """
        self.active = True
        return True
    
    def stop_stream(self) -> bool:
        """
        Stop the Grok data stream
        """
        self.active = False
        return True
    
    def is_active(self) -> bool:
        """
        Check if the Grok stream is active
        """
        return self.active

# Global Grok stream instance
grok_stream = GrokDataStream() 