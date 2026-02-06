from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from fastapi import FastAPI

from .agent import root_agent as math_agent

adk_math_agent = ADKAgent(
    adk_agent=math_agent,
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

app = FastAPI(title="ADK Middleware Math Agent")

add_adk_fastapi_endpoint(app, adk_math_agent, path="/")

if __name__ == "__main__":
    import os

    import uvicorn

    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set!")
        print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        print("   Get a key from: https://makersuite.google.com/app/apikey")
        print()

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("MATH_AGENT_PORT", 8001)))
