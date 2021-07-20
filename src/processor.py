import argparse
import pickle
import sys
import time

from mandelbrot_spectral_lib_matcher.nostdout import nostdout
from mandelbrot_spectral_lib_matcher import logBuilder
from mandelbrot_spectral_lib_matcher.processor import process_query, minimal_process_query, process

from matchms.importing import load_from_mgf

# These numbers are only in effect when running the program as a script
from mandelbrot_spectral_lib_matcher.binary import read_binary_database

DEFAULT_MS_TOLERANCE = 0.01
DEFAULT_MSMS_TOLERANCE = 0.01
DEFAULT_MIN_COSINE_SCORE = 0.2
DEFAULT_MIN_PEAKS = 6

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Match two mgf files")
    parser.add_argument("query_file", metavar='query.mgf', type=str, nargs=1,
                        help="the source MGF file")
    parser.add_argument("db_files", metavar='database.mgf', type=str, nargs='+',
                        help="the database(s) MGF file")
    parser.add_argument("-o", metavar='file.out', type=str, default=sys.stdout,
                        help="output file")
    parser.add_argument("--parent_mz_tolerance", metavar='-p', type=float, nargs='?',
                        help=f"tolerance for the parent ion (MS) (default {DEFAULT_MS_TOLERANCE})",
                        default=DEFAULT_MS_TOLERANCE)
    parser.add_argument("--msms_mz_tolerance", metavar='-m', type=float, nargs='?',
                        help=f"tolerance for the MS/MS ions (default {DEFAULT_MSMS_TOLERANCE})",
                        default=DEFAULT_MSMS_TOLERANCE)
    parser.add_argument("--min_cosine_score", metavar='-c', type=float, nargs='?',
                        help=f"minimal cosine score to consider (default {DEFAULT_MIN_COSINE_SCORE})",
                        default=DEFAULT_MIN_COSINE_SCORE)
    parser.add_argument("--min_peaks", metavar='-k', type=int, nargs='?',
                        help=f"minimal number of peaks to consider (default {DEFAULT_MIN_PEAKS})",
                        default=DEFAULT_MIN_PEAKS)
    parser.add_argument("-c", action='store_true',
                        help="additional cleaning step on the database file")
    parser.add_argument("-v", action='store_true',
                        help="print additional details to stdout")

    args = parser.parse_args()

    cleaning = args.c

    verbose = args.v

    log = logBuilder.logBuilder(verbose)

    log(f"Parsing spectral file {args.query_file[0]} against: {args.db_files[0]}")
    log(f"Output file: {args.o}")
    log("Parameters:")
    log(f" Parent tolerance (MS): {args.parent_mz_tolerance}")
    log(f" MSMS tolerance: {args.msms_mz_tolerance}")
    log(f" Minimal cosine score: {args.min_cosine_score}")
    log(f" Minimum number of peaks: {args.min_peaks}")

    if verbose:
        start_time = time.time()

    log("Loading query file")
    query = list(load_from_mgf(args.query_file[0]))

    log('%s spectra found in the query file.' % len(query))
    log("Loading DB files")
    database = []
    for i in args.db_files:
        with open(i, "rb") as file:
            # We search for the header of our special format
            # we do that because somehow pickle can read some of our MGF files as a pickle file…
            log(f"Loading: {i}")
            output = read_binary_database(file)
            if output is None:
                file.seek(0)  # We go back to the beginning of the file
                new_db = list(load_from_mgf(i))

                if cleaning:
                    log(" Cleaning database")

                    with nostdout(verbose):
                        new_db = process_query(new_db)
                else:
                    log(" Minimally cleaning database")
                    new_db = minimal_process_query(new_db)
                database += new_db
            else:
                database += output
    # database = sum([list(load_from_mgf(i)) for i in args.db_files], [])

    log("Cleaning query")
    with nostdout(verbose):
        query = process_query(query)

    log('Your query spectra will be matched against the %s spectra of the spectral library.' % len(database))

    log("Processing")
    df = process(query, database, args.parent_mz_tolerance, args.msms_mz_tolerance, args.min_cosine_score,
                 args.min_peaks)
    df.to_csv(args.o, sep='\t', compression='gzip', index=False)

    if verbose:
        log(f"Finished in {time.time() - start_time:.2f} seconds.")
        log(f"You can check your results in here {args.o}")

    # if cleaning:
    #    save_as_mgf(spectra_db, "ISDB_averaged_cleaned_pos.mgf")

    sys.exit(0)
