from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )

    user_url = relationship("URL", back_populates="user")


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    long_url = Column(String, nullable=False, index=True)
    short_url = Column(String, unique=True, nullable=False, index=True)
    clicks = Column(Integer, index=True, default=0)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="user_url")
    click_records = relationship("Click", back_populates="url")


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    country = Column(String, index=True)
    state = Column(String, index=True)
    city = Column(String, index=True)
    click_date = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )
    url_id = Column(Integer, ForeignKey("urls.id"))

    url = relationship("URL", back_populates="click_records")
