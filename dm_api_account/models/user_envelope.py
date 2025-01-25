from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import (
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
)


class UserRole(str, Enum):
    GUEST = 'Guest'
    PLAYER = 'Player'
    ADMINISTRATOR = 'Administrator'
    NANNYMODERATOR = 'NannyModerator'
    REGULARMODERATOR = 'RegularModerator'
    SENIORMODERATOR = 'SeniorModerator'


class Rating(BaseModel):
    enabled: bool
    quality: int
    quantity: int


class User(BaseModel):
    login: str
    roles: List[UserRole]
    mediumPictureUrl: Optional[str] = None
    smallPictureUrl: Optional[str] = None
    status: Optional[str] = None
    rating: Rating
    online: Optional[datetime] = None
    name: Optional[str] = None
    location: Optional[str] = None
    registration: Optional[datetime] = None


class UserEnvelope(BaseModel):
    resource: Optional[User] = None
    metadata: Optional[str] = None