"""Database setup and initialization script"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from sqlalchemy import create_engine
    from config.settings import DATABASE_URL
    from src.data.models import Base
    from src.utils.logger import logger
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required packages: pip install sqlalchemy python-dotenv loguru")
    sys.exit(1)

def setup_database():
    """Create all database tables"""
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        
        # Create data directories
        data_dirs = [
            Path("data/raw"),
            Path("data/processed"), 
            Path("data/models")
        ]
        
        for dir_path in data_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            # Create .gitkeep files
            (dir_path / ".gitkeep").touch()
        
        logger.info("Data directories created successfully")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
    print("✅ Database setup completed!")