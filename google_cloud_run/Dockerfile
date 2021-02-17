# Use an official Python image.
# https://hub.docker.com/_/python
FROM python:3.9

WORKDIR /usr/src/app/

RUN pwd

COPY . .

RUN pip install -r google-cloud-run/requirements.txt

# Copy local code to the container image.

# Service must listen to $PORT environment variable.
# This default value facilitates local development.
ARG REDIS_URL_ADDRESS

ENV REDIS_URL=$REDIS_URL_ADDRESS
ENV PORT 8080

# Setting this ensures print statements and log messages
# promptly appear in Cloud Logging.
ENV PYTHONUNBUFFERED TRUE

RUN python3 manage.py collectstatic

CMD exec python3 manage.py runserver 0.0.0.0:$PORT