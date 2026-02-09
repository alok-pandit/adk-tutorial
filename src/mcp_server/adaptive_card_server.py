from mcp.server.fastmcp import FastMCP
import json
from typing import Dict, Any, List

# Create an MCP server
mcp = FastMCP("Adaptive Card Generator")

def create_hero_card(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": f"{data.get('title', 'Hero Card')}. {data.get('description', 'Description goes here...')}",
        "body": [
            {
                "type": "Container",
                "items": [
                    {
                        "type": "Image",
                        "url": data.get("imageUrl", "https://picsum.photos/400/200"),
                        "size": "Stretch",
                        "altText": "Hero Image"
                    },
                    {
                        "type": "TextBlock",
                        "text": data.get("title", "Hero Card"),
                        "weight": "Bolder",
                        "size": "Large"
                    },
                    {
                        "type": "TextBlock",
                        "text": data.get("description", "Description goes here..."),
                        "wrap": True
                    }
                ]
            }
        ],
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "Learn More",
                "url": data.get("url", "https://adaptivecards.io")
            }
        ]
    }

def create_alert_card(data: Dict[str, Any]) -> Dict[str, Any]:
    severity = data.get("severity", "low").lower()
    color = "Good" if severity == "low" else ("Warning" if severity == "medium" else "Attention")
    
    body = [
        {
            "type": "TextBlock",
            "text": f"Status Alert: {severity.upper()}",
            "weight": "Bolder",
            "size": "Medium",
            "color": color
        },
        {
            "type": "FactSet",
            "facts": [
                { "title": "Value:", "value": str(data.get("value", 0)) },
                { "title": "Severity:", "value": severity.title() }
            ]
        },
        {
            "type": "TextBlock",
            "text": data.get("detail", "No details provided."),
            "wrap": True
        }
    ]
    
    actions = []
    if severity != "low":
        actions.append({
            "type": "Action.Submit",
            "title": "Acknowledge",
            "data": { "action": "acknowledge" },
            "text": "acknowledge",
            "msteams": { "type": "imBack", "value": "acknowledge" }
        })
         
    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": f"Status Alert: {severity.upper()}. {data.get('detail', 'No details provided.')}",
        "body": body,
        "actions": actions if actions else None
    }

def create_data_summary_card(data: Dict[str, Any]) -> Dict[str, Any]:
    # Simulate a chart with an image
    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": f"Data Summary for {data.get('title', 'Data Summary')}",
        "body": [
            {
                "type": "TextBlock",
                "text": data.get("title", "Data Summary"),
                "weight": "Bolder",
                "size": "Medium"
            },
            {
                "type": "Image",
                "url": "https://quickchart.io/chart?c={type:'bar',data:{labels:['Q1','Q2','Q3','Q4'],datasets:[{label:'Users',data:[50,60,70,180]}]}}",
                "size": "Stretch",
                "altText": "Data Chart"
            },
            {
                "type": "FactSet",
                "facts": [
                    { "title": "Total:", "value": str(data.get("total", 0)) },
                    { "title": "Trend:", "value": data.get("trend", "Stable") }
                ]
            }
        ]
    }

def create_form_card(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": f"Form: {data.get('title', 'Feedback Form')}",
        "body": [
            {
                "type": "TextBlock",
                "text": data.get("title", "Feedback Form"),
                "weight": "Bolder",
                "size": "Medium"
            },
            {
                "type": "Input.Text",
                "id": "name",
                "placeholder": "Enter your name"
            },
            {
                "type": "Input.Date",
                "id": "date"
            },
            {
                "type": "Input.Text",
                "id": "comment",
                "placeholder": "Comments...",
                "isMultiline": True
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit",
                "data": { "action": "submit_form" },
                "text": "submit_form",
                "msteams": { "type": "imBack", "value": "submit_form" }
            }
        ]
    }

