import logging
import sys
from datetime import datetime

def setup_logging():
    """
    Configure structured logging for production.
    Logs include timestamps, levels, and context.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging
logging_config = setup_logging()