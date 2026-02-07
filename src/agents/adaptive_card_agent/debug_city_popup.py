import asyncio
import logging
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from src.agents.adaptive_card_agent.agent import root_agent

logging.basicConfig(level=logging.INFO)

async def main():
    print("Debugging City Popup Trigger...")
    
    prompt = "Open the city selector."
    print(f"\n=== Test: '{prompt}' ===")
    
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="adaptive_card_agent",
        agent=root_agent,
        session_service=session_service
    )
    
    user_id = "debug_user"
    session_id = "debug_session"
    
    await session_service.create_session(user_id=user_id, session_id=session_id, app_name="adaptive_card_agent")
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    ):
        print(f"Event: {type(event)}")
        if hasattr(event, "tool_calls"):
             for tool_call in event.tool_calls:
                 print(f"Tool Call: {tool_call.name} -> {tool_call.args}")
        if hasattr(event, "text"):
             print(f"Response: {event.text}") 

if __name__ == "__main__":
    asyncio.run(main())