def create_list_card(data: Dict[str, Any]) -> Dict[str, Any]:
    # Check multiple possible keys for the list items
    items = data.get("items") or data.get("tasks") or data.get("checklist") or []
    title = data.get("title") or "Item List"
    
    body = [
        {
            "type": "TextBlock",
            "text": title,
            "size": "Medium",
            "weight": "Bolder"
        }
    ]
    
    if not items:
        body.append({
            "type": "TextBlock",
            "text": "(No items found)",
            "isSubtle": True,
            "italic": True
        })
    else:
        for item in items:
            # Handle both dicts and simple strings
            if isinstance(item, str):
                item_title = item
                item_subtitle = ""
            else:
                item_title = item.get("title", "Item")
                item_subtitle = item.get("subtitle", "")

            item_content = [
                {
                    "type": "TextBlock",
                    "text": item_title,
                    "weight": "Bolder",
                    "wrap": True
                }
            ]
            if item_subtitle:
                item_content.append({
                    "type": "TextBlock",
                    "text": item_subtitle,
                    "isSubtle": True,
                    "spacing": "None",
                    "wrap": True
                })

            body.append({
                "type": "Container",
                "items": item_content,
                "separator": True
            })
        
    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": f"List: {title}. {' '.join([i.get('title', '') if isinstance(i, dict) else i for i in items[:3]])}",
        "body": body
    }

def create_flight_update_card(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": f"Flight Update for {data.get('flightNumber', 'UA123')}, {data.get('route', 'SFO > JFK')}. Status: {data.get('status', 'On Time')}",
        "body": [
            {
                "type": "TextBlock",
                "text": "Flight Update",
                "size": "Medium",
                "weight": "Bolder",
                "color": "Accent"
            },
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": data.get("flightNumber", "UA123"),
                                "size": "ExtraLarge",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": data.get("route", "SFO > JFK"),
                                "isSubtle": True,
                                "spacing": "None"
                            }
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": data.get("status", "On Time"),
                                "color": "Good" if data.get("status") == "On Time" else "Attention",
                                "weight": "Bolder"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "FactSet",
                "facts": [
                    { "title": "Passenger:", "value": data.get("passenger", "John Doe") },
                    { "title": "Gate:", "value": data.get("gate", "TBD") },
                    { "title": "Boarding:", "value": data.get("boardingTime", "12:00 PM") }
                ]
            }
        ],
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "Check In",
                "url": "https://www.united.com"
            }
        ]
    }

def create_weather_card(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": f"Weather in {data.get('city', 'Unknown')}: {data.get('temperature', '72')} degrees fahrenheit, {data.get('condition', 'Sunny')}",
        "body": [
             {
                "type": "TextBlock",
                "text": f"Weather in {data.get('city', 'Unknown')}",
                "size": "Medium",
                "weight": "Bolder"
            },
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {
                                "type": "Image",
                                "url": data.get("iconUrl", "https://openweathermap.org/img/wn/10d@2x.png"),
                                "size": "Small"
                            }
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": f"{data.get('temperature', '72')}°F",
                                "size": "ExtraLarge",
                                "weight": "Lighter"
                            },
                            {
                                "type": "TextBlock",
                                "text": data.get("condition", "Sunny"),
                                "isSubtle": True,
                                "spacing": "None"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "FactSet",
                "facts": [
                    { "title": "High:", "value": f"{data.get('high', '75')}°F" },
                    { "title": "Low:", "value": f"{data.get('low', '60')}°F" },
                    { "title": "Wind:", "value": data.get("wind", "10 mph") }
                ]
            }
        ]
    }

