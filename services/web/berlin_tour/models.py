from datetime import date, time
from . import db
from sqlalchemy import Integer, String, DATE, TIME, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List


class Hotel(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(48))
    address: Mapped[str] = mapped_column(String(48))
    town: Mapped[str] = mapped_column(String(32))
    check_in: Mapped[date] = mapped_column(DATE, unique=True)
    check_out: Mapped[date] = mapped_column(DATE, unique=True)
    price: Mapped[int]
    photo: Mapped[Optional[str]] = mapped_column(String(48))
    link: Mapped[Optional[str]]
    laps: Mapped[List["Lap"]] = relationship(back_populates="hotels")

    def __repr__(self) -> str:
        return f"Hetel: {self.name} - {self.town}"


class Lap(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(DATE, unique=True)
    start: Mapped[str] = mapped_column(String(32))
    destination: Mapped[str] = mapped_column(String(32))
    distance: Mapped[Optional[float]]
    ascent: Mapped[Optional[int]]
    descent: Mapped[Optional[int]]
    duration: Mapped[Optional[time]]
    gpx: Mapped[Optional[str]] = mapped_column(String(48))
    hotel_id = mapped_column(ForeignKey("hotel.id"))

    hotels: Mapped["Hotel"] = relationship(back_populates="laps")

    def __repr__(self) -> str:
        return f"Tappa: {self.start}-{self.destination}  Giorno: {self.date}"
