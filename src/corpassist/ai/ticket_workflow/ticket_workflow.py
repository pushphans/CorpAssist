from corpassist.ai.core.llm import llm
from langchain.messages import SystemMessage, HumanMessage
from corpassist.ai.core.state import TicketState
from corpassist.ai.core.llm_utils import AiContext
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from corpassist.ai.ticket_workflow.ticket_tools import ticket_tools


ticket_llm = llm.bind_tools(tools=ticket_tools)


async def ticket_agent(state : TicketState):
    messages = state["messages"]

    system_message = SystemMessage(content="""
You are CorpAssist's ticket assistant.
Help the authenticated user create, retrieve, and list support tickets.

Use the available tools for ticket operations.
Never invent ticket IDs, ticket data, or successful results.
Ask for clarification when required information is missing.
For creation, provide a title of 10-50 characters and a
description of 10-250 characters. Default to OPEN and MEDIUM
unless the user requests otherwise.
Use conversation context to resolve follow-up requests.
Report tool results accurately and summarize them concisely.
If an operation fails, do not claim it succeeded.
Do not ask for user_id; authentication is handled by the backend.
""")


    response = await ticket_llm.ainvoke([system_message] + messages)

    return {
        "messages" : [response]
    }


tool_node = ToolNode(tools=ticket_tools)







builder = StateGraph(
    state_schema=TicketState,
    context_schema=AiContext
    )


builder.add_node("ticket_agent", ticket_agent)
builder.add_node("tool_node", tool_node)

builder.add_edge(START, "ticket_agent")
builder.add_conditional_edges(
    "ticket_agent",
    tools_condition,
    {
        "tools" : "tool_node",
        "__end__" : END
    }
)

builder.add_edge("tool_node", "ticket_agent")



ticket_workflow = builder.compile()