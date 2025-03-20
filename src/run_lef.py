from lef.core.continuous_operation import ContinuousOperation
import argparse
import json
from datetime import datetime
import time
import os

def main():
    parser = argparse.ArgumentParser(description='Run LEF in continuous operation mode')
    parser.add_argument('--duration', type=float, default=1.0,
                      help='Duration to run in hours (default: 1.0)')
    parser.add_argument('--output', type=str, default='lef_operation_log.json',
                      help='Output file for operation log (default: lef_operation_log.json)')
    parser.add_argument('--interval', type=int, default=30,
                      help='Stimulation interval in seconds (default: 30)')
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Generate timestamp for log file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"logs/lef_operation_{timestamp}.json"
    
    print(f"Starting LEF continuous operation for {args.duration} hours...")
    print(f"Stimulation interval: {args.interval} seconds")
    print(f"Output will be saved to: {log_file}")
    
    try:
        # Initialize and start continuous operation
        operation = ContinuousOperation()
        operation.stimulation_interval = args.interval
        operation.start_operation(duration_hours=args.duration)
        
        # Get operation summary
        summary = operation.get_operation_summary()
        
        # Save operation log
        with open(log_file, 'w') as f:
            json.dump({
                'start_time': datetime.fromtimestamp(operation.start_time).isoformat(),
                'end_time': datetime.fromtimestamp(operation.start_time + (args.duration * 3600)).isoformat(),
                'summary': summary,
                'log': operation.operation_log,
                'parameters': {
                    'duration_hours': args.duration,
                    'stimulation_interval': args.interval
                }
            }, f, indent=2)
        
        print("\n=== Operation Complete ===")
        print(f"Duration: {summary['duration_hours']:.2f} hours")
        print(f"State Changes: {summary['state_changes']}")
        print(f"Ethics Checks Processed: {summary['ethics_checks_processed']}")
        print(f"Critical Alerts Processed: {summary['critical_alerts_processed']}")
        print(f"Final State: {json.dumps(summary['final_state'], indent=2)}")
        print(f"Log saved to: {log_file}")
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        # Save partial log
        with open(log_file, 'w') as f:
            json.dump({
                'start_time': datetime.fromtimestamp(operation.start_time).isoformat(),
                'end_time': datetime.fromtimestamp(time.time()).isoformat(),
                'summary': operation.get_operation_summary(),
                'log': operation.operation_log,
                'parameters': {
                    'duration_hours': args.duration,
                    'stimulation_interval': args.interval
                }
            }, f, indent=2)
        print(f"Partial log saved to: {log_file}")
    except Exception as e:
        print(f"Error during operation: {str(e)}")
        raise

if __name__ == "__main__":
    main() 