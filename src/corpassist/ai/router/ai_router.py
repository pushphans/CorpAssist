import logging

from fastapi import APIRouter, Depends, HTTPException, status

from corpassist.ai.schema.ai_schema import AiRequestSchema, AiResponseSchema
from corpassist.ai.service.ai_service import run_ai_workflow
from corpassist.auth.model.user_model import UserModel
from corpassist.auth.utils.current_user_utils import get_user


logger = logging.getLogger(__name__)
ai_router = APIRouter(prefix="/ai", tags=["AI"])


@ai_router.post("/chat", response_model=AiResponseSchema)
async def execute_ai_workflow(
    data: AiRequestSchema,
    user: UserModel = Depends(get_user),
):
    try:
        result = await run_ai_workflow(user_id=user.id, message=data.message)
        return AiResponseSchema(message=result["messages"][-1].content)

    except Exception:
        logger.exception("AI workflow failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the AI request.",
        ) from None
