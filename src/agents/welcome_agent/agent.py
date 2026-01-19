import path_setup  # noqa: F401
from google.adk.agents import Agent
from src.utils.file_tools import get_current_dir

DIR = get_current_dir(__file__)


root_agent = Agent(
    name='welcome_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
