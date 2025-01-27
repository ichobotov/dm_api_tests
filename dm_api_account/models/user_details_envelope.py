from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import (
    List,
    Optional,
    Any,
)

from pydantic import BaseModel, Field



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


class Info(BaseModel):
    value: str
    parse_mode: str = Field(..., alias='parseMode')


class Paging(BaseModel):
    posts_per_page: int = Field(..., alias='postsPerPage')
    comments_per_page: int = Field(..., alias='commentsPerPage')
    topics_per_page: int = Field(..., alias='topicsPerPage')
    messages_per_page: int = Field(..., alias='messagesPerPage')
    entities_per_page: int = Field(..., alias='entitiesPerPage')


class Settings(BaseModel):
    color_schema: str = Field(..., alias='colorSchema')
    nanny_greetings_message: str = Field(None, alias='nannyGreetingsMessage')
    paging: Paging


class UserDetails(BaseModel):
    login: str
    roles: List[UserRole]
    medium_picture_url: Optional[str] = None
    small_picture_url: Optional[str] = None
    status: Optional[str] = None
    rating: Rating
    online: datetime
    name: Optional[str] = None
    location: Optional[str] = None
    registration: Optional[datetime] = None
    icq: Optional[str] = None
    skype: Optional[str] = None
    original_picture_url: str = Field(None, alias='originalPictureUrl')
    info: Any = None
    settings: Settings


class UserDetailsEnvelope(BaseModel):
    resource: Optional[UserDetails] = None
    metadata: Optional[str] = None