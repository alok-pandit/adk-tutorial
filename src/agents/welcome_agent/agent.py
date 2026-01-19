from google.adk.agents import Agent
from google.adk.tools.google_search_tool import google_search


root_agent = Agent(
    name="welcome_agent",
    description="A helpful assistant for user questions.",
    instruction="Answer user questions to the best of your knowledge. You have access to Google search to find up-to-date information when needed.",
    tools=[google_search],
)
