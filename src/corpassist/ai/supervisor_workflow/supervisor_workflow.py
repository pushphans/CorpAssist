from corpassist.ai.core.llm import llm
from typing import Literal
from pydantic import BaseModel
from langchain.messages import SystemMessage
from corpassist.ai.core.llm_utils import AiContext
from corpassist.ai.leave_workflow.leave_workflow import leave_workflow
from corpassist.ai.ticket_workflow.ticket_workflow import ticket_workflow
from langgraph.graph import StateGraph, START, END
from corpassist.ai.core.state import SupervisorState
from langgraph.types import Command



class SupervisorOutputSchema(BaseModel):
    decision : Literal["ticket_agent", "leave_agent", "FINISH"]


supervisor_llm = llm.with_structured_output(schema=SupervisorOutputSchema)
    



async def supervisor_node(state : SupervisorState) -> Command[Literal["ticket_agent", "leave_agent", "__end__"]]:

    messages = state["messages"]


    system_message = SystemMessage(content="""
You supervise ticket and leave workflows.
s
Choose ticket_agent for pending ticket-related work.
Choose leave_agent for pending leave-related work.
For requests involving both, route to one worker at a time.
Read worker results before choosing the next action.
Do not repeat work already completed for the current request.
Choose FINISH when the request is answered, or a worker has
asked the user for clarification and you must wait for a reply.
""")


    response : SupervisorOutputSchema = await supervisor_llm.ainvoke([system_message] + messages)

    decision = response.decision

    if decision == "ticket_agent":
        return Command(goto="ticket_agent")

    elif decision == "leave_agent":
        return Command(goto="leave_agent")

    else:
        return Command(goto=END)
    


builder = StateGraph(state_schema=SupervisorState, context_schema=AiContext)
builder.add_node("supervisor_node", supervisor_node)
builder.add_node("ticket_agent", ticket_workflow)
builder.add_node("leave_agent", leave_workflow)


builder.add_edge(START, "supervisor_node")
builder.add_edge("ticket_agent", "supervisor_node")
builder.add_edge("leave_agent", "supervisor_node")

supervisor_workflow = builder.compile()