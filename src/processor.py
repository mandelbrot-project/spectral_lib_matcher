import requests
import sys
import time

from matchms.importing import load_from_mgf

# These numbers are only in effect when running the program as a script
from mandelbrot_spectral_lib_matcher.binary import read_binary_database
from mandelbrot_spectral_lib_matcher.nostdout import nostdout
from mandelbrot_spectral_lib_matcher.processor import process_query, minimal_process_query, process

DEFAULT_MS_TOLERANCE = 0.01
DEFAULT_MSMS_TOLERANCE = 0.01
DEFAULT_MIN_COSINE_SCORE = 0.2
DEFAULT_MIN_PEAKS = 6


class ProcessorConfig:
    query_file = None
    db_files = None
    gnps_job = False
    output_file = None
    verbose = True
    cleaning = True
    parent_mz_tolerance = DEFAULT_MS_TOLERANCE
    msms_mz_tolerance = DEFAULT_MSMS_TOLERANCE
    min_cosine_score = DEFAULT_MIN_COSINE_SCORE
    min_peaks = DEFAULT_MIN_PEAKS

    def __init__(self):
        self.db_files = []


def processor(log, config):
    log(f"Parsing spectral file {config.query_file} against: {config.db_files}")
    log(f"Output file: {config.output_file}")
    log("Parameters:")
    log(f" Parent tolerance (MS): {config.parent_mz_tolerance}")
    log(f" MSMS tolerance: {config.msms_mz_tolerance}")
    log(f" Minimal cosine score: {config.min_cosine_score}")
    log(f" Minimum number of peaks: {config.min_peaks}")

    if config.verbose:
        start_time = time.time()

    log("Loading query file")
    if config.gnps_job:
        url = 'http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=' + config.query_file[
            0] + '&block=main&file=spectra/specs_ms.mgf'
        mgf = requests.get(url).text
        log("Saving temporary file")
        print(mgf, file=open('data/' + config.query_file[0] + '.mgf', 'w'))
        query = list(load_from_mgf('data/' + config.query_file[0] + '.mgf'))
    else:
        query = list(load_from_mgf(config.query_file[0]))

    log('%s spectra found in the query file.' % len(query))
    log("Loading DB files")
    database = []
    for i in config.db_files:
        with open(i, "rb") as file:
            # We search for the header of our special format
            # we do that because somehow pickle can read some of our MGF files as a pickle file…
            log(f"Loading: {i}")
            output = read_binary_database(file)
            if output is None:
                file.seek(0)  # We go back to the beginning of the file
                new_db = list(load_from_mgf(i))

                if config.cleaning:
                    log(" Cleaning database")

                    with nostdout(config.verbose):
                        new_db = process_query(new_db)
                else:
                    log(" Minimally cleaning database")
                    new_db = minimal_process_query(new_db)
                database += new_db
            else:
                database += output
    # database = sum([list(load_from_mgf(i)) for i in args.db_files], [])

    log("Cleaning query")
    with nostdout(config.verbose):
        query = process_query(query)

    log('Your query spectra will be matched against the %s spectra of the spectral library.' % len(database))

    log("Processing")
    df = process(query, database, config.parent_mz_tolerance, config.msms_mz_tolerance, config.min_cosine_score,
                 config.min_peaks)

    df.to_csv(config.output_file, sep='\t', index=False)

    if config.verbose:
        log(f"Finished in {time.time() - start_time:.2f} seconds.")
        log(f"You can check your results in here {config.output_file}")

    # if cleaning:
    #    save_as_mgf(spectra_db, "ISDB_averaged_cleaned_pos.mgf")


if __name__ == '__main__':
    from mandelbrot_spectral_lib_matcher import logBuilder
    import argparse

    parser = argparse.ArgumentParser(description="Matches two mgf files")
    parser.add_argument("query_file", metavar='query.mgf', type=str, nargs=1,
                        help="the source MGF file or GNPS job ID (if -g == True)")
    parser.add_argument("db_files", metavar='database.mgf', type=str, nargs='+',
                        help="the database(s) MGF or binary format")
    parser.add_argument("-g", action='store_true',
                        help="specifies that GNPS is the source of the query_file")
    parser.add_argument("-o", metavar='file.out', type=str, default=sys.stdout,
                        help="output file")
    parser.add_argument("--parent_mz_tolerance",'-p', metavar='-p', type=float, nargs='?',
                        help=f"tolerance for the parent ion (MS) (default {DEFAULT_MS_TOLERANCE})",
                        default=DEFAULT_MS_TOLERANCE)
    parser.add_argument("--msms_mz_tolerance", '-m', metavar='-m', type=float, nargs='?',
                        help=f"tolerance for the MS/MS ions (default {DEFAULT_MSMS_TOLERANCE})",
                        default=DEFAULT_MSMS_TOLERANCE)
    parser.add_argument("--min_cosine_score", '-s', metavar='-s', type=float, nargs='?',
                        help=f"minimal cosine score to consider (default {DEFAULT_MIN_COSINE_SCORE})",
                        default=DEFAULT_MIN_COSINE_SCORE)
    parser.add_argument("--min_peaks",'-k', metavar='-k', type=int, nargs='?',
                        help=f"minimal number of peaks to consider (default {DEFAULT_MIN_PEAKS})",
                        default=DEFAULT_MIN_PEAKS)
    parser.add_argument("-c", action='store_true',
                        help="additional cleaning step on the database file")
    parser.add_argument("-v", action='store_true',
                        help="print additional details to stdout")

    args = parser.parse_args()

    config = ProcessorConfig()
    config.query_file = args.query_file
    config.db_files = args.db_files
    config.gnps_job = args.g
    config.output_file = args.o
    config.parent_mz_tolerance = args.parent_mz_tolerance
    config.msms_mz_tolerance = args.msms_mz_tolerance
    config.min_cosine_score = args.min_cosine_score
    config.min_peaks = args.min_peaks
    config.verbose = args.v
    config.cleaning = args.c

    log = logBuilder.logBuilder(config.verbose)

    processor(log, config)

    sys.exit(0)
