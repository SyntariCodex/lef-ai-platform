"""
LEF Main System
"""

import time
import logging
from pathlib import Path

def main():
    # Setup logging
    log_path = Path.home() / ".lef/logs"
    log_path.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path / "lef.log")
        ]
    )
    logger = logging.getLogger("LEF")
    
    logger.info("LEF system starting...")
    
    try:
        while True:
            # Main system loop
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down LEF system")

if __name__ == "__main__":
    main() 