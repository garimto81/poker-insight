#!/usr/bin/env python3
"""
데이터베이스 초기 설정 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import init_db, engine, Base
from config.settings import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """데이터베이스와 테이블 생성"""
    try:
        logger.info(f"Creating database tables...")
        logger.info(f"Database URL: {Config.DATABASE_URL}")
        
        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully!")
        
        # 생성된 테이블 확인
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Created tables: {', '.join(tables)}")
        
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()