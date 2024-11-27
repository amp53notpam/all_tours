import enum
from datetime import date, time, datetime
from . import db
from sqlalchemy import String, BOOLEAN, INT, FLOAT, DATE, TIMESTAMP, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from typing import Optional, List
from flask_babel import _, lazy_gettext as _l


class TripMode(enum.Enum):
    WALKING = "walking"
    BICYCLING = "bicycling"
    DRIVING = "driving"


class Tour(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_mode: Mapped[TripMode] = mapped_column(Enum("walking", "bicycling", "driving", name="mode_enum", native_enum=True), default="walking")
    name: Mapped[str] = mapped_column(String(64), unique=True)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    carousel_pos: Mapped[Optional[int]]

    def __repr__(self) -> str:
        return self.name


class Lap(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(DATE)
    start: Mapped[str] = mapped_column(String(32))
    destination: Mapped[str] = mapped_column(String(32))
    distance: Mapped[Optional[float]] = mapped_column(FLOAT, default=0)
    ascent: Mapped[Optional[int]]
    descent: Mapped[Optional[int]]
    duration: Mapped[Optional[time]]
    done: Mapped[Optional[bool]] = mapped_column(BOOLEAN, default=False)
    has_photos: Mapped[Optional[bool]] = mapped_column(BOOLEAN, default=False)
    gpx: Mapped[Optional[str]] = mapped_column(String(48))
    tour_id: Mapped[int] = mapped_column(ForeignKey("tour.id"))
    hotels: Mapped[List["Hotel"]] = relationship(back_populates="lap")

    def __repr__(self) -> str:
        return f"{_('Tappa')}: {self.start}-{self.destination}  {_('Giorno')}: {self.date}"


class Hotel(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(48))
    address: Mapped[str] = mapped_column(String(48))
    town: Mapped[str] = mapped_column(String(32))
    lat: Mapped[Optional[float]] = mapped_column(FLOAT, default=0)
    long: Mapped[Optional[float]] = mapped_column(FLOAT, default=0)
    phone: Mapped[Optional[str]] = mapped_column(String(16))
    href_phone: Mapped[Optional[str]] = mapped_column(String(16))
    email: Mapped[Optional[str]] = mapped_column(String(32))
    check_in: Mapped[Optional[date]] = mapped_column(DATE)
    check_out: Mapped[Optional[date]] = mapped_column(DATE)
    reserved: Mapped[Optional[bool]] = mapped_column(BOOLEAN, default=False)
    price: Mapped[Optional[int]]
    photo: Mapped[Optional[str]] = mapped_column(String(48))
    link: Mapped[Optional[str]]
    lap_id: Mapped[int] = mapped_column(ForeignKey("lap.id", ondelete="set null"), nullable=True)
    lap: Mapped["Lap"] = relationship(back_populates="hotels")

    def __repr__(self) -> str:
        return f"{_('Albergo')}: {self.name} - {self.town}"


class Admin(UserMixin, db.Model):
    __bind_key__ = 'db_sec'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str]

    def __repr__(self) -> str:
        return "db administrator"


class TripImage(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    lap_id: Mapped[int] = mapped_column(ForeignKey("lap.id", ondelete="set null"), nullable=True)
    img_src:  Mapped[str] = mapped_column(String(96))
    img_width: Mapped[int] = mapped_column(INT, default=0)
    img_height: Mapped[int] = mapped_column(INT, default=0)
    date: Mapped[datetime] = mapped_column(TIMESTAMP)
    lat: Mapped[Optional[float]] = mapped_column(FLOAT, default=0)
    long: Mapped[Optional[float]] = mapped_column(FLOAT, default=0)
    caption: Mapped[Optional[str]] = mapped_column(String(128))
    __table_args__ = (UniqueConstraint('lap_id', 'img_src', name='lap_img_uc'), )

    def __repr__(self) -> str:
        return f"{_('Foto')} {self.img_src[: -4]}"
