FROM openjdk:17-slim-bullseye AS builder

WORKDIR /app/
COPY twofac-demo/ .
RUN  ./gradlew --no-daemon build

FROM openjdk:17-slim-bullseye

COPY --from=builder /app/build/libs/twofac-demo-all.jar /app.jar

ENTRYPOINT ["java", "-jar", "/app.jar"]
