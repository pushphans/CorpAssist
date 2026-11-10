from corpassist.core.config import settings
from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model="qwen/qwen3.8-27b",
    model_provider="groq",
    api_key=settings.GROQ_API_KEY
)