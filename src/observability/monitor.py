import logging
import time
from functools import wraps

# Setup basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("SportExpert")

def log_agent_execution(agent_name):
    """
    Decorator to log agent execution time and status.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Agent [{agent_name}] starting task...")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Agent [{agent_name}] completed in {duration:.2f}s")
                return result
            except Exception as e:
                logger.error(f"Agent [{agent_name}] failed: {str(e)}")
                raise
        return wrapper
    return decorator

# In a real GCP environment, we would also integrate with Cloud Logging and Cloud Monitoring (Trace) here.
