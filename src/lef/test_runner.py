import time
import logging
from datetime import datetime
from .test_scenarios import TestScenario

def run_test():
    """Run the LEF test scenario and monitor performance"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=f'logs/lef_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )
    logger = logging.getLogger('LEF.TestRunner')
    
    try:
        # Initialize and run scenario
        scenario = TestScenario()
        start_time = time.time()
        
        logger.info("Starting LEF test scenario")
        scenario.run_scenario()
        
        # Calculate execution time
        execution_time = time.time() - start_time
        logger.info(f"Scenario completed in {execution_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        raise
        
if __name__ == "__main__":
    run_test() 