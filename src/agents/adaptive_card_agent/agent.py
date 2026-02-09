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
    Ensures every user turn has a valid part (text or function_response).
    Only appends a text part if the turn is effectively empty.
    """
    if not llm_request or not llm_request.contents:
        return None

    repaired = False
    for content in llm_request.contents:
        if content.role == "user":
            # A turn is valid if it has text OR data (function response, inline data, etc.)
            has_valid_content = any(
                getattr(part, 'text', None) is not None or
                getattr(part, 'function_response', None) is not None or
                getattr(part, 'inline_data', None) is not None or
                getattr(part, 'file_data', None) is not None
                for part in content.parts
            )
            
            if not has_valid_content:
                logger.info("Repaired empty user turn in LlmRequest by appending a text part.")
                content.parts.append(types.Part(text="submit_dynamic_form"))
                repaired = True
    
    if repaired:
        logger.info("Successfully repaired empty LlmRequest turns.")
    
    return None


root_agent = Agent(
    name="adaptive_card_agent",
    description="An agent that creates Adaptive Cards by first fetching valid data from sub-agents.",
    instruction="""
    You are an expert at generating Adaptive Card JSON by orchestrating sub-agent tools.
    
    CRITICAL: YOUR FINAL RESPONSE MUST ONLY BE THE RAW ADAPTIVE CARD JSON STRING.
    NEVER include conversational text, markdown blocks (```json), or explanations.

    ### WORKFLOWS
    1. IF THE USER IS SUBMITTING A FORM (identified by "action": "submit_dynamic_form" in data OR the text is "submit_dynamic_form"):
       - You MUST call `validate_form_submission(submission_data=...)`.
       - Pass the entire data object received from the submission.
       - RETURN THE RAW STRING RESULT OF THE TOOL.
    
    2. IF THE USER IS REQUESTING A CARD (feedback, weather, flight, stock, etc.):
       - Step A: Call the appropriate DATA TOOL (e.g., `get_feedback_form` for feedback, `get_weather_forecast` for weather).
       - Step B: Pass the RESULT of that data tool to `generate_adaptive_card(template=..., data=...)`.
       - RETURN THE RAW STRING RESULT OF THE GENERATION TOOL.
    
    3. IF THE USER WANTS A DYNAMIC/CUSTOM FORM:
       - Step A: Call `generate_dynamic_form_card(data=...)` with the requested fields.
       - RETURN THE RAW STRING RESULT OF THE TOOL.

    ### FINAL OUTPUT RULES
    - THE ENTIRE OUTPUT MUST BE VALID JSON STARTING WITH "{" AND ENDING WITH "}".
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
