FROM golang:1.21.3-alpine3.18 AS server-builder

WORKDIR /build

RUN echo "nobody:x:1000:1000:::" > etcpasswd
RUN echo "nobody::1000:nobody" > etcgroup
RUN mkdir dir

COPY go.* .
COPY app app
COPY conf conf
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go install github.com/revel/cmd/revel@v1.1.0 && \
    CGO_ENABLED=0 GOOS=linux revel package .

WORKDIR /service
RUN tar xzvf /build/build.tar.gz

FROM node:21.0.0-alpine3.18 AS front-builder

WORKDIR /build
ENV NODE_ENV=production

COPY package.json package-lock.json .
RUN npm ci

COPY postcss.config.js tailwind.config.js .
COPY public public
COPY app/views app/views
RUN npm run build && rm -rf public/src

FROM ubuntu

COPY --from=server-builder /build/etcpasswd /etc/passwd
COPY --from=server-builder /build/etcgroup /etc/group
COPY --from=server-builder --chown=nobody:nobody /service /service
COPY --chown=nobody:nobody messages /service/src/novosti/messages
COPY --from=front-builder --chown=nobody:nobody /build/public /service/src/novosti/public
COPY --from=server-builder --chown=nobody:nobody --chmod=600 /build/dir /news
COPY --from=server-builder --chown=nobody:nobody --chmod=600 /build/dir /service/admin-secret

WORKDIR /service
USER nobody

CMD [ "/service/build", "-importPath", "novosti", "-srcPath", "/service/src", "-runMode", "prod" ]
