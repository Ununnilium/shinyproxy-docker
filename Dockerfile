# Runs ShinyProxy in a Docker container. Please make sure to mount the Docker socket as volume into
# /var/run/docker.sock.

FROM openjdk:8-jre-alpine
ENV SHINYPROXY_VERSION 1.1.0

RUN apk update && apk add --no-cache --virtual .run-deps python3 curl socat && \
    pip3 install --upgrade pip && \
    pip3 install docker==3.3.0 PyYAML==3.12 && \
    mkdir /shinyproxy && \
    curl -L https://github.com/openanalytics/shinyproxy/releases/download/v${SHINYPROXY_VERSION}/shinyproxy-${SHINYPROXY_VERSION}.jar > /shinyproxy/shinyproxy.jar && \
    rm /var/cache/apk/*
COPY application.yml /shinyproxy/
COPY shiny_start.py /shinyproxy/
EXPOSE 8080
WORKDIR /shinyproxy
CMD ["python3", "shiny_start.py"]
