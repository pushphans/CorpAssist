import uuid

from langchain.messages import HumanMessage

from corpassist.ai.core.llm_utils import AiContext
from corpassist.ai.core.state import SupervisorState
from corpassist.ai.supervisor_workflow.supervisor_workflow import (
    supervisor_workflow,
)


async def run_ai_workflow(
    user_id: uuid.UUID,
    message: str,
) -> SupervisorState:
    """Run the AI workflow for an authenticated user and return updated state.

    Each invocation starts with only the current message and no prior history.
    Workflow errors propagate to the caller for HTTP-level handling.
    """
    message = message.strip()
    if not message:
        raise ValueError("Message must not be empty.")

    messages = [HumanMessage(content=message)]
    return await supervisor_workflow.ainvoke(
        {"messages": messages},
        context=AiContext(user_id=user_id),
    )
