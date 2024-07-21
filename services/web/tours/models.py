from datetime import date, time
from . import db
from sqlalchemy import Integer, String, BOOLEAN, FLOAT, DATE, TIME, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from typing import Optional, List


class Tour(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    bind: Mapped[str] = mapped_column(String(32), unique=True)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=False)

    def __repr__(self) -> str:
        return self.name


class Lap(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(DATE, unique=True)
    start: Mapped[str] = mapped_column(String(32))
    destination: Mapped[str] = mapped_column(String(32))
    distance: Mapped[Optional[float]] = mapped_column(FLOAT, default=0)
    ascent: Mapped[Optional[int]]
    descent: Mapped[Optional[int]]
    duration: Mapped[Optional[time]]
    done: Mapped[Optional[bool]] = mapped_column(BOOLEAN, default=False)
    gpx: Mapped[Optional[str]] = mapped_column(String(48))
    tour_id: Mapped[int] = mapped_column(ForeignKey("tour.id"))
    hotels: Mapped[List["Hotel"]] = relationship(cascade="all, delete-orphan", back_populates="lap")

    def __repr__(self) -> str:
        return f"Tappa: {self.start}-{self.destination}  Giorno: {self.date}"


class Hotel(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(48))
    address: Mapped[str] = mapped_column(String(48))
    town: Mapped[str] = mapped_column(String(32))
    check_in: Mapped[date] = mapped_column(DATE)
    check_out: Mapped[Optional[date]] = mapped_column(DATE)
    reserved: Mapped[Optional[bool]] = mapped_column(BOOLEAN, default=False)
    price: Mapped[Optional[int]]
    photo: Mapped[Optional[str]] = mapped_column(String(48))
    link: Mapped[Optional[str]]
    lap_id: Mapped[int] = mapped_column(ForeignKey("lap.id"))
    lap: Mapped["Lap"] = relationship(back_populates="hotels")

    def __repr__(self) -> str:
        return f"Hotel: {self.name} - {self.town}"


class Admin(UserMixin, db.Model):
    __bind_key__ = 'db_sec'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str]

    def __repr__(self) -> str:
        return ("db administrator")
