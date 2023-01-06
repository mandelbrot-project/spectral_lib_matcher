FROM python:3
    
WORKDIR /usr/src/app

COPY setup.py /usr/src/app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install . --no-cache-dir 
    
COPY . .

SHELL ["/bin/bash", "--login", "-c"]

RUN ./scripts/run_tests.sh