def create_stock_update_card(data: Dict[str, Any]) -> Dict[str, Any]:
    change = float(data.get("change", 0))
    color = "Good" if change >= 0 else "Attention"
    arrow = "▲" if change >= 0 else "▼"
    
    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": f"Market Update for {data.get('symbol', 'MSFT')}: Current price is {data.get('price', '0.00')} dollars, change is {data.get('changePoints', '0.00')} points.",
        "body": [
            {
                "type": "TextBlock",
                "text": "Market Update",
                "size": "Medium",
                "weight": "Bolder",
                "color": "Accent"
            },
            {
                "type": "Container",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": data.get("symbol", "MSFT"),
                        "size": "Large",
                        "weight": "Bolder"
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                            {
                                "type": "Column",
                                "width": "auto",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": f"${data.get('price', '0.00')}",
                                        "size": "ExtraLarge"
                                    }
                                ]
                            },
                            {
                                "type": "Column",
                                "width": "stretch",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": f"{arrow} {abs(change)}% ({data.get('changePoints', '0.00')})",
                                        "color": color,
                                        "weight": "Bolder",
                                        "spacing": "Medium"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

def create_calendar_invite_card(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": f"Calendar Invite: {data.get('title', 'Team Meeting')} at {data.get('time', '10:00 AM - 11:00 AM')}",
        "body": [
            {
                "type": "TextBlock",
                "text": "Calendar Invite",
                "size": "Medium",
                "weight": "Bolder",
                "color": "Accent"
            },
            {
                "type": "TextBlock",
                "text": data.get("title", "Team Meeting"),
                "size": "Large",
                "weight": "Bolder",
                "wrap": True
            },
            {
                "type": "FactSet",
                "facts": [
                    { "title": "Time:", "value": data.get("time", "10:00 AM - 11:00 AM") },
                    { "title": "Location:", "value": data.get("location", "Room 404") },
                    { "title": "Organizer:", "value": data.get("organizer", "Alok Pandit") }
                ]
            },
            {
                "type": "TextBlock",
                "text": data.get("description", "Agenda tbd..."),
                "wrap": True
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Accept",
                "style": "positive",
                "data": { "action": "accept", "eventId": data.get("id") },
                "text": "accept"
            },
            {
                "type": "Action.Submit",
                "title": "Decline",
                "style": "destructive",
                "data": { "action": "decline", "eventId": data.get("id") },
                "text": "decline"
            }
        ]
    }

def create_restaurant_details_card(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
         "type": "AdaptiveCard",
         "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
         "version": "1.4",
         "speak": f"Restaurant Details for {data.get('name', 'Restaurant Name')}. Rating: {data.get('rating', '4.5')}",
         "body": [
            {
               "type": "Image",
               "url": data.get("imageUrl", "https://adaptivecards.io/content/cats/2.png"),
               "size": "Stretch",
               "altText": "Restaurant Image"
            },
            {
               "type": "TextBlock",
               "text": data.get("name", "Restaurant Name"),
               "size": "Medium",
               "weight": "Bolder"
            },
            {
               "type": "ColumnSet",
               "columns": [
                  {
                     "type": "Column",
                     "width": "auto",
                     "items": [
                        {
                           "type": "TextBlock",
                           "text": f"⭐ {data.get('rating', '4.5')} ({data.get('reviews', '100')})",
                           "isSubtle": True
                        }
                     ]
                  },
                  {
                     "type": "Column",
                     "width": "stretch",
                     "items": [
                        {
                           "type": "TextBlock",
                           "text": f"{data.get('cuisine', 'American')} • {data.get('price', '$$$')}",
                           "isSubtle": True,
                           "horizontalAlignment": "Right"
                        }
                     ]
                  }
               ]
            },
            {
               "type": "TextBlock",
               "text": data.get("address", "123 Main St, City"),
               "wrap": True,
               "isSubtle": True
            }
         ],
         "actions": [
            {
               "type": "Action.OpenUrl",
               "title": "Book Table",
               "url": data.get("url", "https://opentable.com")
            },
            {
               "type": "Action.OpenUrl",
               "title": "View Menu",
               "url": data.get("menuUrl", "https://opentable.com")
            }
         ]
    }

def create_popup_card(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": f"{data.get('title', 'Tool')}. {data.get('text', 'Click button to open.')}",
        "body": [
            {
                "type": "Image",
                "url": "https://media.giphy.com/media/l41lI4bYmcsPJX9Go/giphy.gif",
                "size": "Medium",
                "horizontalAlignment": "Center"
            },
            {
                "type": "TextBlock",
                "text": data.get("title", "Tool"),
                "size": "Medium",
                "weight": "Bolder",
                "horizontalAlignment": "Center"
            },
            {
                "type": "TextBlock",
                "text": data.get("text", "Click button to open."),
                "wrap": True
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": f"{data.get('buttonTitle', 'Open')} (Teams)",
                "data": {
                    "msteams": {
                        "type": "task/fetch"
                    },
                    "url": data.get("url", "about:blank"),
                    "title": data.get("title", "Tool")
                },
                "text": "open_tool"
            },
            {
                "type": "Action.OpenUrl",
                "title": f"{data.get('buttonTitle', 'Open')} (Web)",
                "url": data.get("url", "about:blank")
            }
        ]
    }

def create_simple_card(data: Dict[str, Any]) -> Dict[str, Any]:
    text = data.get("message") or data.get("text") or data.get("content") or "No content provided."
    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": text,
        "body": [
            {
                "type": "TextBlock",
                "text": text,
                "wrap": True
            }
        ]
    }

