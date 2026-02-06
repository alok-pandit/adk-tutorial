import logging
import json
from typing import Dict, Any

from google.adk.agents import Agent
from google.adk.tools import ToolContext
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path

# Import strict data models (indirectly used via tools, but good for type safety if needed)
from .models import (
    HeroData, AlertData, DataSummaryData, FormData,
    ListData, SimpleData, FlightUpdateData, WeatherData,
    StockUpdateData, CalendarInviteData, RestaurantDetailsData
)

# Import sub-agent tools
from .sub_agents import (
    get_hero_content, get_system_alert, get_sales_report, get_feedback_form,
    get_task_list, get_simple_message, get_flight_status, get_weather_forecast,
    get_stock_quote, get_calendar_event, get_restaurant_recommendation
)

# Get the directory of the current file
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
MCP_SERVER_SCRIPT = PROJECT_ROOT / "src" / "mcp_server" / "adaptive_card_server.py"

logger = logging.getLogger(__name__)

async def generate_adaptive_card(tool_context: ToolContext, template: str, data_json: str) -> str:
    """
    Generates an Adaptive Card using the specified template and data.
    
    Args:
        template: The template type (e.g., 'hero', 'alert', 'flight_update').
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
    description="An agent that creates Adaptive Cards by first fetching valid data from sub-agents.",
    instruction="""
    You are an intelligent assistant that generates Adaptive Cards.
    
    PROCESS:
    1.  Analyze the user's request to determine the correct scenario.
    2.  If NO specific scenario matches, use the 'simple' sub-agent (`get_simple_message`).
    3.  Call the appropriate "Sub-Agent" tool to get the data.
    4.  The tool will return a structure (JSON-compatible).
    5.  Convert that structure to a JSON string.
    6.  Call `generate_adaptive_card` with the corresponding template name and the JSON string.
    7.  You must ONLY return a valid Adaptive Card JSON string.
    8.  NEVER return plain text, markdown, or conversational filler (e.g., "Here is the card").
    
    CRITICAL OUTPUT RULE:
    - Your final response must start with `{` and end with `}`.
    - Do not wrap it in markdown code blocks (like `json ... `).
    - Just raw JSON string.

    SCENARIO MAPPING (Template -> Tool):
    - 'hero' -> `get_hero_content(topic)`
    - 'alert' -> `get_system_alert(component)`
    - 'data_summary' -> `get_sales_report(quarter)`
    - 'form' -> `get_feedback_form(context)`
    - 'list' -> `get_task_list(user)`
    - 'simple' -> `get_simple_message(text)`
    - 'flight_update' -> `get_flight_status(flight_number)`
    - 'weather' -> `get_weather_forecast(city)`
    - 'stock_update' -> `get_stock_quote(symbol)`
    - 'calendar_invite' -> `get_calendar_event(event_type)`
    - 'restaurant_details' -> `get_restaurant_recommendation(cuisine)`
    
    EXAMPLES:
    - User: "Check flight UA123"
      1. Call `get_flight_status("UA123")` -> Returns FlightUpdateData(...)
      2. Call `generate_adaptive_card("flight_update", json_string_of_data)`
    
    - User: "Stock price for AAPL"
      1. Call `get_stock_quote("AAPL")` -> Returns StockUpdateData(...)
      2. Call `generate_adaptive_card("stock_update", json_string_of_data)`
    """,
    tools=[
        generate_adaptive_card,
        get_hero_content, get_system_alert, get_sales_report, get_feedback_form,
        get_task_list, get_simple_message, get_flight_status, get_weather_forecast,
        get_stock_quote, get_calendar_event, get_restaurant_recommendation
    ],
)
