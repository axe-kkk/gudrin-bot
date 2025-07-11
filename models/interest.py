from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.user_interest import UserInterest

class Interest(SQLModel, table=True):
    __tablename__ = "interests"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    user_interests: List["UserInterest"] = Relationship(back_populates="interest")