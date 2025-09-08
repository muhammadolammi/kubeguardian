from pydantic import BaseModel



class Payload(BaseModel):
    resource: str
    type: str
    tier: str
    name: str 
    namespace:str
    reason: str
    message: str
    conditions: list
    timestamp: str
