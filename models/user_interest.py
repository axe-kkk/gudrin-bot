from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.user import User
    from models.interest import Interest

class UserInterest(SQLModel, table=True):
    __tablename__ = "user_interests"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    interest_id: int = Field(foreign_key="interests.id")

    user: Optional["User"] = Relationship(back_populates="interests")
    interest: Optional["Interest"] = Relationship(back_populates="user_interests")