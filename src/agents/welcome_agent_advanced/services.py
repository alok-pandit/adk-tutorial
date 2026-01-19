from pathlib import Path
from google.adk.cli.service_registry import get_service_registry
from google.adk.sessions.database_session_service import DatabaseSessionService

def custom_session_factory(uri: str, **kwargs):
    """
    Custom session factory that redirects sqlite requests to the agent's 
    local directory.
    """
    # URI format: agentdb://{agent_name}
    agent_name = uri.replace("agentdb://", "")
    
    # This file is located at src/agents/{agent_name}/services.py
    # So the agent folder is the parent of this file.
    agent_dir = Path(__file__).parent.resolve()
    
    # If we are in the correct folder, use it. 
    # Otherwise, we might be loaded from a parent directory (like in adk web).
    if agent_dir.name != agent_name:
        # Try to find the sibling folder
        potential_path = agent_dir / agent_name / f"{agent_name}.db"
    else:
        potential_path = agent_dir / f"{agent_name}.db"
    
    db_url = f"sqlite+aiosqlite:////{potential_path}"
    
    print(f"SERVICES.PY: Routing {uri} to {db_url}")
    
    return DatabaseSessionService(db_url=db_url)

# Register the 'agentdb' scheme
get_service_registry().register_session_service("agentdb", custom_session_factory)
