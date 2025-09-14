from typing import Any, Optional
from pydantic import BaseModel

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
    labels: dict[str, str] = {}              # object labels
    annotations: dict[str, str] = {}         # object annotations
    extra: dict[str, Any] = {}               # kind-specific info (pods, services, ingress, etc.)
