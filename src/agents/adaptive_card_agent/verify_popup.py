import asyncio
import logging
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from src.agents.adaptive_card_agent.agent import root_agent

logging.basicConfig(level=logging.INFO)

async def run_prompt(prompt: str, i: int):
    print(f"\n=== Test {i+1}: '{prompt}' ===")
    
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="adaptive_card_agent",
        agent=root_agent,
        session_service=session_service
    )
    
    user_id = f"popup_test_user_{i}"
    session_id = f"popup_test_session_{i}"
    
    await session_service.create_session(user_id=user_id, session_id=session_id, app_name="adaptive_card_agent")
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    ):
        if hasattr(event, "text") and event.text:
             print(f"Response: {event.text}") 

async def main():
    print("Running Popup Action Verification...")
    
    prompts = [
        "Open the calendar for me.",
        "I need to select a city from the list.",
        "Can you show me the checklist?"
    ]
    
    for i, prompt in enumerate(prompts):
        await run_prompt(prompt, i)

if __name__ == "__main__":
    asyncio.run(main())
