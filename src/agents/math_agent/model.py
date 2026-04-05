from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field

model=LiteLlm(
        model="ollama/gemma4:e4b",
        temperature=0.0,
        extra_body={
            "skip_special_tokens": True,
            "chat_template_kwargs": {
                "enable_thinking": True
            }
        },
    )

class CalculationResult(BaseModel):
    """The result of a mathematical calculation."""
    explanation: str = Field(description="A detailed, step-by-step explanation using Markdown bullet points.")
    result: float = Field(description="The final numerical result, which MUST match the last step in your explanation.")