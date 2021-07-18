import argparse
import pickle
import sys
import time

from matchms.importing import load_from_mgf

from mandelbrot_spectral_lib_matcher import logBuilder
from mandelbrot_spectral_lib_matcher.nostdout import nostdout
from mandelbrot_spectral_lib_matcher.processor import process_query, minimal_process_query
from mandelbrot_spectral_lib_matcher.binary import write_binary_database

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert mgf(s) to a preprocessed binary library")
    parser.add_argument("db_files", metavar='database.mgf', type=str, nargs='+',
                        help="the database(s) MGF file")
    parser.add_argument("-c", action='store_true',
                        help="additional cleaning step on the database file")
    parser.add_argument("-v", action='store_true',
                        help="print additional details to stdout")
    parser.add_argument("-o", metavar='file.out', type=str, required=True,
                        help="output file")

    args = parser.parse_args()
    cleaning = args.c

    verbose = args.v

    log = logBuilder.logBuilder(verbose)

    if verbose:
        start_time = time.time()

    log("Loading DB files")
    database = sum([list(load_from_mgf(i)) for i in args.db_files], [])

    if cleaning:
        log("Cleaning database")

        with nostdout(verbose):
            database = process_query(database)
    else:
        log("Minimally cleaning database")
        database = minimal_process_query(database)

    log('Your library will contain %s spectra.' % len(database))
    log('Be careful, your file may be specific to a given Python version! These are not meant to be distributed.')
    log('You should also never run a binary database file you received from untrusted parties!')
    log('TL;DR : Only use files you made yourself!')
    log('Writing')
    with open(args.o, "wb") as file:
        write_binary_database(database, file)

    if verbose:
        log(f"Finished in {(time.time() - start_time):.2f} seconds.")
        log(f"The database has been saved in {args.o}")

    sys.exit(0)
