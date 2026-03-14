from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///jobs.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Job(Base):

    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    pdf_name = Column(String)
    frames = Column(Integer)
    style = Column(String)
    video_path = Column(String)
    status = Column(String)
    
Base.metadata.create_all(bind=engine)