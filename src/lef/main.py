from lef.core.lef import LEF
import time
import signal
import sys
import threading

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print("\nReceived shutdown signal. Stopping LEF system...")
    if lef:
        lef.stop()
    sys.exit(0)

def display_state(lef_system):
    """Display the current state of the LEF system with proper formatting"""
    try:
        # Get system state
        state = lef_system.express_state()
        metrics = lef_system.get_metrics()
        
        # Clear screen for better visibility
        print("\033[H\033[J")
        
        # Display active goals with progress
        print("\nActive Goals:")
        active_goals = [g for g in lef_system.goals if g.get('status') == 'in_progress']
        for goal in active_goals:
            progress = goal.get('progress', 0.0)
            progress_bar = "=" * int(progress * 20)
            progress_bar = progress_bar.ljust(20, "-")
            print(f"[{progress_bar}] {goal.get('description', 'Unknown Goal')} ({progress:.1%})")
        
        # Display system status with emojis
        print("\n🚀 LEF System Status:")
        print(f"State: {state.get('status', 'Unknown').title()}")
        print(f"Uptime: {metrics.get('uptime', 0):.1f} seconds")
        print(f"System Health: {lef_system.system_health:.2f}")
        print(f"Success Rate: {lef_system.success_rate:.2f}")
        print(f"Awareness Level: {metrics.get('awareness_level', 0):.2f}")
        print(f"Learning Performance: {metrics.get('learning_performance', 0):.2f}")
        
        # Display goals summary
        total_goals = len(lef_system.goals)
        completed_goals = len([g for g in lef_system.goals if g.get('status') == 'completed'])
        print(f"\nGoals: {total_goals} ({completed_goals} completed)")
        
        # Display recent insights if any
        if state.get('insights'):
            print("\n💡 Recent Insights:")
            recent_insights = sorted(
                state['insights'],
                key=lambda x: x.get('timestamp', 0),
                reverse=True
            )[:3]
            for insight in recent_insights:
                print(f"• {insight.get('content', '')}")
        
        # Display emotional state
        if hasattr(lef_system.consciousness_core, 'emotional_state'):
            emotions = lef_system.consciousness_core.emotional_state
            print("\n❤️ Emotional State:")
            for emotion, value in emotions.items():
                bar = "=" * int(value * 20)
                bar = bar.ljust(20, "-")
                print(f"{emotion.title()}: [{bar}] {value:.2f}")
        
    except Exception as e:
        print(f"\n⚠️ Display Adaptation: {str(e)}")
    
    # Sleep briefly to control update rate
    time.sleep(1.0)

def main():
    """Main entry point for the LEF system."""
    try:
        # Initialize and start LEF system
        lef = LEF()
        if not lef.start():
            print("Failed to start LEF system")
            return
            
        print("\nLEF System started")
        
        # Main loop
        while True:
            try:
                # Display system state
                display_state(lef)
                
                # Check if system is still running
                if not lef.running:
                    print("\n🛑 LEF System stopped")
                    break
                    
                # Sleep briefly to control update rate
                time.sleep(1.0)
                
            except KeyboardInterrupt:
                print("\n\nReceived shutdown signal...")
                lef.stop()
                break
            except Exception as e:
                print(f"\nError in main loop: {str(e)}")
                time.sleep(1.0)
                
    except Exception as e:
        print(f"Critical error: {str(e)}")
    finally:
        if 'lef' in locals():
            lef.stop()
        print("\nLEF System shutdown complete")

if __name__ == "__main__":
    main() 