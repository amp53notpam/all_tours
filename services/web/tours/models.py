from __future__ import annotations

import enum
from datetime import date, time, datetime
from . import db, Base
from sqlalchemy import Table, Column, String, BOOLEAN, INT, FLOAT, DATE, TIMESTAMP, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from typing import List
from flask_babel import _, lazy_gettext as _l


class TripMode(enum.Enum):
    WALKING = "walking"
    BICYCLING = "bicycling"
    DRIVING = "driving"


class MediaType(enum.Enum):
    VIDEO = "video"
    IMAGE = "image"


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(String(64), unique=True)
    is_admin: Mapped[bool | None] = mapped_column(BOOLEAN, default=False)
    tours: Mapped[List[Tour]] = relationship(back_populates="owner")

    def __repr__(self):
        return self.username


class Tour(db.Model):
    # __tablename__ = 'tour'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    trip_mode: Mapped[TripMode] = mapped_column(Enum("walking", "bicycling", "driving", name="mode_enum", native_enum=True), default="walking")
    is_visible: Mapped[bool | None] = mapped_column(BOOLEAN, default=True)
    trip_pic: Mapped[str | None] = mapped_column(String(96))
    pic_caption: Mapped[str | None] = mapped_column(String(128))
    carousel_pos: Mapped[int | None]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped[User] = relationship(back_populates="tours")
    laps: Mapped[List[Lap]] = relationship(back_populates="tour", order_by="Lap.date")

    __table_args__ = (UniqueConstraint('name', 'trip_mode', name='name_mode_uc'),)

    def __repr__(self) -> str:
        return self.name


class Lap(db.Model):
    # __tablename__ = 'lap'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date]
    start: Mapped[str] = mapped_column(String(32))
    destination: Mapped[str] = mapped_column(String(32))
    duration: Mapped[time | None]
    distance: Mapped[float | None] = mapped_column(FLOAT)
    ascent: Mapped[int | None]
    descent: Mapped[int | None]
    gpx: Mapped[str | None] = mapped_column(String(64))
    done: Mapped[bool | None] = mapped_column(BOOLEAN, default=False)
    tour_id: Mapped[int] = mapped_column(ForeignKey("tour.id"))
    tour: Mapped[Tour] = relationship(back_populates="laps")

    hotels: Mapped[List[Hotel]] = relationship(back_populates="lap")
    photos: Mapped[List[Media]] = relationship(back_populates="lap", order_by="Media.date")

    __table_args__ = (UniqueConstraint('tour_id', 'date', name='tour_lap_at_date_uc'),)

    def __repr__(self) -> str:
        return f"{_('Tappa')}: {self.start}-{self.destination}  {_('Giorno')}: {self.date}."


class Media(db.Model):
    # __tablename__ = 'media'

    id: Mapped[int] = mapped_column(primary_key=True)
    media_src: Mapped[str] = mapped_column(String(96))
    media_width: Mapped[int] = mapped_column(INT, default=0)
    media_height: Mapped[int] = mapped_column(INT, default=0)
    media_type: Mapped[MediaType] = mapped_column(Enum("video", "image", name="media_types", native_enum=True), default="image")
    date: Mapped[datetime] = mapped_column(TIMESTAMP)
    lat: Mapped[float | None] = mapped_column(FLOAT)
    long: Mapped[float | None] = mapped_column(FLOAT)
    caption: Mapped[str | None] = mapped_column(String(128))
    lap_id: Mapped[int] = mapped_column(ForeignKey("lap.id"))
    lap: Mapped[Lap] = relationship(back_populates="photos")

    __table_args__ = (UniqueConstraint('lap_id', 'media_src', name='lap_media_uc'), )

    def __repr__(self) -> str:
        return f"{_('Foto')} {self.media_src[: -4]}"


association_table = Table(
    "hotel_phone",
    Base.metadata,
    Column("hotel_id", ForeignKey("hotel.id"), nullable=False),
    Column("phone_num_id", ForeignKey("phone_number.id"), nullable=False),
)


class Hotel(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    address: Mapped[str] = mapped_column(String(48))
    town: Mapped[str] = mapped_column(String(32))
    email: Mapped[str | None] = mapped_column(String(48))
    check_in: Mapped[date | None]
    check_out: Mapped[date | None]
    reserved: Mapped[bool | None] = mapped_column(BOOLEAN, default=False)
    price: Mapped[int | None]
    photo: Mapped[str | None] = mapped_column(String(48))
    link: Mapped[str | None]
    lat: Mapped[float | None]
    long: Mapped[float | None]
    lap_id: Mapped[int] = mapped_column(ForeignKey("lap.id"))
    lap: Mapped[Lap] = relationship(back_populates="hotels")
    phones: Mapped[List[PhoneNumber]] = relationship(secondary=association_table, back_populates="hotel")

    def __repr__(self) -> str:
        return f"{_('Albergo')}: {self.name} - {self.town}"


class PhoneNumber(db.Model):
    # __tablename__ = 'phone_number'

    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str] = mapped_column(String(24))
    href_phone: Mapped[str] = mapped_column(String(16), unique=True)
    hotel: Mapped[List[Hotel]] = relationship(secondary=association_table, back_populates="phones")

    def __repr__(self) -> str:
        return f"{_('Telefono')} {self.href_phone}"
