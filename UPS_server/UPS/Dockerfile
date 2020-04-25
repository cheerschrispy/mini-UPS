FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
RUN python3 -m pip install google
RUN python3 -m pip install protobuf
RUN python3 -m pip install psycopg2
ADD . /code/
