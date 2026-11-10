import os

from langchain_groq import ChatGroq

DEFAULT_LLM_MODEL = "llama-3.3-70b-versatile"


def get_llm(
    model: str = DEFAULT_LLM_MODEL,
    temperature: float = 0.1,
) -> ChatGroq:
    if os.getenv("GROQ_API_KEY") is None:
        raise RuntimeError("GROQ_API_KEY environment variable is not set")

    return ChatGroq(model=model, temperature=temperature)
