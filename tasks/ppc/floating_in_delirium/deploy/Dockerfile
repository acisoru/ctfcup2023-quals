FROM python:3.10-alpine

RUN apk add --no-cache socat

ADD delirium.py /
RUN chmod +x /delirium.py

USER nobody

CMD [ "socat", "TCP-LISTEN:2112,reuseaddr,fork", "EXEC:/delirium.py" ]
