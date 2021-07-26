FROM continuumio/miniconda3

WORKDIR /app

RUN mkdir -p /app
COPY environment.yml /app
RUN conda update -n base -c defaults conda && conda env create -f environment.yml
RUN echo "conda activate spectral_lib_matcher" >> ~/.bashrc
COPY . /app
SHELL ["/bin/bash", "--login", "-c"]
RUN ./scripts/run_tests.sh
