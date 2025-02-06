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


class MediaType(enum.Enum):
    VIDEO = "video"
    IMAGE = "image"


class Tour(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_mode: Mapped[TripMode] = mapped_column(Enum("walking", "bicycling", "driving", name="mode_enum", native_enum=True), default="walking")
    name: Mapped[str] = mapped_column(String(64))
    is_visible: Mapped[Optional[bool]] = mapped_column(BOOLEAN, default=True)
    trip_pic: Mapped[Optional[str]] = mapped_column(String(96))
    pic_caption: Mapped[Optional[str]] = mapped_column(String(128))
    carousel_pos: Mapped[Optional[int]]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["Users"] = relationship(back_populates="tours")

    __table_args__ = (UniqueConstraint('name', 'trip_mode', name='name_mode_uc'),)

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

    __table_args__ = (UniqueConstraint('tour_id', 'date', name='tour_lap_at_date_uc'),)

    def __repr__(self) -> str:
        return f"{_('Tappa')}: {self.start}-{self.destination}  {_('Giorno')}: {self.date}."


class Hotel(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(48))
    address: Mapped[str] = mapped_column(String(48))
    town: Mapped[str] = mapped_column(String(32))
    lat: Mapped[Optional[float]] = mapped_column(FLOAT, default=0)
    long: Mapped[Optional[float]] = mapped_column(FLOAT, default=0)
    # phone: Mapped[Optional[str]] = mapped_column(String(16))
    # href_phone: Mapped[Optional[str]] = mapped_column(String(16))
    email: Mapped[Optional[str]] = mapped_column(String(32))
    check_in: Mapped[Optional[date]] = mapped_column(DATE)
    check_out: Mapped[Optional[date]] = mapped_column(DATE)
    reserved: Mapped[Optional[bool]] = mapped_column(BOOLEAN, default=False)
    price: Mapped[Optional[int]]
    photo: Mapped[Optional[str]] = mapped_column(String(48))
    link: Mapped[Optional[str]]
    lap_id: Mapped[int] = mapped_column(ForeignKey("lap.id", ondelete="set null"), nullable=True)
    tour_id: Mapped[int] = mapped_column(ForeignKey("tour.id", ondelete="cascade"))
    lap: Mapped["Lap"] = relationship(back_populates="hotels")
    phones: Mapped[List["PhoneNumber"]] = relationship(back_populates="hotel")

    def __repr__(self) -> str:
        return f"{_('Albergo')}: {self.name} - {self.town}"


class Users(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(String(64), unique=True)
    is_admin: Mapped[Optional[bool]] = mapped_column(BOOLEAN, default=False)
    tours: Mapped[List["Tour"]] = relationship(back_populates="owner")

    def __repr__(self):
        return self.username


class Media(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    lap_id: Mapped[int] = mapped_column(ForeignKey("lap.id", ondelete="set null"), nullable=True)
    media_src: Mapped[str] = mapped_column(String(96))
    media_width: Mapped[int] = mapped_column(INT, default=0)
    media_height: Mapped[int] = mapped_column(INT, default=0)
    media_type: Mapped[MediaType] = mapped_column(Enum("video", "image", name="media_types", native_enum=True), default="image")
    date: Mapped[datetime] = mapped_column(TIMESTAMP)
    lat: Mapped[Optional[float]] = mapped_column(FLOAT)
    long: Mapped[Optional[float]] = mapped_column(FLOAT)
    caption: Mapped[Optional[str]] = mapped_column(String(128))
    __table_args__ = (UniqueConstraint('lap_id', 'media_src', name='lap_media_uc'), )

    def __repr__(self) -> str:
        return f"{_('Foto')} {self.media_src[: -4]}"


class PhoneNumber(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[Optional[str]] = mapped_column(String(16))
    href_phone: Mapped[Optional[str]] = mapped_column(String(16), unique=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotel.id", ondelete="cascade"))
    hotel: Mapped["Hotel"] = relationship(back_populates="phones")

    def __repr__(self) -> str:
        return f"{_('Telefono')} {self.href_phone} - {self.hotel.name}"
