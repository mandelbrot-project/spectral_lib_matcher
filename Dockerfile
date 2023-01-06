FROM python:3.10.0-alpine
    
WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip install . --no-cache-dir 
    
COPY . .

SHELL ["/bin/bash", "--login", "-c"]

RUN ./scripts/run_tests.sh
