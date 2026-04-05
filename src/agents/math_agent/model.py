from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field

model=LiteLlm(
        model="ollama/gemma4:31b",
        temperature=0.0,
        extra_body={
            "skip_special_tokens": False,
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        },
    )

class CalculationResult(BaseModel):
    """The result of a mathematical calculation."""
    result: float = Field(description="The numeric result of the calculation")
    explanation: str = Field(description="A brief explanation for the user")    