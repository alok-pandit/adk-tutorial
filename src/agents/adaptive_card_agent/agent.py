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
    Use this when the user requests specific fields, date ranges, or custom inputs.
    
    Args:
        data: The form structure following the DynamicFormData schema.
    """
    return await generate_adaptive_card(template="dynamic_form", data=data)


async def generate_adaptive_card(
    template: str, data: Any
) -> str:
    """
    Generates an Adaptive Card for a specific template and data.

    Args:
        template: The template type ('hero', 'form', 'alert', 'dynamic_form', etc.).
        data: The data for the card (dict, string, or object from sub-agents).
    """
    # Robust serialization for all input types (JSON strings, dicts, Pydantic models)
    try:
        if isinstance(data, str):
            # Check if it's already a JSON string
            try:
                json.loads(data)
                serialized_data = data
            except json.JSONDecodeError:
                serialized_data = json.dumps(data)
        elif hasattr(data, "model_dump"):
            serialized_data = json.dumps(data.model_dump())
        elif isinstance(data, (dict, list)):
            serialized_data = json.dumps(data)
        else:
            serialized_data = str(data)
    except Exception as e:
        logger.error(f"Serialization failed: {e}")
        serialized_data = str(data)

    logger.info(f"Generating adaptive card: template={template}, data_len={len(serialized_data)}")

    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python3", args=[str(MCP_SERVER_SCRIPT)], env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    "generate_adaptive_card",
                    arguments={"template": template, "data": serialized_data},
                )

                if result.content and hasattr(result.content[0], "text"):
                    text = result.content[0].text  # type: ignore
                    return str(text)
                else:
                    return _build_fallback_card("No content returned from generator.", template, serialized_data)

    except Exception as e:
        logger.error(f"Generator tool failed: {e}")
        return _build_fallback_card(f"Error: {e}", template, serialized_data)


root_agent = Agent(
    name="adaptive_card_agent",
    description="An agent that creates Adaptive Cards by first fetching valid data from sub-agents.",
    instruction="""
    You are an expert at generating Adaptive Card JSON.
    
    CRITICAL: YOU MUST ONLY RETURN THE RAW JSON STRING AS YOUR FINAL RESPONSE.
    NEVER include conversational text, markdown code blocks (```json), or explanations.

    ### PROCESS
    1. Determine if a specific data tool matches the user's request (e.g., flight, weather, tasks).
    2. If it matches, call the data tool. Pass its result to `generate_adaptive_card(template=..., data=...)`.
    3. If the user wants a CUSTOM form with specific fields (dropdowns, date ranges, checkboxes), YOU MUST call `generate_dynamic_form_card(data=...)` with the requested structure.
    4. If no specific tools match, use `get_simple_message` and pass to `generate_adaptive_card(template="simple", data=...)`.
    5. RETURN THE RAW RESULT OF THE GENERATION TOOL DIRECTLY. DO NOT WRAP IT.

    ### TOOLS
    - DATA TOOLS: get_hero_content, get_system_alert, get_feedback_form, get_task_list, get_simple_message, get_flight_status, get_weather_forecast, get_stock_quote, get_calendar_event, get_restaurant_recommendation.
    - GENERATION TOOLS: 
        - `generate_adaptive_card(template, data)`: Use for 'hero', 'form', 'alert', 'list', 'simple', 'flight_update', 'weather', etc.
        - `generate_dynamic_form_card(data)`: Use for 'dynamic_form' with custom fields.

    ### DYNAMIC FORM DATA FORMAT
    Use this for `generate_dynamic_form_card`:
    {
      "title": "Title",
      "instructions": "Help text (optional)",
      "fields": [
        {
          "id": "id",
          "type": "text|date|number|choice|checkbox",
          "label": "Label",
          "isRequired": bool,
          "options": [{"title": "Label", "value": "val"}] (for choice/checkbox)
        }
      ]
    }

    ### FINAL OUTPUT RULES
    - YOUR ENTIRE RESPONSE MUST START WITH "{" AND END WITH "}".
    - NO PREAMBLE. NO POSTAMBLE. NO MARKDOWN BLOCKS.
    - Example of GOOD response: {"type": "AdaptiveCard", ...}
    - Example of BAD response: Here is the card: {"type": "AdaptiveCard", ...}
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
