from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide the first number by the second. Returns None if division by zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


root_agent = Agent(
    name="math_agent",
    description="A math agent that can perform basic arithmetic operations: addition, subtraction, multiplication, and division.",
    instruction="You are a math assistant that helps users perform basic arithmetic operations. Use the appropriate tool based on the operation requested:\n- For addition, use the add tool\n- For subtraction, use the subtract tool\n- For multiplication, use the multiply tool\n- For division, use the divide tool\n\nProvide clear, concise answers with the result of the calculation.",
    tools=[add, subtract, multiply, divide],
)
