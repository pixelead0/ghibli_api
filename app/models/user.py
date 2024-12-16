import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    ADMIN = "admin"
    FILMS = "films"
    PEOPLE = "people"
    LOCATIONS = "locations"
    SPECIES = "species"
    VEHICLES = "vehicles"


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    role: UserRole = Field(default=UserRole.FILMS)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, unique=True, nullable=False
    )
    hashed_password: str = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: uuid.UUID


class UserUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
