import logging
from datetime import date
from typing import Optional
from google.adk.agents import Agent
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.adk.tools import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from ..path_setup import resolve_agent_reference

resolve_agent_reference(__file__)
from src.utils.file_tools import get_current_dir

logger = logging.getLogger(__name__)
DIR = get_current_dir(__file__)
db_path = DIR / "pto_agent.db"
db_url = f"sqlite+aiosqlite:////{db_path}"


def open_calendar_for_selection(tool_context: ToolContext) -> str:
    """Action: Opens the calendar component for the user to select a date range for their leave."""
    tool_confirmation = tool_context.tool_confirmation
    if not tool_confirmation:
        tool_context.request_confirmation(
            hint="Please select your leave dates using the calendar.",
            payload={}
        )
        return "I've opened the calendar for you. Please select the dates and click apply."
    
    # Returning the payload back to the agent so it knows the dates
    return str(tool_confirmation.payload)


def request_user_approval(
    start_date: str, end_date: str, tool_context: ToolContext, reason: Optional[str] = None
) -> str:
    """Action: Requests approval from the user for the leave request details before submitting to the manager."""
    tool_confirmation = tool_context.tool_confirmation
    if not tool_confirmation:
        tool_context.request_confirmation(
            hint="Please approve or cancel the leave request.",
            payload={"start_date": start_date, "end_date": end_date, "reason": reason}
        )
        return "Please confirm the details on the card shown above."
    
    # Return the user's decision
    return str(tool_confirmation.payload)


def submit_to_manager(
    start_date: str, end_date: str, reason: Optional[str] = None
) -> str:
    """Submits the leave request with the selected dates to the manager for approval."""
    return f"Your leave request from {start_date} to {end_date} has been submitted to your manager for approval."


def get_instructions(context: ReadonlyContext) -> str:
    """Returns the agent instructions."""
    return (
        "You are a helpful PTO leave assistant.\n\n"
        "WORKFLOW:\n"
        "1. When an employee asks for leave, ALWAYS use 'open_calendar_for_selection' first to prompt them for dates.\n"
        "2. Once the user selects the dates via the calendar, verify the dates and then ASK the user for the reason for their leave in the chat.\n"
        "3. Once the reason is provided, use 'request_user_approval' to show them the confirmation card with the dates and the reason.\n"
        "4. IF AND ONLY IF the user approves (the tool returns 'Approved'), then use 'submit_to_manager' to process the request.\n"
        "5. If the user cancels or says no, acknowledge it and do NOT submit.\n"
        "6. Confirm submission to the user once 'submit_to_manager' is called."
    )


async def log_startup(callback_context: CallbackContext):
    """Lifecycle hook to log agent startup information."""
    logger.info("🚀 PTO AGENT STARTING!")
    return None


root_agent = Agent(
    name="PTO_agent",
    description="PTO/leave approval agent with automatic calendar selection and manager submission.",
    instruction=get_instructions,
    tools=[open_calendar_for_selection, request_user_approval, submit_to_manager],
    before_agent_callback=log_startup,
)

# session_service = DatabaseSessionService(db_url=db_url)
# runner = Runner(app_name="pto_agent", agent=root_agent, session_service=session_service)