def create_dynamic_form(data: Dict[str, Any]) -> Dict[str, Any]:
    title = data.get("title", "Dynamic Form")
    instructions = data.get("instructions")
    fields = data.get("fields", [])
    
    body = [
        {
            "type": "TextBlock",
            "text": title,
            "weight": "Bolder",
            "size": "Large"
        }
    ]
    
    if instructions:
        body.append({
            "type": "TextBlock",
            "text": instructions,
            "wrap": True,
            "isSubtle": True
        })
        
    for field in fields:
        field_id = field.get("id")
        field_type = field.get("type", "text").lower()
        label = field.get("label", field_id)
        placeholder = field.get("placeholder", "")
        is_required = field.get("isRequired", False)
        
        # Add Label
        body.append({
            "type": "TextBlock",
            "text": label,
            "weight": "Bolder",
            "spacing": "Medium"
        })
        
        # Add Input Element
        if field_type == "text":
            body.append({
                "type": "Input.Text",
                "id": field_id,
                "placeholder": placeholder,
                "isRequired": is_required,
                "errorMessage": f"{label} is required"
            })
        elif field_type == "date":
            body.append({
                "type": "Input.Date",
                "id": field_id,
                "isRequired": is_required,
                "errorMessage": f"{label} is required"
            })
        elif field_type == "number":
             body.append({
                "type": "Input.Number",
                "id": field_id,
                "placeholder": placeholder,
                "isRequired": is_required,
                "errorMessage": f"{label} is required"
            })
        elif field_type in ["choice", "checkbox"]:
            choices = []
            for opt in field.get("options", []):
                choices.append({
                    "title": opt.get("title", "Option"),
                    "value": opt.get("value", "val")
                })
            
            is_multi = field.get("isMultiSelect", False) or field_type == "checkbox"
            style = "expanded" if field_type == "checkbox" else "compact"
            
            body.append({
                "type": "Input.ChoiceSet",
                "id": field_id,
                "choices": choices,
                "isMultiSelect": is_multi,
                "style": style,
                "isRequired": is_required,
                "errorMessage": f"Please select {label}"
            })

    submit_data = { "action": "submit_dynamic_form" }
    if "form_id" in data:
        submit_data["form_id"] = data["form_id"]

    return {
        "type": "AdaptiveCard",
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "speak": f"Dynamic Form: {title}",
        "body": body,
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit",
                "data": submit_data,
                "text": "submit_dynamic_form",
                "msteams": { "type": "imBack", "value": "submit_dynamic_form" }
            }
        ]
    }

@mcp.tool()
def generate_adaptive_card(template: str, data: str) -> str:
    """
    Generates an Adaptive Card based on the specified template and data.
    
    Args:
        template: The template type ('hero', 'alert', 'data_summary', 'form', 'list', 'simple', 'flight_update', 'weather', 'stock_update', 'calendar_invite', 'restaurant_details', 'dynamic_form').
        data: A JSON string containing the data for the card.
    """
    try:
        data_dict = json.loads(data)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON data provided."})
        
    template = template.lower()
    
    if template == "hero":
        card = create_hero_card(data_dict)
    elif template == "alert":
        card = create_alert_card(data_dict)
    elif template == "data_summary":
        card = create_data_summary_card(data_dict)
    elif template == "form":
        card = create_form_card(data_dict)
    elif template == "list":
        card = create_list_card(data_dict)
    elif template == "flight_update":
        card = create_flight_update_card(data_dict)
    elif template == "weather":
        card = create_weather_card(data_dict)
    elif template == "stock_update":
        card = create_stock_update_card(data_dict)
    elif template == "calendar_invite":
        card = create_calendar_invite_card(data_dict)
    elif template == "restaurant_details":
        card = create_restaurant_details_card(data_dict)
    elif template == "popup":
        card = create_popup_card(data_dict)
    elif template == "simple":
        card = create_simple_card(data_dict)
    elif template == "dynamic_form":
        card = create_dynamic_form(data_dict)
    else:
        # Default simple card fallback
        card = create_simple_card(data_dict)
        
    return json.dumps(card, indent=2)

if __name__ == "__main__":
    mcp.run()
