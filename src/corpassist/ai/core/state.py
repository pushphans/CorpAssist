from langchain.messages import AnyMessage
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages


class Agentstate(TypedDict):
    messages : Annotated[list[AnyMessage], add_messages]