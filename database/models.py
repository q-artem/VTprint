from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import Mapped

from database.base import Base

class Language(Base):
    __tablename__ = "languages"

    code: Mapped[str] = Column(String(2), primary_key=True)
    name: Mapped[str] = Column(String(50), nullable=False)

    users = relationship("User", back_populates="language")

class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    sheets_per_day: Mapped[int] = Column(Integer, nullable=False)
    password: Mapped[str] = Column(String(50), nullable=False)

    users = relationship("User", back_populates="group")

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = Column(Integer, primary_key=True)
    language_code: Mapped[str] = Column(String(2), ForeignKey("languages.code"), nullable=False)
    group_id: Mapped[int] = Column(Integer, ForeignKey("groups.id"), nullable=False)
    pages_left: Mapped[int] = Column(Integer, nullable=False)
    banned: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    language = relationship("Language", back_populates="users", lazy="selectin")
    group = relationship("Group", back_populates="users", lazy="selectin")