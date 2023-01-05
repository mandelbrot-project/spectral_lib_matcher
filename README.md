# Spectral library matcher

A script based on the [matchms](https://github.com/matchms/matchms) library allowing to calculate spectral similarity measures between two mgf (usually a query file and a library file). 
A library of natural products in silico generated spectra is availabe here: <https://doi.org/10.5281/zenodo.5607185>

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
python src/processor.py [-h] [-g] [-o file.out] [--parent_mz_tolerance [-p]] [--msms_mz_tolerance [-m]] [--min_score [-s]] [--similarity_method [-z]] [--min_peaks [-k]] [-c] [-v]
                    query.mgf database.mgf [database.mgf ...]
```

positional arguments:

* query.mgf the source MGF file or GNPS job ID (if -g == True)
* database.mgf the database(s) MGF or binary format

optional arguments:

* -h, --help show this help message and exit
* -g specifies that GNPS is the source of the query_file
* -o file.out output file
* --parent_mz_tolerance [-p], -p [-p]
  * tolerance for the parent ion (MS) (default 0.01)
* --msms_mz_tolerance [-m], -m [-m]
  * tolerance for the MS/MS ions (default 0.01)
* --min_score [-s], -s [-s]
  * minimal score to consider (default 0.2)
* --similarity_method [-z], -z [-z]
  * similarity method used to perform spectral matching (default ModifiedCosine)
* --min_peaks [-k], -k [-k]
  * minimal number of peaks to consider (default 6)
* -c additional cleaning step on the database file
* -v print additional details to stdout

### Command line example:

```shell
python src/processor.py -v -o data/annotations.tsv -p 0.01 -m 0.01 -s 0.2 -k 6 -z ModifiedCosine data/query.mgf data/spectral_lib.mgf 
```

Using the -g argument you can alternatively use a GNPS job id for a direct download of the spectral file

```shell
python src/processor.py -v -g -o data/annotations.tsv -p 0.01 -m 0.01 -s 0.2 -k 6 -z ModifiedCosine d7a9cacf9ccd4510a04d119ab1561ea5 data/spectral_lib.mdbl 
```

If you want to compare two MGF's without structural annotation, use the `--index true` argument to match indices (feature_id's) instead.

```shell
python src/processor.py -v -g -o data/annotations.tsv -p 0.01 -m 0.01 -s 0.2 -k 6 -z ModifiedCosine data/query.mgf data/spectral_lib.mgf -i true
```

## Using binary libraries

To accelerate the matching especially when always using the same library, it is possible to use specialy crafted binary
libraries. Under the hood, it is a Python pickle object but with a custom header on the file (because we found some MGF
files that pickle would unmarshal)

### Create a binary library

```shell
python  src/binary_library_builder.py -v -o data/spectral_lib.mdbl data/spectral_lib.mgf
```

### Use a binary library

There is nothing special to do, the processor will detect automatically if your library is a mgf or a binary.

```shell
python src/processor.py -v -o data/annotations.tsv -p 0.01 -m 0.01 -s 0.2 -k 6 -z ModifiedCosine data/query.mgf data/spectral_lib.mdbl  
```

### For the h4ck3rs

You can also use `Spec2Vec` and `MS2DeepScore`.
Therefore, you'll need to either train your own models or get them from Zenodo as indicated in the respective
repositories (and store them in `models/`).
This part experimental and we won't offer support for it.

## Citations

Depending on which parts you used, do not forget to cite:

- matchms: https://doi.org/10.21105/joss.02411
- spec2vec: https://doi.org/10.1371/journal.pcbi.1008724
- ms2deepscore: https://doi.org/10.1186/s13321-021-00558-4
