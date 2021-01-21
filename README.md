# Spectral library matcher

A script based on the matchms library allowing to calculate spectral similarity measures between two mgf (usually a query file and a library file).

## Requirements

You nedd to install matchms and activate the matchms environment.
See instruction here https://github.com/matchms/matchms

## Running the spectral matching 

The spectral_lib_matcher.py script takes 7 arguments. 

1. the path of the query spectral file (in .mgf format) you want to annotate
2. the path of the database spectral file (in .mgf format) you want to use for annotation
3. the parent mass tolerance (in Da)
4. the msms fragments mass tolerance (in Da)
5. the minimal cosine score to return a spectral match
6. the minimal number of peaks between query and database spectra to return a spectral match
7. the path of the annotation results file

Command line example

`python spectral_lib_matcher.py path/to/your/query_spectra.mgf path/to/your/database_spectra.mgf 0.01 0.01 0.2 6 path/to/your/results_file.tsv`


## More on matchms

You can follow Florian Huber excellent tutorial here https://blog.esciencecenter.nl/build-your-own-mass-spectrometry-analysis-pipeline-in-python-using-matchms-part-i-d96c718c68ee