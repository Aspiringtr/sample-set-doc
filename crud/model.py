from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped

from data_base.database import Base

class Item(Base):
    __tablename__ = "item"

    id:Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True)
    item_name:Mapped[str] = mapped_column(String(100), nullable=False)
    item_description:Mapped[str] = mapped_column(String(200), nullable=False, default="")
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey("users.id"),nullable=False,index=True)