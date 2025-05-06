###########
# BUILDER #
###########

# pull the official base image
FROM python:3.12.8-slim-bookworm AS builder

# set the work directory
WORKDIR /usr/src/app

# set the environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

# lint
RUN pip install --upgrade pip
RUN pip install flake8
COPY . /usr/src/app/
RUN flake8 --ignore=E127,E501,F401,E711 .

# install python dependecies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

#########
# FINAL #
#########

# pull official base image for python
FROM python:3.12.8-slim-bookworm

# install system dependencies
RUN apt-get update && apt-get install -y locales bind9-dnsutils postgresql-client && rm -r /var/lib/apt/lists/*
RUN sed -Ei 's/^#[[:blank:]]*(it_IT[.]U.*)/\1/' /etc/locale.gen && sed -Ei 's/^#[[:blank:]]*(en_GB[.]U.*)/\1/' /etc/locale.gen && dpkg-reconfigure --frontend=noninteractive locales


# create the user "flasker"
# NOTE: flasker is the user that will own the application and run it in the container
RUN addgroup --system flasker && adduser --system --group flasker

# create the home directory for flasker
RUN mkdir -p /home/flasker

# create the appropriate directories
ENV HOME=/home/flasker
ENV APP_HOME=/home/flasker/web
RUN mkdir -p ${APP_HOME} && mkdir ${APP_HOME}/logs

WORKDIR $APP_HOME

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd imagemagick libimage-exiftool-perl && apt-get purge expat
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy entrypoint
COPY ./entrypoint.sh ${APP_HOME}

# copy flaskr
COPY . ${APP_HOME}

# chown all the file to the flasker user
RUN chown -R flasker:flasker ${APP_HOME}

# change to the app user
USER flasker

EXPOSE 10000

CMD  ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:10000", "wsgi:app", "--timeout", "60", "--access-logfile", "/home/flasker/web/logs/gunicorn-access.log", "--error-logfile", "/home/flasker/web/logs/gunicorn-error.log", "--timeout", "60"]

# run entrypoint.sh
ENTRYPOINT ["/home/flasker/web/entrypoint.sh"]
