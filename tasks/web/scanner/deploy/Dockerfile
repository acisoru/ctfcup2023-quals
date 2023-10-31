FROM python:3.11-bullseye

RUN useradd -UMs /bin/bash serveruser
RUN apt update && apt install -y supervisor redis-server dnsutils

WORKDIR /usr/src/

COPY src/requirements.txt /usr/src/

RUN pip3 install -r requirements.txt

COPY src /usr/src

COPY conf/supervisord.conf /supervisord.conf
COPY entry.sh .

RUN chmod -R 755 /usr/src/

CMD ["./entry.sh"]
