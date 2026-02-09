from pydantic import BaseModel, Field
from typing import List, Optional

class HeroData(BaseModel):
    title: str = Field(..., description="Title of the hero card")
    description: str = Field(..., description="Description text")
    imageUrl: str = Field(..., description="URL of the hero image")
    url: str = Field(..., description="Action URL")

class AlertData(BaseModel):
    severity: str = Field(..., description="low, medium, or high")
    value: float = Field(..., description="Numeric value associated with the alert")
    detail: str = Field(..., description="Detailed message")

class DataSummaryData(BaseModel):
    title: str = Field(..., description="Title of the data summary")
    total: float = Field(..., description="Total value")
    trend: str = Field(..., description="Trend description, e.g. 'Up 10%'")

class FormData(BaseModel):
    title: str = Field(..., description="Title of the form")

class ListItem(BaseModel):
    title: str
    subtitle: str

class ListData(BaseModel):
    title: str = Field(..., description="Title of the list")
    items: List[ListItem] = Field(..., description="List of items")

class SimpleData(BaseModel):
    message: str = Field(..., description="The message content")

class FlightUpdateData(BaseModel):
    flightNumber: str
    status: str
    gate: str
    passenger: str
    boardingTime: str
    route: str

class WeatherData(BaseModel):
    city: str
    temperature: int
    condition: str
    high: int
    low: int
    wind: str
    iconUrl: str

class StockUpdateData(BaseModel):
    symbol: str
    price: float
    change: float
    changePoints: float

class CalendarInviteData(BaseModel):
    title: str
    time: str
    location: str
    organizer: str
    description: str
    id: str

class RestaurantDetailsData(BaseModel):
    name: str
    rating: float
    reviews: int
    cuisine: str
    price: str
    address: str
    imageUrl: str
    url: str
    menuUrl: str

class PopupData(BaseModel):
    title: str
    text: str
    buttonTitle: str
    url: str

class FormOption(BaseModel):
    title: str
    value: str

class FormField(BaseModel):
    id: str
    type: str = Field(..., description="text, date, choice, checkbox, number")
    label: str
    placeholder: Optional[str] = None
    isRequired: bool = False
    options: Optional[List[FormOption]] = None
    isMultiSelect: bool = False

class DynamicFormData(BaseModel):
    title: str = Field(..., description="Title of the dynamic form")
    instructions: Optional[str] = None
    fields: List[FormField]

