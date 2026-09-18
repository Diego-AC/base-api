#!/bin/sh

set -e

if [ "${WAIT_DB}" = 1 ]; then
  echo "Waiting for postgres..."

  while ! nc -z postgres 5432; do
    sleep 0.1
  done

  sleep 1

  echo "Postgre SQL started"
fi;

DEBUG_FLAG=""
if [ "${FLASK_DEBUG}" = "1" ] || [ "${FLASK_DEBUG}" = "true" ]; then
  DEBUG_FLAG="--debug"
fi

exec flask --app wsgi.py run --host=0.0.0.0 --port=${PORT} ${DEBUG_FLAG}
