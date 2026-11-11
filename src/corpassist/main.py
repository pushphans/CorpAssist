from corpassist.tickets.router.ticket_router import ticket_router
from corpassist.auth.router.auth_router import auth_router
from corpassist.leaves.router.leave_router import leave_router
from corpassist.ai.router.ai_router import ai_router
from fastapi import FastAPI
from fastapi import Request
from starlette.responses import JSONResponse
from corpassist.auth.utils.current_user_utils import InvalidTokenError
from corpassist.auth.utils.current_user_utils import InvalidCredentialError

app = FastAPI()


async def auth_exception_handler(
    request: Request,
    exc: InvalidTokenError | InvalidCredentialError
):
    return JSONResponse(
        status_code=401,
        content={"detail": "Unauthorized"}
    )


app.add_exception_handler(InvalidTokenError, auth_exception_handler)
app.add_exception_handler(InvalidCredentialError, auth_exception_handler)


app.include_router(auth_router)
app.include_router(ticket_router)
app.include_router(leave_router)
app.include_router(ai_router)

@app.get("/")
def health_check():
    return {
        "status" : "ok"
    }
