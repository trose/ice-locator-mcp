"""
Database models for the heatmap feature.
Defines the Detainee, Facility, and DetaineeLocationHistory dataclasses.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Detainee:
    """Represents a detainee in the system."""
    id: Optional[int]
    first_name: str
    last_name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


@dataclass
class Facility:
    """Represents a facility where detainees are held."""
    id: Optional[int]
    name: str
    latitude: float
    longitude: float
    address: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


@dataclass
class DetaineeLocationHistory:
    """Tracks detainee location changes over time."""
    id: Optional[int]
    detainee_id: int
    facility_id: int
    start_date: datetime
    end_date: Optional[datetime]
    created_at: Optional[datetime]