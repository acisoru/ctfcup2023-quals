FROM python:3.11.6-alpine3.18

RUN apk update && \
    apk upgrade && \
    apk add ffmpeg

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY voices voices
COPY *.py .

RUN chown -R nobody:nobody .
USER nobody

ENTRYPOINT [ "python3", "checkpoint.py" ]
