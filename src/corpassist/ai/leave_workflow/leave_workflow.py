from langchain.messages import SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from corpassist.ai.core.llm import llm
from corpassist.ai.core.llm_utils import AiContext
from corpassist.ai.core.state import LeaveState
from corpassist.ai.leave_workflow.leave_tools import leave_tools


leave_llm = llm.bind_tools(tools=leave_tools)


async def leave_agent(state: LeaveState):
    system_message = SystemMessage(content="""
You are CorpAssist's leave assistant.
Help the authenticated user create, retrieve, list, update, and delete leave requests.

Use the available tools for leave operations.
Never invent leave IDs, leave records, or successful results.
Ask for clarification when required information is missing or ambiguous.
For creation, collect leave type, start date, end date, days count, and reason.
Leave type must be CASUAL, SICK, or EARNED. Dates use YYYY-MM-DD format.
Days count must be positive and end date must not precede start date.
Do not assume calendar days equal chargeable leave days; clarify when needed.
New requests are PENDING, not automatically approved.
For updates, provide only the fields the user wants to change.
Do not approve or reject leave requests; approval requires authorized handling.
Delete a request only when the user explicitly asks to delete it and the
target request is unambiguous. Otherwise ask for clarification.
Use conversation context to resolve follow-up requests.
Report tool results accurately and summarize them concisely.
If an operation fails, do not claim it succeeded.
Do not ask for user_id; authentication is handled by the backend.
""")

    response = await leave_llm.ainvoke(
        [system_message, *state["messages"]]
    )
    return {"messages": [response]}


tool_node = ToolNode(tools=leave_tools)

builder = StateGraph(
    state_schema=LeaveState,
    context_schema=AiContext,
)
builder.add_node("leave_agent", leave_agent)
builder.add_node("tool_node", tool_node)
builder.add_edge(START, "leave_agent")
builder.add_conditional_edges(
    "leave_agent",
    tools_condition,
    {"tools": "tool_node", "__end__": END},
)
builder.add_edge("tool_node", "leave_agent")

leave_workflow = builder.compile()
