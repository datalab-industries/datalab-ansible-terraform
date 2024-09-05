FROM python:3.11-alpine AS builder
WORKDIR /app
RUN apk add --no-cache borgbackup mongodb-tools openssh
RUN pip install --user borgmatic
ENV PATH="$PATH:/root/.local/bin"

COPY config.yaml /etc/borgmatic/config.yaml

CMD ["borgmatic", "--verbosity", "1", "--config", "/etc/borgmatic/config.yaml"]
