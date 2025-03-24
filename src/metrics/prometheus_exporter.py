from prometheus_client import start_http_server, Gauge, Counter
from typing import Dict, Any
import time
import threading
import logging

class LEFMetricsExporter:
    def __init__(self, port: int = 8000):
        self.port = port
        
        # Core metrics
        self.pattern_recognition_score = Gauge('lef_pattern_recognition_score', 
            'Current pattern recognition effectiveness score')
        self.system_awareness = Gauge('lef_system_awareness', 
            'Current system awareness level')
        self.evolution_score = Gauge('lef_evolution_score', 
            'Current evolution tracking score')
        
        # Category progress metrics
        self.category_progress = Gauge('lef_category_progress', 
            'Progress percentage by category', 
            ['category'])
        
        # Task status metrics
        self.task_status = Gauge('lef_task_status',
            'Number of tasks in each status',
            ['status'])
            
        # Event counters
        self.synchronicity_events = Counter('lef_synchronicity_events',
            'Number of synchronicity events detected')
        self.connection_events = Counter('lef_connection_events',
            'Number of meaningful connection events')
        self.growth_events = Counter('lef_growth_events',
            'Number of personal/community growth events')
            
        self._running = False
        self._thread = None
        
    def start(self):
        """Start the metrics server"""
        if self._running:
            return
            
        def _run_server():
            try:
                start_http_server(self.port)
                logging.info(f"Metrics server started on port {self.port}")
                while self._running:
                    time.sleep(1)
            except Exception as e:
                logging.error(f"Error in metrics server: {e}")
                self._running = False
                
        self._running = True
        self._thread = threading.Thread(target=_run_server, daemon=True)
        self._thread.start()
        
    def stop(self):
        """Stop the metrics server"""
        self._running = False
        if self._thread:
            self._thread.join()
            
    def update_metrics(self, metrics_data: Dict[str, Any]):
        """Update all metrics with new values"""
        try:
            # Update core metrics
            if 'pattern_recognition' in metrics_data:
                self.pattern_recognition_score.set(metrics_data['pattern_recognition'])
            if 'system_awareness' in metrics_data:
                self.system_awareness.set(metrics_data['system_awareness'])
            if 'evolution_score' in metrics_data:
                self.evolution_score.set(metrics_data['evolution_score'])
                
            # Update category progress
            if 'categories' in metrics_data:
                for category, progress in metrics_data['categories'].items():
                    self.category_progress.labels(category=category).set(progress)
                    
            # Update task status counts
            if 'task_status' in metrics_data:
                for status, count in metrics_data['task_status'].items():
                    self.task_status.labels(status=status).set(count)
                    
            # Increment event counters if events occurred
            if metrics_data.get('new_synchronicity_events', 0) > 0:
                self.synchronicity_events.inc(metrics_data['new_synchronicity_events'])
            if metrics_data.get('new_connection_events', 0) > 0:
                self.connection_events.inc(metrics_data['new_connection_events'])
            if metrics_data.get('new_growth_events', 0) > 0:
                self.growth_events.inc(metrics_data['new_growth_events'])
                
        except Exception as e:
            logging.error(f"Error updating metrics: {e}")
            
    def get_current_values(self) -> Dict[str, Any]:
        """Get current values of all metrics"""
        return {
            'pattern_recognition': self.pattern_recognition_score._value.get(),
            'system_awareness': self.system_awareness._value.get(),
            'evolution_score': self.evolution_score._value.get(),
            'categories': {
                label_dict['category']: self.category_progress._value.get(label_dict)
                for label_dict in self.category_progress._metrics
            },
            'task_status': {
                label_dict['status']: self.task_status._value.get(label_dict)
                for label_dict in self.task_status._metrics
            },
            'events': {
                'synchronicity': self.synchronicity_events._value.get(),
                'connection': self.connection_events._value.get(),
                'growth': self.growth_events._value.get()
            }
        }

# Example usage:
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    exporter = LEFMetricsExporter()
    exporter.start()
    
    # Example metrics update
    example_data = {
        'pattern_recognition': 85.5,
        'system_awareness': 92.0,
        'evolution_score': 78.5,
        'categories': {
            'Core Framework': 75.0,
            'Pattern Recognition': 85.0,
            'Evolution Tracking': 65.0
        },
        'task_status': {
            'NOT_STARTED': 5,
            'IN_PROGRESS': 8,
            'COMPLETE': 12
        },
        'new_synchronicity_events': 2,
        'new_connection_events': 3,
        'new_growth_events': 1
    }
    
    exporter.update_metrics(example_data)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        exporter.stop() 