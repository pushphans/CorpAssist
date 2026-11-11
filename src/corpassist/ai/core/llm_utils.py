import uuid
from dataclasses import dataclass



@dataclass
class AiContext:
    user_id : uuid.UUID