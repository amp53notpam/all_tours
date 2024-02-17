#! /bin/sh

if [ "${DATABASE}" = "postgresql" ]
then
    echo "Waiting for PostgreSQL..."

    while ! nc -z ${SQL_HOST} ${SQL_PORT}; do
	sleep 0.1
    done
    
    echo "PostgreSQL started"

fi


if [ "$FLASK_ENV" = "development" -o "$FLASK_DEBUG"="1" ]
then
    echo "Creating the database tables..."
    python manage.py create_db
    echo "Done"
    echo "Populating the database..."
    python manage.py populate_db
    echo "Done"
fi

exec "$@"
