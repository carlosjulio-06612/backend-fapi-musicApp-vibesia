# File: app/models/audit_log.py (CORRECTED VERSION)

from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class AuditLog(Base):
    __tablename__ = 'audit_log'
    __table_args__ = {'schema': 'vibesia_schema'}
    
    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    app_user_id = Column(Integer, ForeignKey('vibesia_schema.users.user_id', ondelete='SET NULL'), nullable=True)
    
    app_user_email = Column(String(255), nullable=True)
    app_user_role = Column(String(50), nullable=True)
    

    db_user_name = Column(String(100), nullable=False, server_default=func.current_user())
    action_type = Column(String(10), nullable=False)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=True)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    connection_ip = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    api_endpoint = Column(String(255), nullable=True)
    request_id = Column(String(100), nullable=True)
    application_name = Column(String(50), server_default='vibesia_app')
    environment = Column(String(20), server_default='production')
    
    app_user = relationship("User", foreign_keys=[app_user_id])