FROM debian:bullseye@sha256:3066ef83131c678999ce82e8473e8d017345a30f5573ad3e44f62e5c9c46442b

RUN apt-get update -qq
RUN apt-get upgrade --no-install-recommends -yqq
RUN apt-get install --no-install-recommends -yqq procps python3-pip uwsgi uwsgi-plugin-python3 python3-setuptools

WORKDIR /pinserver
COPY wsgi.ini requirements.txt wsgi.py server.py lib.py pindb.py __init__.py generateserverkey.py flaskserver.py /pinserver/
RUN pip3 install --upgrade pip wheel
RUN pip3 install --require-hashes -r /pinserver/requirements.txt

VOLUME /data
VOLUME /data/pins
WORKDIR /data
ENV PYTHONPATH=/

CMD ["uwsgi", "--ini", "/pinserver/wsgi.ini"]
