from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from config.settings import Config

Base = declarative_base()

class PokerSite(Base):
    __tablename__ = 'poker_sites'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    url = Column(String(255))
    network = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    traffic_data = relationship('TrafficData', back_populates='site')
    news_items = relationship('NewsItem', back_populates='site')

class TrafficData(Base):
    __tablename__ = 'traffic_data'
    
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('poker_sites.id'), nullable=False)
    cash_players = Column(Integer)
    tournament_players = Column(Integer)
    total_players = Column(Integer)
    seven_day_average = Column(Float)
    peak_players = Column(Integer)
    rank = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    site = relationship('PokerSite', back_populates='traffic_data')

class NewsItem(Base):
    __tablename__ = 'news_items'
    
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('poker_sites.id'))
    title = Column(String(500), nullable=False)
    url = Column(String(500), unique=True)
    content = Column(Text)
    author = Column(String(100))
    published_date = Column(DateTime)
    category = Column(String(50))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    site = relationship('PokerSite', back_populates='news_items')

class CrawlLog(Base):
    __tablename__ = 'crawl_logs'
    
    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)  # 'pokernews' or 'pokerscout'
    status = Column(String(20), nullable=False)  # 'success', 'failed', 'partial'
    items_scraped = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    
# Database setup
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()