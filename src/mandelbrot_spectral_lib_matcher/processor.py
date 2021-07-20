import numpy as np
import pandas as pd

from matchms import calculate_scores

from matchms.exporting import save_as_mgf

from matchms.filtering import add_precursor_mz
from matchms.filtering import default_filters
from matchms.filtering import normalize_intensities

from matchms.similarity import CosineGreedy
from matchms.similarity import PrecursorMzMatch

from tqdm.contrib import tzip


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
                         'feature_id': spectra_query[x].get("scans") or x + 1,
                         'short_inchikey': spectra_db[y].get("name"),
                         'smiles': spectra_db[y].get("smiles")})
    return pd.DataFrame(data)
