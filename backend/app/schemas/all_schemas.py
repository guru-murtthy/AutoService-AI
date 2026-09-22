from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

# Auth & User Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "owner"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Business Schemas
class BusinessCreate(BaseModel):
    name: str
    business_type: Optional[str] = "travel_and_tour"
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class BusinessResponse(BaseModel):
    id: str
    name: str
    business_type: str
    phone: Optional[str]
    email: Optional[str]
    currency: str
    subscription_plan: str
    subscription_status: str

# Customer & Enquiry Schemas with Input Validation
class EnquiryRequest(BaseModel):
    business_id: str
    customer_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=5)
    email: Optional[EmailStr] = None
    message: str = Field(..., min_length=2)

    @field_validator("phone")

    def validate_phone(cls, v):
        clean = re.sub(r"[^\d+]", "", v)
        if len(clean) < 7:
            raise ValueError("Phone number must contain at least 7 digits")
        return v

    @field_validator("customer_name")

    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Customer name cannot be empty")
        return v.strip()

class ExtractedRequirement(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    vehicle_type: Optional[str] = None
    duration_days: Optional[int] = Field(None, gt=0)
    travel_date: Optional[str] = None
    passenger_count: Optional[int] = Field(None, gt=0)
    budget: Optional[float] = Field(None, ge=0)
    confidence: float = 0.9

class EnquiryResponse(BaseModel):
    lead_id: str
    customer_id: str
    extracted: ExtractedRequirement
    missing_fields: List[str]
    reply_message: str
    lead_score: int

# Pricing Calculation Schemas
class QuoteCalculationRequest(BaseModel):
    business_id: str
    vehicle_type: str
    duration_days: int = Field(1, gt=0)
    estimated_km: Optional[float] = Field(None, ge=0)
    include_driver_allowance: bool = True
    discount_amount: float = Field(0.0, ge=0)

class QuoteItemSchema(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total: float

class QuoteCalculationResponse(BaseModel):
    subtotal: float
    tax: float
    discount: float
    total: float
    currency: str = "INR"
    items: List[QuoteItemSchema]

# Quotation Schemas
class QuotationCreateRequest(BaseModel):
    lead_id: str
    calculation: QuoteCalculationResponse
    valid_days: int = Field(7, gt=0)

class QuotationResponse(BaseModel):
    id: str
    lead_id: str
    quotation_number: str
    subtotal: float
    tax: float
    discount: float
    total: float
    currency: str
    status: str
    created_at: datetime

# Lead Schemas
class LeadResponse(BaseModel):
    id: str
    business_id: str
    customer_id: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    destination: Optional[str]
    origin: Optional[str]
    duration_days: Optional[int] = None
    travel_date: Optional[str]
    passenger_count: Optional[int]
    vehicle_type: Optional[str]
    budget: Optional[float]
    status: str
    lead_score: int
    created_at: datetime

class LeadStatusUpdate(BaseModel):
    status: str

# Daily Report Schema
class DailyReportResponse(BaseModel):
    date: str
    enquiries_count: int
    qualified_leads: int
    quotes_generated: int
    quotes_accepted: int
    bookings_count: int
    revenue_amount: float
    pending_followups: int
    failed_tasks: int
    estimated_ai_cost: float
    net_contribution: float

# Emergency Stop Schema
class EmergencyStopRequest(BaseModel):
    reason: str = "Manual admin trigger"

class EmergencyStopStatus(BaseModel):
    is_active: bool
    activated_by: Optional[str]
    activated_at: Optional[datetime]
    reason: Optional[str]
