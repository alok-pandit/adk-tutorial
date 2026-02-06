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
    
    user_id = f"lib_test_user_{i}"
    session_id = f"lib_test_session_{i}"
    
    await session_service.create_session(user_id=user_id, session_id=session_id, app_name="adaptive_card_agent")
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    ):
        pass 

async def main():
    print("Running Expanded Adaptive Card Library Verification...")
    
    prompts = [
        "What is the status of flight UA123?",
        "What is the weather like in Seattle?",
        "Show me the stock price for GOOGL.",
        "Create a calendar invite for the team sync at 10am tomorrow.",
        "Recommend a good sushi restaurant nearby."
    ]
    
    for i, prompt in enumerate(prompts):
        await run_prompt(prompt, i)

if __name__ == "__main__":
    asyncio.run(main())
