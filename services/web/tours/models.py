from __future__ import annotations

import enum
from datetime import date, time, datetime
from . import db, Base
from sqlalchemy import Table, Column, String, BOOLEAN, INT, FLOAT, DATE, TIMESTAMP, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from typing import List


class TripMode(str, enum.Enum):
    WALKING = "walking"
    BICYCLING = "bicycling"
    DRIVING = "driving"


class MediaType(str, enum.Enum):
    VIDEO = "video"
    IMAGE = "image"


class CheckInOutType(str, enum.Enum):
    IN = "check_in"
    OUT = "check_out"


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
    trip_mode: Mapped[TripMode] = mapped_column(Enum(TripMode, name="trip_mode_enum", native_enum=True), default='walking')
    is_visible: Mapped[bool | None] = mapped_column(BOOLEAN, default=True)
    trip_pic: Mapped[str | None] = mapped_column(String(96))
    pic_caption: Mapped[str | None] = mapped_column(String(128))
    carousel_pos: Mapped[int | None]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped[User] = relationship(back_populates="tours")
    laps: Mapped[List[Lap]] = relationship(back_populates="tour", order_by="Lap.date")

    __table_args__ = (UniqueConstraint('name', 'trip_mode', name='name_mode_uc'),)

    def __repr__(self) -> str:
        return f"{self.name}"


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
    # main gpx
    primary_gpx: Mapped[str | None] = mapped_column(String(64))
    done: Mapped[bool | None] = mapped_column(BOOLEAN, default=False)
    tour_id: Mapped[int] = mapped_column(ForeignKey("tour.id"))
    tour: Mapped[Tour] = relationship(back_populates="laps")

    other_gpx: Mapped[List[Gpx]] = relationship(back_populates="lap")
    pois: Mapped[List[POI]] = relationship(back_populates="lap")
    hotels: Mapped[List[Hotel]] = relationship(back_populates="lap")
    photos: Mapped[List[Media]] = relationship(back_populates="lap", order_by="Media.date")

    __table_args__ = (UniqueConstraint('tour_id', 'date', name='tour_lap_at_date_uc'),)

    def __repr__(self) -> str:
        return f"{self.start}-{self.destination}  {self.date}."


class Gpx(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    gpx: Mapped[str] = mapped_column(String(64))
    caption: Mapped[str | None] = mapped_column(String(32))
    lap_id: Mapped[int] = mapped_column(ForeignKey("lap.id"))
    lap: Mapped[Lap] = relationship(back_populates="other_gpx")

    __table_args__ = (UniqueConstraint('lap_id', 'gpx', name='lap_gpx_uc'),)


class POI(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    poi: Mapped[str] = mapped_column(String(128))
    at_km: Mapped[float | None]
    position: Mapped[int]
    lap_id: Mapped[int] = mapped_column(ForeignKey("lap.id"))
    lap: Mapped[Lap] = relationship(back_populates="pois")


class Media(db.Model):
    # __tablename__ = 'media'

    id: Mapped[int] = mapped_column(primary_key=True)
    media_src: Mapped[str] = mapped_column(String(96))
    media_width: Mapped[int | None]
    media_height: Mapped[int | None]
    media_type: Mapped[MediaType | None] = mapped_column(Enum(MediaType, name="media_type_enum", native_enum=True))
    date: Mapped[datetime] = mapped_column(TIMESTAMP)
    lat: Mapped[float | None] = mapped_column(FLOAT)
    long: Mapped[float | None] = mapped_column(FLOAT)
    caption: Mapped[str | None] = mapped_column(String(128))
    lap_id: Mapped[int] = mapped_column(ForeignKey("lap.id"))
    lap: Mapped[Lap] = relationship(back_populates="photos")

    __table_args__ = (UniqueConstraint('lap_id', 'media_src', name='lap_media_uc'), )

    def __repr__(self) -> str:
        return f"{self.media_src[: -4]}"


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
    reserved: Mapped[bool | None] = mapped_column(BOOLEAN, default=False)
    # check_in: Mapped[date | None]
    # check_out : Mapped[date | None]
    price: Mapped[int | None]
    photo: Mapped[str | None] = mapped_column(String(48))
    link: Mapped[str | None]
    lat: Mapped[float | None]
    long: Mapped[float | None]
    lap_id: Mapped[int] = mapped_column(ForeignKey("lap.id"))
    lap: Mapped[Lap] = relationship(back_populates="hotels")
    phones: Mapped[List[PhoneNumber]] = relationship(secondary=association_table, back_populates="hotel")
    checks: Mapped[List[CheckInOut]] = relationship(back_populates="hotel", order_by="CheckInOut.date")

    def __repr__(self) -> str:
        return f"{self.name} - {self.town}"


class CheckInOut(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    check_type: Mapped[CheckInOutType] = mapped_column(Enum(CheckInOutType, name="checkinout_enum", native_enum=True))
    date: Mapped[date | None]
    after: Mapped[time | None]
    before: Mapped[time | None]
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotel.id"))
    hotel: Mapped[Hotel] = relationship(back_populates="checks")


class PhoneNumber(db.Model):
    # __tablename__ = 'phone_number'

    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str] = mapped_column(String(24))
    href_phone: Mapped[str] = mapped_column(String(16), unique=True)
    hotel: Mapped[List[Hotel]] = relationship(secondary=association_table, back_populates="phones")

    def __repr__(self) -> str:
        return f"Tel: {self.href_phone}"
