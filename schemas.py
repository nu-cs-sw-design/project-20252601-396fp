# schemas.py
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ---------- USERS ----------
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str

    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user_id: int


# ---------- LISTINGS ----------
class ListingCreate(BaseModel):
    title: str
    description: str
    price_per_day: float


class ListingOut(BaseModel):
    id: int
    owner_id: int
    title: str
    description: str
    price_per_day: float

    class Config:
        orm_mode = True


# ---------- RENTALS ----------
class RentalRequestCreate(BaseModel):
    listing_id: int
    start_date: date
    end_date: date


class RentalOut(BaseModel):
    id: int
    listing_id: int
    owner_id: int
    rentee_id: int
    start_date: date
    end_date: date
    status: str

    class Config:
        orm_mode = True


# ---------- MESSAGES ----------
class MessageCreate(BaseModel):
    rental_id: int
    receiver_id: int
    text: str


class MessageOut(BaseModel):
    id: int
    rental_id: int
    sender_id: int
    receiver_id: int
    text: str
    created_at: datetime

    class Config:
        orm_mode = True


# ---------- NOTIFICATIONS ----------
class NotificationOut(BaseModel):
    id: int
    user_id: int
    type: str
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True
