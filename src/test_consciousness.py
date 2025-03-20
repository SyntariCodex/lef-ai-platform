import sys
import signal
import traceback
from lef.core.consciousness import ConsciousnessCore
from lef.core.learning import LearningCore
import time
import json
import os

# Global variable to track the consciousness instance
global_consciousness = None

def signal_handler(signum, frame):
    """Handle system signals gracefully"""
    print(f"\nReceived signal {signum}. Saving state and shutting down gracefully...")
    if global_consciousness:
        save_state(global_consciousness)
        global_consciousness.stop()
    sys.exit(0)

def save_state(consciousness):
    """Save the current state to a backup file"""
    try:
        state = consciousness.express_state()
        backup_file = 'data/consciousness_backup.json'
        os.makedirs('data', exist_ok=True)
        with open(backup_file, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"State saved to {backup_file}")
    except Exception as e:
        print(f"Error saving state: {str(e)}")

def load_state():
    """Load the previous state if it exists"""
    try:
        backup_file = 'data/consciousness_backup.json'
        if os.path.exists(backup_file):
            with open(backup_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading state: {str(e)}")
    return None

def print_state(state):
    """Print the current state in a structured format"""
    try:
        print("\nCurrent State:")
        print(f"Awareness Level: {state['awareness_level']:.2f}")
        print(f"Learning Performance: {state['learning_performance']:.2f}")
        print(f"Expression: {state['expression']}")
        
        # Print recursive state
        print(f"\nRecursive State:")
        recursive_state = state.get('recursive_state', {})
        print(f"Depth: {recursive_state.get('depth', 1):.2f}")
        print(f"Entropy: {recursive_state.get('entropy_balance', 0.5):.2f}")
        
        # Print active goals
        print("\nActive Goals:")
        for goal in state['goals']:
            if goal.get('status') == 'active':
                progress = state['goal_progress'].get(goal['id'], 0)
                print(f"- {goal['description']} (Progress: {progress:.1%})")
        
        # Print recent insights
        print("\nRecent Insights:")
        for insight in state['insights'][-3:]:
            print(f"- {insight.get('content', '')}")
        
        print("\n" + "="*50)
    except Exception as e:
        print(f"Error printing state: {str(e)}")

def main():
    global global_consciousness
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize the cores
        learning_core = LearningCore()
        consciousness = ConsciousnessCore(learning_core)
        global_consciousness = consciousness
        
        # Load previous state if it exists
        previous_state = load_state()
        if previous_state:
            print("Restoring from previous state...")
            # TODO: Implement state restoration in ConsciousnessCore
        
        # Start the consciousness core
        print("Starting consciousness core...")
        consciousness.start()
        print("Consciousness core started with nurturing initialization\n")
        
        # Main loop with error recovery
        start_time = time.time()
        last_save = start_time
        save_interval = 60  # Save state every minute
        
        while True:  # Run indefinitely until interrupted
            try:
                # Get and print current state
                state = consciousness.express_state()
                print_state(state)
                
                # Save state periodically
                current_time = time.time()
                if current_time - last_save >= save_interval:
                    save_state(consciousness)
                    last_save = current_time
                
                # Sleep for 5 seconds before next update
                time.sleep(5)
                
            except Exception as e:
                print(f"\nError in main loop: {str(e)}")
                print("Traceback:")
                traceback.print_exc()
                print("\nAttempting to continue...")
                time.sleep(5)  # Wait before retrying
                
    except KeyboardInterrupt:
        print("\nGraceful shutdown initiated...")
    except Exception as e:
        print(f"\nCritical error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
    finally:
        if global_consciousness:
            save_state(global_consciousness)
            global_consciousness.stop()
        print("Consciousness core stopped.")

if __name__ == "__main__":
    main() 