from pathlib import Path
from typing import Any, Dict
from google.adk.sessions import DatabaseSessionService


def get_current_dir(file_path: str) -> Path:
    """Returns the absolute parent directory of the provided file path."""
    return Path(file_path).parent.resolve()


async def create_session_with_state(
    session_service: DatabaseSessionService,
    app_name: str,
    user_id: str,
    username: str = "Alok",
) -> str:
    """Creates a session with pre-populated state including the username.

    Args:
        session_service: The DatabaseSessionService instance
        app_name: The name of the application
        user_id: The unique user identifier
        username: The username to include in state (default: "Alok")

    Returns:
        The session ID of the created session
    """
    state: Dict[str, Any] = {"username": username}
    session = await session_service.create_session(
        app_name=app_name, user_id=user_id, state=state
    )
    return session.id
