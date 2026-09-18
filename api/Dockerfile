FROM python:3.12.3-alpine3.18

ENV PORT=5050
ENV PYTHONPATH=/api
ENV FLASK_APP=wsgi.py

RUN mkdir -p /api
WORKDIR /api
COPY . /api

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]