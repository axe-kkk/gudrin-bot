# models/user.py

from sqlmodel import SQLModel, Field
from typing import Optional, TYPE_CHECKING
from sqlmodel import Relationship
from typing import List

from models.user_interest import UserInterest

if TYPE_CHECKING:
    from user import User

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int
    coins: int = Field(default=1)
    diamonds: int = Field(default=0)
    referred_by: Optional[int] = Field(default=None, foreign_key="users.id")
    flag: bool = Field(default=True)
    interests: List["UserInterest"] = Relationship(back_populates="user")

    referrals: List["User"] = Relationship(back_populates="referrer", sa_relationship_kwargs={"cascade": "all, delete"})
    referrer: Optional["User"] = Relationship(back_populates="referrals",
                                              sa_relationship_kwargs={"remote_side": "User.id"})