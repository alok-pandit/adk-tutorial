"""Shared State feature."""

from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from fastapi import FastAPI
from .agent import root_agent as proverbs_agent


# Create ADK middleware agent instance
adk_proverbs_agent = ADKAgent(
    adk_agent=proverbs_agent,
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Proverbs Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_proverbs_agent, path="/")

if __name__ == "__main__":
    import os

    import uvicorn

    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set!")
        print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        print("   Get a key from: https://makersuite.google.com/app/apikey")
        print()

    port = int(os.getenv("WEATHER_AGENT_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
