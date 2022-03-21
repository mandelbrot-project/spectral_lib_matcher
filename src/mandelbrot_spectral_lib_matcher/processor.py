import numpy as np
import pandas as pd

from matchms import calculate_scores

from matchms.filtering import default_filters
from matchms.filtering import normalize_intensities

from matchms.similarity import CosineGreedy
from matchms.similarity import CosineHungarian
from matchms.similarity import ModifiedCosine
from matchms.similarity import NeutralLossesCosine
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


def process(spectra_query, spectra_db, parent_mz_tolerance=0.01, msms_mz_tolerance=0.01, min_score=0.2, min_peaks=6, similarity_method="ModifiedCosine"):
    similarity_score = PrecursorMzMatch(tolerance=parent_mz_tolerance, tolerance_type="Dalton")
    scores = calculate_scores(spectra_query, spectra_db, similarity_score)
    indices = np.where(np.asarray(scores.scores))
    idx_row, idx_col = indices
    spectral_similarity = eval(similarity_method)(tolerance=msms_mz_tolerance)
    data = []

    for (x, y) in tzip(idx_row, idx_col):
        msms_score, n_matches = spectral_similarity.pair(spectra_query[x], spectra_db[y])[()]
        if (msms_score > min_score) & (n_matches > min_peaks):
            data.append({'msms_score': msms_score,
                         'matched_peaks': n_matches,
                         # Get the feature_id or generate one
                         'feature_id': spectra_query[x].get("scans") or x + 1,
                         'short_inchikey': spectra_db[y].get("compound_name"),
                         'smiles': spectra_db[y].get("smiles"),
                         'molecular_formula': spectra_db[y].get("molecular_formula"),
                         'exact_mass': spectra_db[y].get("parent_mass")
                        })
    return pd.DataFrame(data)
