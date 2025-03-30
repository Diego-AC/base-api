#!/bin/sh

if [ "${WAIT_DB}" = 1 ]; then
  echo "Waiting for postgres..."

  while ! nc -z postgres 5432; do
    sleep 0.1
  done

  sleep 1

  echo "Postgre SQL started"
fi;

if [ "${FLASK_DEBUG}" = 1 ]; then
  flask run --host=0.0.0.0 --port=${PORT} --debug
fi;
