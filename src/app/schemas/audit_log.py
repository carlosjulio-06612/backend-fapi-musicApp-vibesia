#app/schemas/audit_log.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    audit_id: int
    db_user_name: str
    app_user_id: Optional[int] = None
    app_user_email: Optional[str] = None
    app_user_role: Optional[str] = None
    action_type: str
    timestamp: datetime
    table_name: str
    record_id: Optional[int] = None
    old_values: Optional[dict | list] = None
    new_values: Optional[dict | list] = None
    connection_ip: Optional[str] = None 
    user_agent: Optional[str] = None
    api_endpoint: Optional[str] = None
    request_id: Optional[str] = None

class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
    total: int
    page: int
    per_page: int