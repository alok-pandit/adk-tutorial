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

class MathStep(BaseModel):
    """An individual step in a mathematical calculation."""
    description: str = Field(description="A clear description of the operation (e.g., 'Added 2 to 3')")
    result: float = Field(description="The numeric result of this specific operation")

class CalculationResult(BaseModel):
    """The result of a mathematical calculation."""
    steps: list[MathStep] = Field(description="A sequential list of EVERY calculation step performed using tools.")
    final_result: float = Field(description="The final numerical result, which MUST match the result of the last step in your list exactly.")