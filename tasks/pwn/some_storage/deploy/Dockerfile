FROM ubuntu:22.04@sha256:b492494d8e0113c4ad3fe4528a4b5ff89faa5331f7d52c5c138196f69ce176a6 as builder

RUN apt update && apt install -y g++

WORKDIR build/

COPY ./some_storage.cpp .

RUN g++ -o ./some_storage ./some_storage.cpp


FROM ubuntu:22.04@sha256:b492494d8e0113c4ad3fe4528a4b5ff89faa5331f7d52c5c138196f69ce176a6

RUN apt update && apt install -y socat

RUN echo "nobody:x:1337:1337:::" > /etc/passwd
RUN echo "nobody::1337:nobody" > /etc/group

COPY --from=builder --chown=nobody:nobody /build/some_storage /some_storage

ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN touch /flag.txt && chmod o+w /flag.txt

WORKDIR /
USER nobody

CMD [ "/entrypoint.sh" ]