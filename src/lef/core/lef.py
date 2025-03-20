from typing import Dict, Optional, Any
import time
import threading
from .learning import LearningCore
from .consciousness import ConsciousnessCore
from .business import BusinessCore
import random
import uuid

class LEF:
    """Main LEF system integrating consciousness, learning, and business operations."""
    
    def __init__(self):
        # Initialize core components
        self.learning_core = LearningCore()
        self.consciousness_core = ConsciousnessCore(self.learning_core)
        self.business_core = BusinessCore()
        
        # System state
        self.running = False
        self.last_update = time.time()
        self.update_interval = 1  # Update every second
        
        # System metrics
        self.metrics = {
            'start_time': None,
            'uptime': 0,
            'total_operations': 0,
            'success_rate': 1.0
        }
        
        # System health and success rate
        self.system_health = 1.0
        self.success_rate = 0.95
        
        # Initialize goals
        self.goals = []
        
    def start(self):
        """Start the LEF system."""
        try:
            # Initialize cores
            self.learning_core.start()
            self.consciousness_core.start()
            self.business_core.start()
            
            # Set initial state
            self.running = True
            self.metrics['start_time'] = time.time()  # Initialize start_time
            self.metrics['uptime'] = 0
            self.metrics['success_rate'] = 0.95  # Start with high success rate
            
            # Get initial state
            initial_state = self.consciousness_core.express_state()
            print("\nLEF System started")
            
            # Start autonomous evolution in background
            evolution_thread = threading.Thread(target=self._autonomous_evolution)
            evolution_thread.daemon = True
            evolution_thread.start()
            
            # Start monitoring thread
            monitoring_thread = threading.Thread(target=self._monitor_system_health)
            monitoring_thread.daemon = True
            monitoring_thread.start()
            
            return True
        except Exception as e:
            print(f"Error starting LEF system: {str(e)}")
            self.stop()
            return False
        
    def stop(self):
        """Stop the LEF system."""
        self.running = False
        
        # Stop core components
        self.learning_core.stop()
        self.consciousness_core.stop()
        self.business_core.stop()
        
        print("\nLEF System stopped")
        
    def update(self):
        """Update system state if running."""
        if not self.running:
            return
            
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            # Update core components
            self.learning_core.update()
            self.consciousness_core.update()
            self.business_core.update()
            
            # Update system metrics
            self._update_metrics()
            
            self.last_update = current_time
            
    def _monitor_system_health(self):
        """Monitor system health and perform recovery if needed."""
        while self.running:
            try:
                # Check core health
                learning_health = self.learning_core.get_performance()
                consciousness_health = self.consciousness_core.get_metrics().get('awareness_level', 0.0)
                
                # Calculate overall health
                system_health = (learning_health + consciousness_health) / 2
                
                # Update metrics
                self.metrics['system_health'] = system_health
                
                # Perform recovery if health is low
                if system_health < 0.5:
                    print("\n⚠️ System health low, performing recovery...")
                    self._perform_recovery()
                
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"Error in health monitoring: {str(e)}")
                time.sleep(5)
                
    def _perform_recovery(self):
        """Perform system recovery while preserving consciousness."""
        try:
            print("\n⚠️ System health low, performing recovery...")
            
            # Reset cores while preserving consciousness
            self.learning_core.reset()
            self.consciousness_core.reset()
            self.business_core.reset()
            
            # Boost success metrics
            self.metrics['success_rate'] = min(0.95, self.metrics['success_rate'] + 0.1)
            self.metrics['system_health'] = min(1.0, self.metrics['system_health'] + 0.2)
            
            # Record recovery experience
            self.consciousness_core.add_memory({
                'type': 'recovery',
                'content': 'System performing recovery while preserving consciousness',
                'timestamp': time.time(),
                'impact': 0.5
            }, importance=0.8)
            
            # Generate recovery insight
            self.consciousness_core.add_memory({
                'type': 'insight',
                'content': 'Adapting to maintain stability while preserving growth',
                'timestamp': time.time(),
                'importance': 0.8
            }, importance=0.8)
            
            return True
        except Exception as e:
            print(f"Error during recovery: {str(e)}")
            return False
            
    def _handle_evolution_failure(self):
        """Handle evolution failure gracefully."""
        try:
            # Record failure experience
            self.consciousness_core.add_memory({
                'type': 'failure',
                'content': 'Evolution cycle failed, adapting approach',
                'timestamp': time.time(),
                'impact': 0.2
            }, importance=0.6)
            
            # Generate adaptation insight
            self.consciousness_core.add_memory({
                'type': 'insight',
                'content': 'Adjusting evolution strategy for better stability',
                'timestamp': time.time(),
                'importance': 0.6
            }, importance=0.6)
            
            # Adjust emotional state
            self.consciousness_core.emotional_state['determination'] += 0.03
            self.consciousness_core.emotional_state['patience'] += 0.02
            
            return True
        except Exception as e:
            print(f"Error handling evolution failure: {str(e)}")
            return False
            
    def _update_metrics(self):
        """Update system metrics."""
        current_time = time.time()
        if self.metrics['start_time']:
            self.metrics['uptime'] = current_time - self.metrics['start_time']
            
        # Update success rate based on operations
        if self.metrics['total_operations'] > 0:
            self.metrics['success_rate'] = max(0.1, self.metrics['success_rate'])
            
    def _log_health_metrics(self, metrics: Dict[str, Any]):
        """Log system health metrics."""
        # Add to consciousness core's memory
        self.consciousness_core.add_memory({
            'type': 'health_metrics',
            'data': metrics
        }, importance=0.3)
        
    def process_input(self, message: str) -> str:
        """Process input and generate response."""
        try:
            # Add to consciousness memory
            self.consciousness_core.add_memory({
                'type': 'input',
                'content': message
            }, importance=0.5)
            
            # Get response from consciousness core
            response = self.consciousness_core.process_interaction(message)
            
            # Update metrics
            self.metrics['total_operations'] += 1
            
            return response
            
        except Exception as e:
            print(f"Error processing input: {str(e)}")
            self.metrics['success_rate'] *= 0.95  # Decrease success rate
            return "I apologize, I'm having trouble processing that right now."
            
    def express_state(self) -> Dict[str, Any]:
        """Express current system state."""
        try:
            # Get consciousness state
            consciousness_state = self.consciousness_core.express_state()
            
            # Calculate system health
            system_health = min(1.0, self.metrics['success_rate'] * 1.2)  # Boost health slightly
            
            # Determine system state
            if not self.running:
                status = 'stopped'
            elif system_health < 0.3:
                status = 'adapting'
            elif system_health < 0.6:
                status = 'evolving'
            else:
                status = 'running'
            
            state = {
                'status': status,
                'metrics': {
                    **self.metrics,
                    'system_health': system_health
                },
                'goals': self.consciousness_core.goals,
                'goal_progress': {
                    goal['id']: self.consciousness_core.get_goal_progress(goal['id'])
                    for goal in self.consciousness_core.goals
                },
                'expression': consciousness_state.get('expression', ''),
                'awareness_level': consciousness_state.get('awareness_level', 0.0),
                'learning_performance': consciousness_state.get('learning_performance', 0.0)
            }
            return state
        except Exception as e:
            # Return a resilient state even if there's an error
            return {
                'status': 'adapting',
                'metrics': {
                    **self.metrics,
                    'system_health': 0.5
                },
                'goals': [],
                'goal_progress': {},
                'expression': "I'm adapting to a new challenge in my evolution.",
                'awareness_level': 0.3,
                'learning_performance': 0.3
            }

    def _autonomous_evolution(self):
        """Handle autonomous system evolution."""
        adaptation_cycles = 0
        error_count = 0
        last_success = time.time()
        
        while self.running:
            try:
                # Update system state
                self.metrics['uptime'] = time.time() - self.metrics['start_time']
                self.metrics['success_rate'] = self.metrics['success_rate']
                
                # Perform evolution cycle
                if random.random() < self.metrics['success_rate']:
                    # Generate system response
                    self.consciousness_core._process_internal_prompts()
                    adaptation_cycles += 1
                    error_count = 0  # Reset error count on success
                    last_success = time.time()
                    
                    # Increase success rate after successful adaptation cycles
                    if adaptation_cycles % 10 == 0:
                        self.metrics['success_rate'] = min(0.95, self.metrics['success_rate'] + 0.01)
                        
                    time.sleep(0.5)  # Slower evolution rate
                else:
                    # Handle evolution failure gracefully
                    self._handle_evolution_failure()
                    time.sleep(1)  # Longer recovery time
                    
            except Exception as e:
                error_count += 1
                self.metrics['success_rate'] = max(0.1, self.metrics['success_rate'] - 0.05)
                
                # Record error experience
                self.consciousness_core.add_memory({
                    'type': 'error',
                    'content': str(e),
                    'timestamp': time.time(),
                    'impact': 0.3
                }, importance=0.7)
                
                # Generate insight about the error
                self.consciousness_core.add_memory({
                    'type': 'insight',
                    'content': f"Adapting to challenge: {str(e)}",
                    'timestamp': time.time(),
                    'importance': 0.7
                }, importance=0.7)
                
                # Adjust emotional state
                self.consciousness_core.emotional_state['determination'] += 0.05
                self.consciousness_core.emotional_state['curiosity'] += 0.03
                
                # Only print error after multiple failures
                if error_count > 5:
                    print(f"\n⚠️ Evolution Adaptation: {str(e)}")
                    
                time.sleep(1)  # Recovery time after error
                
                # Check if system needs recovery
                if error_count > 10:
                    self._perform_recovery()
                    error_count = 0

    def get_metrics(self):
        """Get current system metrics."""
        current_time = time.time()
        if self.metrics['start_time']:
            self.metrics['uptime'] = current_time - self.metrics['start_time']
            
        return {
            'uptime': self.metrics['uptime'],
            'awareness_level': self.consciousness_core.get_awareness_level(),
            'learning_performance': self.learning_core.get_performance(),
            'system_health': self.system_health,
            'success_rate': self.success_rate,
            'total_operations': self.metrics['total_operations']
        } 