import json
import logging
import uuid
from typing import Any, Dict

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.genai import types
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

# Persistent store for form definitions (In-memory for this tutorial)
FORM_STORE: Dict[str, Any] = {}


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
    # Generate unique ID and store definition for validation
    form_id = str(uuid.uuid4())
    
    # Ensure data is a dict for injecting form_id
    if hasattr(data, "model_dump"):
        data_dict = data.model_dump()
    elif isinstance(data, dict):
        data_dict = data
    else:
        try:
            data_dict = json.loads(str(data))
        except:
            data_dict = {"title": "Form", "fields": []}
            
    data_dict["form_id"] = form_id
    FORM_STORE[form_id] = data_dict
    logger.info(f"Stored form {form_id} in FORM_STORE")
    
    return await generate_adaptive_card(template="dynamic_form", data=data_dict)


async def validate_form_submission(
    submission_data: Any
) -> str:
    """
    Validates a form submission against its stored definition.
    Use this when you receive a message containing "action": "submit_dynamic_form".
    
    Args:
        submission_data: The key-value pairs from the form submission.
    """
    logger.info(f"Validating submission: {submission_data}")
    
    # Handle cases where submission_data is passed as a string/json
    if isinstance(submission_data, str):
        try:
            submission_data = json.loads(submission_data)
        except:
            pass

    # Ensure submission_data is a dictionary
    if not isinstance(submission_data, dict):
        logger.warning(f"Submission data is not a dict: {type(submission_data)}")
        return await generate_adaptive_card(
            template="simple", 
            data={"message": "Error: Invalid submission data received."}
        )

    form_id = submission_data.get("form_id")
    if not form_id or form_id not in FORM_STORE:
        logger.error(f"Form ID '{form_id}' not found in FORM_STORE")
        return await generate_adaptive_card(
            template="simple", 
            data={"message": f"Error: Form session '{form_id}' not found or expired."}
        )
    
    definition = FORM_STORE[form_id]
    fields = definition.get("fields", [])
    errors = []
    
    for field in fields:
        fid = field.get("id")
        label = field.get("label", fid)
        val = submission_data.get(fid)
        
        if field.get("isRequired") and (val is None or val == ""):
            errors.append(f"- {label} is required.")
            
    if errors:
        error_msg = "Validation Failed:\n" + "\n".join(errors)
        return await generate_adaptive_card(
            template="simple",
            data={"message": error_msg}
        )
    
    success_msg = f"Success! Your submission for '{definition.get('title')}' has been validated."
    return await generate_adaptive_card(
        template="simple",
        data={"message": success_msg}
    )


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


async def repair_llm_request_callback(
    callback_context: CallbackContext, 
    llm_request: Any # LlmRequest
):
    """
    Final-stage repair callback to fix Gemini 'INVALID_ARGUMENT' errors.
    Iterates through the request contents and ensures every user turn has a non-null text part.
    We are careful to only add/modify text if there is no other data in the Part (oneof field).
    """
    if not llm_request or not llm_request.contents:
        return None

    repaired = False
    for content in llm_request.contents:
        if content.role == "user":
            # Check if this turn is completely empty (no text and no other data in any part)
            is_empty_turn = True
            if content.parts:
                for part in content.parts:
                    # Check for any field that satisfies Gemini's requirement for a part
                    if (getattr(part, 'text', None) or 
                        getattr(part, 'inline_data', None) or 
                        getattr(part, 'function_response', None) or
                        getattr(part, 'file_data', None)):
                        is_empty_turn = False
                        break
            else:
                is_empty_turn = True # No parts at all is definitely empty
            
            if is_empty_turn:
                logger.info("Repaired empty user turn in LlmRequest for Gemini turn order.")
                if content.parts:
                    # Set text on the first part ONLY if it has no other data (oneof collision check)
                    part = content.parts[0]
                    # Since is_empty_turn is true, no field is set, so setting text is safe
                    part.text = "submit_dynamic_form"
                else:
                    content.parts.append(types.Part(text="submit_dynamic_form"))
                repaired = True
    
    if repaired:
        logger.info("Successfully repaired LlmRequest contents.")
    
    return None


root_agent = Agent(
    name="adaptive_card_agent",
    description="An agent that creates Adaptive Cards by first fetching valid data from sub-agents.",
    instruction="""
    You are an expert at generating Adaptive Card JSON.
    
    CRITICAL: YOU MUST ONLY RETURN THE RAW JSON STRING AS YOUR FINAL RESPONSE.
    NEVER include conversational text, markdown code blocks (```json), or explanations.

    ### PROCESS
    1. Determine if the user is SUBMITTING a form or REQUESTING a new card.
    2. If SUBMITTING (input contains `action: "submit_dynamic_form"` OR text is "submit_dynamic_form"):
       - You must call `validate_form_submission(submission_data=...)`.
       - If the input is just the string "submit_dynamic_form", look through the conversation history or session state for the most recent form data if possible, or request the user to provide the fields.
       - Usually, the entire card data is passed in the tool call.
    3. If REQUESTING (fetching data/generating new card):
       - Determine if a specific data tool matches (flight, weather, etc.).
       - If it matches, call the data tool and pass result to `generate_adaptive_card(template=..., data=...)`.
       - If the user wants a CUSTOM form, call `generate_dynamic_form_card(data=...)`.
       - Otherwise, use `get_simple_message` -> `generate_adaptive_card(template="simple", data=...)`.
    4. RETURN THE RAW RESULT OF THE GENERATION TOOL DIRECTLY. DO NOT WRAP IT.

    ### TOOLS
    - DATA TOOLS: get_hero_content, get_system_alert, get_feedback_form, get_task_list, get_simple_message, get_flight_status, get_weather_forecast, get_stock_quote, get_calendar_event, get_restaurant_recommendation.
    - VALIDATION TOOLS:
        - `validate_form_submission(submission_data)`: Validates form results.
    - GENERATION TOOLS: 
        - `generate_adaptive_card(template, data)`: For standard templates.
        - `generate_dynamic_form_card(data)`: For custom forms (generates a form_id).

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
        validate_form_submission,
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
    before_model_callback=repair_llm_request_callback,
)
