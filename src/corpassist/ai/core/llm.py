import os

from langchain_groq import ChatGroq

from corpassist.core.config import settings
from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model="qwen/qwen3.8-27b",
    model_provider="groq",
    api_key=settings.GROQ_API_KEY
)




intent_llm = init_chat_model(
    model="openai/gpt-oss-20b",
    model_provider="groq",
    api_key=settings.GROQ_API_KEY
)


DEFAULT_LLM_MODEL = "llama-3.3-70b-versatile"


def get_llm(
    model: str = DEFAULT_LLM_MODEL,
    temperature: float = 0.1,
) -> ChatGroq:
    if os.getenv("GROQ_API_KEY") is None:
        raise RuntimeError("GROQ_API_KEY environment variable is not set")

    return ChatGroq(model=model, temperature=temperature)
