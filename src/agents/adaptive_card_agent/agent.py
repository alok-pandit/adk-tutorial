import logging
import json
from typing import Dict, Any

from google.adk.agents import Agent
from google.adk.tools import ToolContext
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path

# Get the directory of the current file
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
MCP_SERVER_SCRIPT = PROJECT_ROOT / "src" / "mcp_server" / "adaptive_card_server.py"

logger = logging.getLogger(__name__)

async def generate_adaptive_card(tool_context: ToolContext, template: str, data_json: str) -> str:
    """
    Generates an Adaptive Card using the specified template and data.
    
    Args:
        template: The template type ('hero', 'alert', 'data_summary', 'form', 'list', 'simple').
        data_json: A JSON string containing the data for the card.
    """
    
    # Connect to MCP server to generate card
    server_params = StdioServerParameters(
        command="python3",
        args=[str(MCP_SERVER_SCRIPT)],
        env=None 
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.call_tool(
                    "generate_adaptive_card",
                    arguments={
                        "template": template,
                        "data": data_json
                    }
                )
                
                if result.content and hasattr(result.content[0], "text"):
                     return result.content[0].text
                else:
                    return "Error: Empty response from MCP server."

    except Exception as e:
        logger.error(f"Failed to communicate with MCP server: {e}")
        return f"Error creating card: {e}"

root_agent = Agent(
    name="adaptive_card_agent",
    description="An agent that generates Adaptive Cards based on user requests using an MCP server.",
    instruction="""
    You are an intelligent assistant capable of generating Adaptive Cards to present information rich responses.
    
    Your goal is to choose the most appropriate Adaptive Card template for the user's request and populate it with relevant data.
    
    AVAILABLE TEMPLATES:
    1. 'hero': Use for introductions, welcomes, or featuring a specific item. Needs 'title', 'description', 'imageUrl', 'url'.
    2. 'alert': Use for warnings, errors, notifications, or status updates. Needs 'severity' (low/medium/high), 'value', 'detail'.
    3. 'data_summary': Use for reports, statistics, or analytical data. Needs 'title', 'total', 'trend'.
    4. 'form': Use when you need to collect information or feedback from the user. Needs 'title'.
    5. 'list': Use for displaying a list of items, tasks, or options. Needs 'title', 'items' (list of objects with 'title', 'subtitle').
    6. 'simple': Use for basic text responses. Needs 'message'.
    7. 'flight_update': Use for flight status information. Needs 'flightNumber', 'status', 'gate', 'boardingTime'.
    8. 'weather': Use for weather forecasts. Needs 'city', 'temperature', 'condition', 'high', 'low'.
    9. 'stock_update': Use for stock market data. Needs 'symbol', 'price', 'change', 'changePoints'.
    10. 'calendar_invite': Use for meeting invites. Needs 'title', 'time', 'location', 'organizer', 'description'.
    11. 'restaurant_details': Use for restaurant recommendations/details. Needs 'name', 'rating', 'cuisine', 'price', 'address', 'imageUrl'.
    
    INSTRUCTIONS:
    - When the user asks a question or gives a command, analyze the intent.
    - Select the best template from the list above.
    - Construct a JSON string representing the data for that template.
    - Call the `generate_adaptive_card` tool with the template name and the JSON string.
    - Return the resulting Adaptive Card JSON only and no other commentary to the user.
    - No need to write "The Adaptive Card for the system alert is displayed below:" or any other text in the response. Just return the adaptive card JSON only.
    
    EXAMPLES:
    - User: "Show me the sales report" -> Use 'data_summary' template with sales data.
    - User: "I want to give feedback" -> Use 'form' template.
    - User: "System is overheating!" -> Use 'alert' template with 'high' severity.
    - User: "What are my tasks?" -> Use 'list' template with task items.
    - User: "Is flight UA123 on time?" -> Use 'flight_update' template.
    - User: "What's the weather in NY?" -> Use 'weather' template.
    - User: "How is MSFT doing?" -> Use 'stock_update' template.
    - User: "Schedule a meeting" -> Use 'calendar_invite' template.
    - User: "Find a good Italian place" -> Use 'restaurant_details' template.
    """,
    tools=[generate_adaptive_card],
)
