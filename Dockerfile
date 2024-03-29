FROM python:3.10
    
WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip install -e . --no-cache-dir 
RUN pip install pytest --no-cache-dir 
RUN pip install PyYAML --no-cache-dir # Missing in matchms new pipeline?
RUN python -m pytest

COPY . .
