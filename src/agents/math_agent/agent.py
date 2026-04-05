from google.adk.agents import Agent
from .instructions import instruction, description
from .model import model, CalculationResult
from .tools import add, subtract, multiply, divide

root_agent = Agent(
    name="math_agent",
    model=model,
    description=description,
    instruction=instruction,
    tools=[add, subtract, multiply, divide],
    output_schema=CalculationResult,
)
