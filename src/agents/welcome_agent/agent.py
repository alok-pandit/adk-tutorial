from google.adk.agents import Agent
from google.adk.tools.google_search_tool import google_search
from google.adk.models.lite_llm import LiteLlm

model = LiteLlm(
    # model="openrouter/openai/gpt-oss-20b:free",
    api_key="abcd1234",  # Replace with your actual API key
    model="ollama/magistral:24b",
    # api_key=os.getenv("OPENROUTER_API_KEY"),
    api_base="https://loyal-marginally-turtle.ngrok-free.app",
    # model="mistral/mistral-small-latest",
    # api_key="jkiO0qRkEWF5NWtFfSlGejn0hM79DGis",
)


def add(a: int, b: int) -> int:
    """A simple addition function."""
    return a + b


root_agent = Agent(
    name="welcome_agent",
    model=model,
    description="A helpful assistant for simple arithmetic operations.",
    instruction="You are a helpful assistant that can perform simple arithmetic operations. Use the add tool for addition. Provide only the final result in your response.",
    tools=[add],
)
