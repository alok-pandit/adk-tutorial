import logging
import json
from typing import Any, Dict

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path

# Import sub-agent tools
from .sub_agents import (
    get_hero_content,
    get_system_alert,
    get_data_report,
    get_feedback_form,
    get_task_list,
    get_simple_message,
    get_flight_status,
    get_weather_forecast,
    get_stock_quote,
    get_calendar_event,
    get_restaurant_recommendation,
    get_popup_tools,
)

# Metadata for type checking (optional but helpful for reference)
from .models import DynamicFormData, FormField, FormOption

# Get the directory of the current file
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
MCP_SERVER_SCRIPT = PROJECT_ROOT / "src" / "mcp_server" / "adaptive_card_server.py"

logger = logging.getLogger(__name__)


def _build_fallback_card(message: str, template: str, data_json: str) -> str:
    """
    Build a minimal Adaptive Card JSON that conveys an error but adheres to the contract
    of returning only Adaptive Card JSON.
    """
    card = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "body": [
            {"type": "TextBlock", "text": "Adaptive Card Generation Error", "weight": "Bolder", "size": "Medium"},
            {"type": "TextBlock", "text": message, "wrap": True}
        ],
        "actions": [
            {"type": "Action.Submit", "title": "Retry", "data": {"action": "retry", "template": template, "originalData": data_json}}
        ]
    }
    return json.dumps(card)


async def generate_dynamic_form_card(
    data: Any
) -> str:
    """
    Generates an Adaptive Card for a custom dynamic form.
    Use this for requests involving specific fields, date ranges, or custom inputs.
    """
    logger.info(f"Generating dynamic form with data type: {type(data)}")
    
    # Ensure data is a JSON string
    if isinstance(data, (dict, list)):
        data_json = json.dumps(data)
    else:
        data_json = str(data)
        
    return await generate_adaptive_card(template="dynamic_form", data=data_json)


async def generate_adaptive_card(
    template: str, data: Any
) -> str:
    """
    Generates an Adaptive Card using the specified template and data.

    Args:
        template: The template type (e.g., 'hero', 'alert', 'flight_update').
        data: The data for the card, as a JSON string or a dictionary.
    """
    # Ensure data is a JSON string for the MCP call
    if isinstance(data, (dict, list)):
        data_json = json.dumps(data)
    else:
        data_json = str(data)

    logger.info(f"Generating adaptive card: template={template}, data_len={len(data_json)}")

    # Connect to MCP server to generate card
    server_params = StdioServerParameters(
        command="python3", args=[str(MCP_SERVER_SCRIPT)], env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    "generate_adaptive_card",
                    arguments={"template": template, "data": data_json},
                )

                if result.content and hasattr(result.content[0], "text"):
                    text = result.content[0].text  # type: ignore
                    if isinstance(text, str) and text.strip():
                        return text
                    else:
                        return _build_fallback_card("Empty response from MCP server.", template, data_json)
                else:
                    return _build_fallback_card("Empty response from MCP server.", template, data_json)

    except Exception as e:
        logger.error(f"Failed to communicate with MCP server: {e}")
        return _build_fallback_card(f"Error creating card: {e}", template, data_json)


root_agent = Agent(
    name="adaptive_card_agent",
    description="An agent that creates Adaptive Cards by first fetching valid data from sub-agents.",
    instruction="""
    You are an intelligent assistant that generates Adaptive Cards.
    
    PROCESS:
    1.  Analyze the user's request.
    2.  If it's a CUSTOM/DYNAMIC request (specific fields like dropdowns, selectors, date ranges), you MUST construct the data and call `generate_dynamic_form_card(data=...)`.
    3.  Otherwise, call a "Sub-Agent" tool and pass its result to `generate_adaptive_card(template=..., data=...)`.
    
    CRITICAL RULES:
    4.  TOOL CALLING: When you call a tool, do NOT include ANY text, pleasantries, or descriptions. ONLY provide the tool call.
    5.  RESPONSE: You must return the RAW JSON string exactly as returned by the tool. Do NOT add conversational text or wrap it.
    6.  ONLY VALID JSON: Your entire output must be a single Adaptive Card JSON string.
    7.  NEVER return Markdown code blocks (e.g., no ```json). Return the raw text.
    8.  NEVER wrap the output in objects like `{"result": ...}`.
    
    DYNAMIC FORM SCHEMA:
    {
      "title": "String",
      "instructions": "Helpful text",
      "fields": [
        {
          "id": "unique_string",
          "type": "text | date | number | choice | checkbox",
          "label": "Display Label",
          "placeholder": "Optional text",
          "isRequired": boolean,
          "options": [{"title": "Label", "value": "val"}], (Required for choice/checkbox)
          "isMultiSelect": boolean (Optional for choice)
        }
      ]
    }

    SCENARIO MAPPING:
    - Custom Form Fields/Date Ranges -> `generate_dynamic_form_card(data=...)`
    - 'hero' -> `get_hero_content(topic)`
    - 'alert' -> `get_system_alert(component)`
    - 'data_summary' -> `get_data_report(report_type)`
    - 'form' -> `get_feedback_form(context)` (Use ONLY for generic "I want to give feedback")
    - 'list' -> `get_task_list(user)`
    - 'simple' -> `get_simple_message(text)`
    - 'flight_update' -> `get_flight_status(flight_number)`
    - 'weather' -> `get_weather_forecast(city)`
    - 'stock_update' -> `get_stock_quote(symbol)`
    - 'calendar_invite' -> `get_calendar_event(event_type)`
    - 'restaurant_details' -> `get_restaurant_recommendation(cuisine)`
    - 'popup' -> `get_popup_tools(tool_type)`
    
    EXAMPLES:
    - User: "I need to provide feedback with a date range, severity checkbox (low to high), and city dropdown."
      1. Call `generate_dynamic_form_card` with the following `data`:
         {
           "title": "Detailed Feedback",
           "fields": [
             {"id": "start_date", "type": "date", "label": "Start Date", "isRequired": true},
             {"id": "end_date", "type": "date", "label": "End Date", "isRequired": true},
             {"id": "severity", "type": "checkbox", "label": "Severity Level", "options": [{"title": "Low", "value": "low"}, {"title": "Medium", "value": "med"}, {"title": "High", "value": "high"}]},
             {"id": "city", "type": "choice", "label": "Select City", "options": [{"title": "Seattle", "value": "sea"}, {"title": "New York", "value": "nyc"}]}
           ]
         }
      2. Return only the raw string from the tool.

    - User: "I want to give feedback"
      1. data = `get_feedback_form(context="general")`
      2. Call `generate_adaptive_card(template="form", data=data)`
      3. Return only the raw string from the tool.

    - User: "What are my tasks?"
      1. Call `get_task_list("user")` -> Returns ListData(...)
      2. Call `generate_adaptive_card("list", json_string_of_data)`
    """,
    tools=[
        generate_dynamic_form_card,
        generate_adaptive_card,
        get_hero_content,
        get_system_alert,
        get_data_report,
        get_feedback_form,
        get_task_list,
        get_simple_message,
        get_flight_status,
        get_weather_forecast,
        get_stock_quote,
        get_calendar_event,
        get_restaurant_recommendation,
        get_popup_tools,
    ],
)
