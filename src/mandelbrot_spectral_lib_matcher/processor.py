import gensim
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

from ms2deepscore import MS2DeepScore
from ms2deepscore.models import load_model
from spec2vec import Spec2Vec

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


def process(spectra_query, spectra_db, parent_mz_tolerance=0.01, msms_mz_tolerance=0.01, min_score=0.2, min_peaks=6,
            similarity_method="ModifiedCosine", index=False):
    newMethods = ["Spec2Vec", "MS2DeepScore"]
    similarity_score = PrecursorMzMatch(tolerance=parent_mz_tolerance, tolerance_type="Dalton")
    scores = calculate_scores(references=spectra_query, queries=spectra_db, array_type="numpy",is_symmetric=False, similarity_function=similarity_score)
    indices = np.where(np.asarray(scores.scores.to_array()))
    idx_row, idx_col = indices
    spectral_similarity = eval(similarity_method)
    method_name = spectral_similarity.__name__

    if (method_name not in newMethods):
        spectral_similarity = spectral_similarity(tolerance=msms_mz_tolerance)
    elif (method_name == "Spec2Vec"):
        spectral_similarity = spectral_similarity(
            model=gensim.models.Word2Vec.load("models/spec2vec_AllPositive_ratio05_filtered_201101_iter_15.model"),
            intensity_weighting_power=0.5, allowed_missing_percentage=5.0)
        spectra_db = process_query(spectra_db)
    else:
        spectral_similarity = spectral_similarity(
            model=load_model("models/MS2DeepScore_allGNPSpositive_10k_500_500_200.hdf5"))

    data = []

    for (x, y) in tzip(idx_row, idx_col):
        if (method_name not in newMethods):
            msms_score, n_matches = spectral_similarity.pair(spectra_query[x], spectra_db[y])[()]
        else:
            msms_score = spectral_similarity.pair(spectra_query[x], spectra_db[y])
            cosine_score, n_matches = ModifiedCosine(tolerance=msms_mz_tolerance).pair(spectra_query[x], spectra_db[y])[
                ()]
        if (msms_score > min_score) & (n_matches > min_peaks):
            if index:
                data.append({'msms_score': msms_score,
                             'matched_peaks': n_matches,
                             'matched_ratio' : n_matches / max(len(spectra_query[x].peaks.intensities), len(spectra_db[y].peaks.intensities)),
                             'feature_id': spectra_query[x].get("feature_id") or x + 1,
                             'target_id': spectra_db[y].get("feature_id") or y + 1
                             })
            else:
                data.append({'msms_score': msms_score,
                             'matched_peaks': n_matches,
                             'matched_ratio' : n_matches / max(len(spectra_query[x].peaks.intensities), len(spectra_db[y].peaks.intensities)),
                              # Get the feature_id or generate one
                             'feature_id': spectra_query[x].get("feature_id") or x + 1,
                             'short_inchikey': spectra_db[y].get("compound_name"),
                             'smiles': spectra_db[y].get("smiles"),
                             'molecular_formula': spectra_db[y].get("molecular_formula"),
                             'exact_mass': spectra_db[y].get("parent_mass")
                             })

    return pd.DataFrame(data)
