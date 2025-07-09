import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("loguru not installed, using standard logging")

try:
    from config.settings import LOG_LEVEL, LOGS_DIR
except ImportError:
    LOG_LEVEL = "INFO"
    LOGS_DIR = Path("logs")
    LOGS_DIR.mkdir(exist_ok=True)

def setup_logger():
    """Configure loguru logger"""
    try:
        logger.remove()  # Remove default handler
        
        # Console handler
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=LOG_LEVEL,
            colorize=True
        )
        
        # File handler
        logger.add(
            LOGS_DIR / "trendsense.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=LOG_LEVEL,
            rotation="10 MB",
            retention="1 week",
            compression="zip"
        )
    except Exception as e:
        print(f"Warning: Could not setup advanced logging: {e}")
    
    return logger

# Initialize logger
setup_logger()