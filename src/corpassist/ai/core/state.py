from corpassist.core.enums import TicketPriority
from corpassist.core.enums import TicketStatus
from langchain.messages import AnyMessage
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages


class SupervisorState(TypedDict):
    messages : Annotated[list[AnyMessage], add_messages]



class TicketState(TypedDict):
    messages : Annotated[list[AnyMessage], add_messages]


class LeaveState(TypedDict):
    messages : Annotated[list[AnyMessage], add_messages]
