from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import Config

Base = declarative_base()

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.engine = create_engine(Config.DATABASE_URL, echo=Config.DEBUG)
            cls._instance.SessionLocal = sessionmaker(bind=cls._instance.engine)
        return cls._instance

    def get_session(self):
        return self.SessionLocal()
    
    def init_db(self):
        Base.metadata.create_all(self.engine)

db = Database()
