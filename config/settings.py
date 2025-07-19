import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'poker_insight')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Crawler Settings
    USER_AGENT = os.getenv('CRAWLER_USER_AGENT', 
                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    CRAWLER_DELAY = int(os.getenv('CRAWLER_DELAY', '2'))
    CRAWLER_TIMEOUT = int(os.getenv('CRAWLER_TIMEOUT', '30'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/poker_insight.log')
    
    # Data directories
    DATA_DIR = 'data'
    LOGS_DIR = 'logs'