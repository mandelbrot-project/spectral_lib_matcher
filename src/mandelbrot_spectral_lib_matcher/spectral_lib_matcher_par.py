import argparse
import numpy as np
import pandas as pd
import sys
import time
import tqdm


from matchms.importing import load_from_mgf

from matchms.filtering import default_filters
from matchms.filtering import normalize_intensities

from matchms.similarity import PrecursorMzMatch
from matchms import calculate_scores
from matchms.similarity import CosineGreedy

from nostdout import nostdout

from tqdm.contrib import tzip
from time import sleep




DEFAULT_MS_TOLERANCE = 0.01
DEFAULT_MSMS_TOLERANCE = 0.01
DEFAULT_MIN_COSINE_SCORE = 0.2
DEFAULT_MIN_PEAKS = 6

parser = argparse.ArgumentParser(description="Match two mgf files")
parser.add_argument("query_file", metavar='query.mgf', type=str, nargs=1,
                    help="the source MGF file")
parser.add_argument("db_files", metavar='database.mgf', type=str, nargs='+',
                    help="the database(s) MGF file")
parser.add_argument("-o", metavar='file.out', type=str, nargs=1,
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
parser.add_argument("-v", action='store_true',
                    help="print additional details to stdout")

args = parser.parse_args()

verbose = args.v


def log(string: str):
    if verbose:
        print(string)


log(f"Parsing spectral file {args.query_file[0]} against: {args.db_files[0]}")
log(f"Output file: {args.o[0]}")
log("Parameters:")
log(f" Parent tolerance (MS): {args.parent_mz_tolerance}")
log(f" MSMS tolerance: {args.msms_mz_tolerance}")
log(f" Minimal cosine score: {args.min_cosine_score}")
log(f" Minimum number of peaks: {args.min_peaks}")

if verbose:
    start_time = time.time()

log("Loading query file")
spectra_query = list(load_from_mgf(args.query_file[0]))
log('%s spectra found in the query file.' % len(spectra_query))
log("Loading DB files")
spectra_db = sum([list(load_from_mgf(i)) for i in args.db_files], [])
log('Your query spectra will be matched against the %s spectra of the spectral library.' % len(spectra_db))


def metadata_processing(spectrum):
    spectrum = default_filters(spectrum)
    return spectrum


def peak_processing(spectrum):
    spectrum = default_filters(spectrum)
    spectrum = normalize_intensities(spectrum)
    return spectrum


def process_query(spectra):
    return [peak_processing(metadata_processing(s)) for s in spectra]


log("Cleaning query")

with nostdout(verbose):
    spectra_query = process_query(spectra_query)

log("Cleaning database")

with nostdout(verbose):
    spectra_db = process_query(spectra_db)

log("Processing")

similarity_score = PrecursorMzMatch(tolerance=args.parent_mz_tolerance, tolerance_type="Dalton")
scores = calculate_scores(spectra_query, spectra_db, similarity_score)
indices = np.where(np.asarray(scores.scores))
idx_row, idx_col = indices
cosine_greedy = CosineGreedy(tolerance=args.msms_mz_tolerance)
data = []

# for (x, y) in tzip(idx_row, idx_col):
    # sleep(0.1)
# for (x, y) in zip(idx_row, idx_col):
for (x, y) in tzip(idx_row, idx_col):
    if x < y:
        msms_score, n_matches = cosine_greedy.pair(spectra_query[x], spectra_db[y])[()]
        if (msms_score > args.min_cosine_score) & (n_matches > args.min_peaks):
            data.append({'msms_score': msms_score,
                         'matched_peaks': n_matches,
                         'feature_id': x + 1,
                         'reference_id': y + 1,
                         'inchikey': spectra_db[y].get("name")})
df = pd.DataFrame(data)

df.to_csv(args.o[0], sep='\t')

if verbose:
    log(f"Finished in {time.time() - start_time} seconds.")
    log(f"You can check your results in here {args.o[0]}")

sys.exit(0)


