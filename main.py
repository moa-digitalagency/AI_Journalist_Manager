import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_init_database():
    """Check environment and initialize database on startup."""
    required_vars = ['DATABASE_URL']
    missing = [v for v in required_vars if not os.environ.get(v)]
    
    if missing:
        logger.warning(f"Missing environment variables: {', '.join(missing)}")
        logger.warning("Some features may not work correctly.")
    
    from init_db import run_initialization
    run_initialization()

check_and_init_database()

from app import app  # noqa: F401
