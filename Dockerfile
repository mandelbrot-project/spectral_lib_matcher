FROM python:3.11-alpine

WORKDIR /usr/src/app

COPY pyproject.toml /usr/src/app/
COPY environment.yml /usr/src/app/

RUN apk add --no-cache gcc musl-dev libffi-dev && \
    pip install --no-cache-dir -e . pytest PyYAML && \
    python -m pytest && \
    apk del gcc musl-dev libffi-dev

COPY . /usr/src/app