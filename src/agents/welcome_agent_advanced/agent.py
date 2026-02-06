import logging
from google.adk.agents import Agent
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from path_setup import resolve_agent_reference

resolve_agent_reference(__file__)

from src.utils.file_tools import get_current_dir

logger = logging.getLogger(__name__)

DIR = get_current_dir(__file__)

# Four slashes for absolute path: sqlite+aiosqlite:////home/user/...
db_path = DIR / "welcome_agent_advanced.db"
db_url = f"sqlite+aiosqlite:///{db_path}"
if not db_url.startswith("sqlite+aiosqlite:////"):
    db_url = db_url.replace("sqlite+aiosqlite:///", "sqlite+aiosqlite:////")


async def log_startup(callback_context: CallbackContext):
    """Lifecycle hook to log agent startup information."""
    logger.info("🚀 AGENT STARTING!")
    logger.info(f"📂 DIR: {DIR}")
    logger.info(f"🗄️ CONFIGURED DB URL: {db_url}")
    return None  # Return None to continue normal agent execution


def get_instructions(context: ReadonlyContext) -> str:
    """Returns the agent instructions with the user's name from state."""
    state = context.state
    username = state.get("username", "User")
    return f"Hello {username}! You are a helpful assistant. Answer user questions to the best of your knowledge."


root_agent = Agent(
    name="welcome_agent_advanced",
    description="A helpful assistant for user questions.",
    instruction=get_instructions,
    before_agent_callback=log_startup,
)

session_service = DatabaseSessionService(db_url=db_url)

# This runner is for programmatic use.
# Note: 'adk web' currently creates its own runner using 'root_agent'
# and defaults to storing sessions in the .adk/ directory.
runner = Runner(
    app_name="welcome_agent_advanced",
    agent=root_agent,
    session_service=session_service,
)
