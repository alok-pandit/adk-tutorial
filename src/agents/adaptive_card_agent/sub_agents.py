from .models import (
    HeroData, AlertData, DataSummaryData, FormData, ListData, ListItem, SimpleData,
    FlightUpdateData, WeatherData, StockUpdateData, CalendarInviteData, RestaurantDetailsData, PopupData
)

def get_hero_content(topic: str) -> HeroData:
    """Returns content for a hero card based on a topic."""
    return HeroData(
        title=f"Welcome to {topic}",
        description=f"This is a demonstration of {topic}.",
        imageUrl="https://adaptivecards.io/content/cats/1.png",
        url="https://adaptivecards.io"
    )

def get_system_alert(component: str) -> AlertData:
    """Returns system alert data."""
    return AlertData(
        severity="high",
        value=99.9,
        detail=f"Critical failure detected in {component} module."
    )

def get_data_report(report_type: str) -> DataSummaryData:
    """Returns a data report based on the requested type (e.g., sales, growth, performance)."""
    if "growth" in report_type.lower():
        return DataSummaryData(
            title=f"User Growth - {report_type}",
            total=5432.00,
            trend="Up 25% WoW"
        )
    elif "performance" in report_type.lower():
         return DataSummaryData(
            title=f"System Performance - {report_type}",
            total=98.5,
            trend="Stable"
        )
    else:
        # Default to sales
        return DataSummaryData(
            title=f"Sales Report - {report_type}",
            total=125000.00,
            trend="Up 15% YoY"
        )

def get_feedback_form(context: str = "general") -> FormData:
    """Returns a feedback form structure."""
    return FormData(title=f"Feedback for {context}")

def get_task_list(user: str) -> ListData:
    """Returns a list of tasks for a user."""
    return ListData(
        title=f"Tasks for {user}",
        items=[
            ListItem(title="Review PR", subtitle="High Priority"),
            ListItem(title="Team Sync", subtitle="10:00 AM"),
            ListItem(title="Update Docs", subtitle="Low Priority")
        ]
    )

def get_simple_message(text: str) -> SimpleData:
    """Returns a simple message."""
    return SimpleData(message=text)

def get_flight_status(flight_number: str) -> FlightUpdateData:
    """Returns flight status information."""
    return FlightUpdateData(
        flightNumber=flight_number,
        status="On Time",
        gate="G12",
        passenger="Jane Doe",
        boardingTime="14:30",
        route="SFO > LHR"
    )

def get_weather_forecast(city: str) -> WeatherData:
    """Returns weather forecast for a city."""
    return WeatherData(
        city=city,
        temperature=72,
        condition="Sunny",
        high=78,
        low=62,
        wind="10 mph",
        iconUrl="https://openweathermap.org/img/wn/01d@2x.png"
    )

def get_stock_quote(symbol: str) -> StockUpdateData:
    """Returns stock quote for a symbol."""
    return StockUpdateData(
        symbol=symbol,
        price=350.25,
        change=1.25,
        changePoints=4.30
    )

def get_calendar_event(event_type: str) -> CalendarInviteData:
    """Returns calendar event details."""
    return CalendarInviteData(
        title=f"{event_type} Sync",
        time="Tomorrow, 10:00 AM - 11:00 AM",
        location="Room 404",
        organizer="Alok Pandit",
        description="Discussing Q3 project roadmap.",
        id="evt_12345"
    )

def get_restaurant_recommendation(cuisine: str) -> RestaurantDetailsData:
    """Returns a restaurant recommendation."""
    return RestaurantDetailsData(
        name=f"The Best {cuisine} Place",
        rating=4.8,
        reviews=342,
        cuisine=cuisine,
        price="$$$",
        address="123 Flavor St, Food City",
        imageUrl="https://adaptivecards.io/content/cats/2.png",
        url="https://opentable.com",
        menuUrl="https://opentable.com/menu"
    )

def get_popup_tools(tool_type: str) -> PopupData:
    """Returns popup action data for specific tools (calendar, city, checklist)."""
    base_url = "http://10.0.0.250:3000"
    tool_type = tool_type.lower()
    
    if "calendar" in tool_type:
        return PopupData(
            title="Calendar Tool",
            text="Click below to open the calendar picker.",
            buttonTitle="Open Calendar",
            url=f"{base_url}"
            # url=f"{base_url}/calendar"
        )
    elif "city" in tool_type or "location" in tool_type:
        return PopupData(
            title="Location Selector",
            text="Click below to select a city.",
            buttonTitle="Select City",
            url=f"{base_url}"
            # url=f"{base_url}/city"
        )
    elif "checklist" in tool_type:
        return PopupData(
             title="Checklist View",
             text="Click below to view the checklist.",
             buttonTitle="View Checklist",
             url=f"{base_url}"
            # url=f"{base_url}/checklist"
        )
    else:
        # Default fallback
        return PopupData(
            title="External Tool",
            text="Click below to open the tool.",
            buttonTitle="Open Tool",
            url=f"{base_url}"
        )
