from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from auth.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    mode = Column(String)
    findings_json = Column(Text)
    summary_json = Column(Text)
    total_resources_scanned = Column(Integer)
    total_issues_found = Column(Integer)
    total_estimated_monthly_savings_usd = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
