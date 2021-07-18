import argparse
import sys
import time

import numpy as np
import pandas as pd

from matchms import calculate_scores

from matchms.exporting import save_as_mgf

from matchms.filtering import add_precursor_mz
from matchms.filtering import default_filters
from matchms.filtering import normalize_intensities

from matchms.importing import load_from_mgf

from matchms.similarity import CosineGreedy
from matchms.similarity import PrecursorMzMatch

from tqdm.contrib import tzip

from mandelbrot_spectral_lib_matcher.nostdout import nostdout

# These numbers are only in effect when running the program as a script
DEFAULT_MS_TOLERANCE = 0.01
DEFAULT_MSMS_TOLERANCE = 0.01
DEFAULT_MIN_COSINE_SCORE = 0.2
DEFAULT_MIN_PEAKS = 6


def log(string: str):
    if verbose:
        print(string)


def metadata_processing(spectrum):
    spectrum = default_filters(spectrum)
    return spectrum


def minimal_processing(spectrum):
    spectrum = default_filters(spectrum)
    return spectrum


def peak_processing(spectrum):
    spectrum = default_filters(spectrum)
    spectrum = normalize_intensities(spectrum)
    return spectrum


def process_query(spectra):
    return [peak_processing(metadata_processing(s)) for s in spectra]


def minimal_process_query(spectra):
    return [minimal_processing(s) for s in spectra]


def process(spectra_query, spectra_db, parent_mz_tolerance, msms_mz_tolerance, min_cosine, min_peaks):
    similarity_score = PrecursorMzMatch(tolerance=parent_mz_tolerance, tolerance_type="Dalton")
    scores = calculate_scores(spectra_query, spectra_db, similarity_score)
    indices = np.where(np.asarray(scores.scores))
    idx_row, idx_col = indices
    cosine_greedy = CosineGreedy(tolerance=msms_mz_tolerance)
    data = []

    for (x, y) in tzip(idx_row, idx_col):
        msms_score, n_matches = cosine_greedy.pair(spectra_query[x], spectra_db[y])[()]
        if (msms_score > min_cosine) & (n_matches > min_peaks):
            data.append({'msms_score': msms_score,
                         'matched_peaks': n_matches,
                         # Get the feature_id or generate one
                         'feature_id': spectra_query[x].get("feature_id") or x + 1,
                         'short_inchikey': spectra_db[y].get("name")})
    return pd.DataFrame(data)


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
                        help="aditional cleaning step on the database file")
    parser.add_argument("-v", action='store_true',
                        help="print additional details to stdout")

    args = parser.parse_args()

    cleaning = args.c

    verbose = args.v

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
    database = sum([list(load_from_mgf(i)) for i in args.db_files], [])

    log("Cleaning query")
    with nostdout(verbose):
        query = process_query(query)

    if cleaning:
        log("Cleaning database")

        with nostdout(verbose):
            database = process_query(database)
    else:
        log("Minimally cleaning database")
        database = minimal_process_query(database)
    print(type(database))
    log('Your query spectra will be matched against the %s spectra of the spectral library.' % len(database))

    log("Processing")
    df = process(query, database, args.parent_mz_tolerance, args.msms_mz_tolerance, args.min_cosine_score,
                 args.min_peaks)
    df.to_csv(args.o, sep='\t', index=False)

    if verbose:
        log(f"Finished in {time.time() - start_time} seconds.")
        log(f"You can check your results in here {args.o[0]}")

    # if cleaning:
    #    save_as_mgf(spectra_db, "ISDB_averaged_cleaned_pos.mgf")

    sys.exit(0)
