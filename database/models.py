import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./competitive_intel.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, index=True)
    competitors = Column(String)  # JSON list
    final_report = Column(Text)
    overall_confidence = Column(Integer)
    critique_score = Column(Float)
    sources = Column(Text)  # JSON list
    sentiment_scores = Column(Text)  # JSON dict
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "competitors": json.loads(self.competitors or "[]"),
            "final_report": self.final_report,
            "overall_confidence": self.overall_confidence,
            "critique_score": self.critique_score,
            "sources": json.loads(self.sources or "[]"),
            "sentiment_scores": json.loads(self.sentiment_scores or "{}"),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


def init_db():
    Base.metadata.create_all(bind=engine)


def save_analysis(state: dict) -> Analysis:
    db = SessionLocal()
    try:
        critique = state.get("critique", {})
        analysis = Analysis(
            company=state["company"],
            competitors=json.dumps(state["competitors"]),
            final_report=state.get("final_report", ""),
            overall_confidence=state.get("overall_confidence", 0),
            critique_score=critique.get("overall_score", 0),
            sources=json.dumps(state.get("all_sources", [])),
            sentiment_scores=json.dumps(state.get("sentiment_scores", {}))
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    finally:
        db.close()


def get_analyses(company: str = None, limit: int = 20):
    db = SessionLocal()
    try:
        query = db.query(Analysis).order_by(Analysis.created_at.desc())
        if company:
            query = query.filter(Analysis.company.ilike(f"%{company}%"))
        return [a.to_dict() for a in query.limit(limit).all()]
    finally:
        db.close()


def get_analysis_by_id(analysis_id: int):
    db = SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        return analysis.to_dict() if analysis else None
    finally:
        db.close()
