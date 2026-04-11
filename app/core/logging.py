import sys
from loguru import logger

def setup_logging():
    # Remove default handler
    logger.remove()
    
    # Add standard output handler with structured format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    
    # Add file handler for persistent logs (optional, commented out for now)
    # logger.add("logs/app.log", rotation="500 MB", retention="10 days", compression="zip")

    logger.info("Logging initialized with Loguru.")

# Initialize logging on import
setup_logging()
