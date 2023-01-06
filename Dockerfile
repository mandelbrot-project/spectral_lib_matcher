FROM python:3.10
    
WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip install -e . --no-cache-dir 
RUN python -m pytest

COPY . .
