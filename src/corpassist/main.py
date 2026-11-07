from corpassist.auth.router.auth_router import auth_router
from fastapi import FastAPI

app = FastAPI()


app.include_router(auth_router)

@app.get("/")
def health_check():
    return {
        "status" : "ok"
    }