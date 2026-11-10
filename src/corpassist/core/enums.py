from enum import Enum


class TicketPriority(Enum):   
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"



class TicketStatus(Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"   



class LeaveType(Enum):
    CASUAL = "CASUAL"
    SICK = "SICK"
    EARNED = "EARNED"

class LeaveStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"