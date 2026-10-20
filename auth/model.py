from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from data_base.database import Base

class User(Base):
    __tablename__ = "users"

    id:Mapped[int]=mapped_column(Integer,autoincrement=True,primary_key=True,index=True)
    user_name:Mapped[str]=mapped_column(String(50),index=True,nullable=False,unique=True)
    password_hash:Mapped[str]=mapped_column(String(255),nullable=False)
