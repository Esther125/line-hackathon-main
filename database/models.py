"""SQLAlchemy models for Cony app."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class CouponType(enum.Enum):
    permanent = "permanent"
    game = "game"


class AppUser(Base):
    __tablename__ = "app_user"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    coupons = relationship("Coupon", back_populates="user", cascade="all, delete")


class Coupon(Base):
    __tablename__ = "coupon"
    __table_args__ = (UniqueConstraint("code", name="uq_coupon_code"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), ForeignKey("app_user.user_id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(CouponType), nullable=False, default=CouponType.game)
    code = Column(String(64), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("AppUser", back_populates="coupons")
