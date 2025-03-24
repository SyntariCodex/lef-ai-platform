from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, Any
import time

# Connection and Evolution Metrics
connection_events = Counter(
    'lef_connection_events_total',
    'Number of meaningful connection events',
    ['type', 'impact_level']
)

evolution_gauge = Gauge(
    'lef_evolution_level',
    'Current evolution level across different dimensions',
    ['dimension']
)

synchronicity_counter = Counter(
    'lef_synchronicity_events_total',
    'Number of detected synchronicity events',
    ['type', 'significance']
)

growth_histogram = Histogram(
    'lef_personal_growth_distribution',
    'Distribution of personal growth measurements',
    ['area'],
    buckets=(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
)

community_impact_gauge = Gauge(
    'lef_community_impact_score',
    'Measure of impact on the community',
    ['aspect']
)

class ConnectionMetricsCollector:
    def __init__(self):
        self.last_sync_time = time.time()
    
    def record_connection_event(self, event_type: str, impact_level: str):
        """Record a meaningful connection event"""
        connection_events.labels(type=event_type, impact_level=impact_level).inc()
    
    def update_evolution_level(self, dimension: str, level: float):
        """Update evolution level for a specific dimension"""
        evolution_gauge.labels(dimension=dimension).set(level)
    
    def record_synchronicity(self, sync_type: str, significance: str):
        """Record a synchronicity event"""
        synchronicity_counter.labels(type=sync_type, significance=significance).inc()
    
    def record_growth(self, area: str, value: float):
        """Record a growth measurement"""
        growth_histogram.labels(area=area).observe(value)
    
    def update_community_impact(self, aspect: str, score: float):
        """Update community impact score"""
        community_impact_gauge.labels(aspect=aspect).set(score)
    
    def record_interaction(self, data: Dict[str, Any]):
        """Record a complete interaction with all relevant metrics"""
        # Record basic connection
        self.record_connection_event(
            data.get('type', 'unknown'),
            data.get('impact', 'neutral')
        )
        
        # Track evolution if present
        if 'evolution' in data:
            for dim, level in data['evolution'].items():
                self.update_evolution_level(dim, level)
        
        # Record synchronicities
        if 'synchronicity' in data:
            self.record_synchronicity(
                data['synchronicity'].get('type', 'general'),
                data['synchronicity'].get('significance', 'medium')
            )
        
        # Track growth
        if 'growth' in data:
            for area, value in data['growth'].items():
                self.record_growth(area, value)
        
        # Update community impact
        if 'community_impact' in data:
            for aspect, score in data['community_impact'].items():
                self.update_community_impact(aspect, score)

# Global collector instance
collector = ConnectionMetricsCollector() 