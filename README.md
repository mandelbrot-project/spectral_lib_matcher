# Spectral library matcher

A script based on the matchms library allowing to calculate spectral similarity measures between two mgf (usually a
query file and a library file).

## Requirements

### With conda

You can create a conda environment with environment.yml.

```shell
conda env create -f environment.yml
```

and activate it 

```shell
conda activate spectral_lib_matcher
```


### With docker.

```shell
docker build -t spectrallibmatcher .
```

```shell
docker run -it --rm -v $PWD:/app spectrallibmatcher bash
```

Run the tests to check that everything works:

```shell
docker run -it --rm -v $PWD:/app spectrallibmatcher bash --login scripts/run_tests
```

## Running the spectral matching

```
usage: processor.py [-h] [-o file.out] [--parent_mz_tolerance [-p]] [--msms_mz_tolerance [-m]] [--min_cosine_score [-c]] [--min_peaks [-k]] [-c] [-v] query.mgf database.mgf [database.mgf ...]
```

positional arguments:
  * query.mgf             the source MGF file or GNPS job ID (if -g == True)
  * database.mgf          the database(s) MGF or binary format

optional arguments:
  * -h, --help            show this help message and exit
  * -g                    specifies that GNPS is the source of the query_file
  * -o file.out           output file
  * --parent_mz_tolerance [-p], -p [-p]
                        * tolerance for the parent ion (MS) (default 0.01)
  * --msms_mz_tolerance [-m], -m [-m]
                        * tolerance for the MS/MS ions (default 0.01)
  * --min_cosine_score [-s], -s [-s]
                        * minimal cosine score to consider (default 0.2)
  * --min_peaks [-k], -k [-k]
                        * minimal number of peaks to consider (default 6)
  * -c                    additional cleaning step on the database file
  * -v                    print additional details to stdout

Command line example:

```shell
python src/processor.py -v -o path/to/your/results_file.tsv -p 0.01 -m 0.01 -c 0.2 -k 6 query.mgf database.mgf  
```

## Using binary libraries

To accelerate the matching especially when always using the same library, it is possible to use specialy crafted binary
libraries. Under the hood, it is a Python pickle object but with a custom header on the file (because we found some MGF
files that pickle would unmarshal)

### Create a binary library

```shell
python  src/binary_library_builder.py -v -o yourdatabase.mdbl yourdatabase.mgf
```

### Use a binary library

There is nothing special to do, the processor will detect automatically if your library is a mgf or a binary.

```shell
python src/processor.py -v -o path/to/your/results_file.tsv -p 0.01 -m 0.01 -c 0.2 -k 6 query_spectra.mgf yourdatabase.mdbl  
```

## More on matchms

You can follow Florian Huber excellent tutorial
here https://blog.esciencecenter.nl/build-your-own-mass-spectrometry-analysis-pipeline-in-python-using-matchms-part-i-d96c718c68ee
