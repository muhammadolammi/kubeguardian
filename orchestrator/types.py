from pydantic import BaseModel
from typing import Optional

class Payload(BaseModel):
    resource: str
    type: str
    name: str
    namespace: Optional[str] = None   # cluster-scoped safe
    reason: Optional[str] = None
    message: Optional[str] = None
    conditions: list[dict] = []
    timestamp: Optional[str] = None
    tier: Optional[str] = None
