#! venv/bin/python

from flask.cli import FlaskGroup, with_appcontext
from datetime import datetime, time
from locale import LC_ALL, setlocale
from json import load
from berlin_tour import create_app, db
from berlin_tour.models import Lap, Hotel

cli = FlaskGroup(create_app=create_app)
app = cli.create_app()


@cli.command("create_db")
def create_db():
    with app.app_context():
        db.drop_all()
        db.create_all()


@cli.command("populate_db")
def populate_db():
    setlocale(LC_ALL, 'it_IT.UTF-8')

    with open("berlin_tour/progetto.json") as IN:
        laps = load(IN)

    with app.app_context():
        for lap in laps:
            new_hotel = Hotel(name=lap['Alloggio'],
                              address=lap['Indirizzo'],
                              town=lap['End'],
                              check_in=datetime.strptime(lap['Check-in'], "%a %d %b %Y").date(),
                              check_out=datetime.strptime(lap['Check-out'], "%a %d %b %Y").date(),
                              price=lap['Costo'],
                              photo=lap['Photo'],
                              link=lap['Booking']
                              )
            new_hotel.laps = [Lap(date=datetime.strptime(lap['Data'], "%a %d %b %Y").date(),
                              start=lap['Start'],
                              destination=lap['End'],
                              distance=lap['Distanza'],
                              ascent=lap['Ascesa'],
                              descent=lap['Discesa'],
                              duration=time.fromisoformat(lap['Tempo']),
                              gpx=lap['gpx']
                                  )
                              ]
            db.session.add(new_hotel)
            db.session.commit()


if __name__ == "__main__":
    cli()
