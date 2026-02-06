# import asyncio
# import logging
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types
# from src.agents.adaptive_card_agent.agent import root_agent

# logging.basicConfig(level=logging.INFO)

# async def run_prompt(prompt: str, i: int):
#     print(f"\n=== Test {i+1}: '{prompt}' ===")
    
#     session_service = InMemorySessionService()
#     runner = Runner(
#         app_name="adaptive_card_agent",
#         agent=root_agent,
#         session_service=session_service
#     )
    
#     user_id = f"test_user_{i}"
#     session_id = f"test_session_{i}"
    
#     await session_service.create_session(user_id=user_id, session_id=session_id, app_name="adaptive_card_agent")
    
#     message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
#     async for event in runner.run_async(
#         user_id=user_id,
#         session_id=session_id,
#         new_message=message
#     ):
#         pass 

# async def main():
#     print("Running Autonomous Adaptive Card Agent Verification...")
    
#     prompts = [
#         "Hi there! Who are you?",
#         "Show me a sales report for Q1.",
#         "CRITICAL: The server is on fire!",
#         "I need to submit some feedback.",
#         "What are my top 3 tasks for today?"
#     ]
    
#     for i, prompt in enumerate(prompts):
#         await run_prompt(prompt, i)

# if __name__ == "__main__":
#     asyncio.run(main())
"""Shared State feature."""

from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from fastapi import FastAPI
from .agent import root_agent as adaptive_card_agent


# Create ADK middleware agent instance
adk_adaptive_card_agent = ADKAgent(
    adk_agent=adaptive_card_agent,
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Adaptive Card Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_adaptive_card_agent, path="/")

if __name__ == "__main__":
    import os

    import uvicorn

    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set!")
        print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        print("   Get a key from: https://makersuite.google.com/app/apikey")
        print()

    port = int(os.getenv("ADAPTIVE_CARD_AGENT_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
