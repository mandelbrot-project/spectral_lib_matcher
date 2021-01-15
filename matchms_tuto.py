import os
import numpy as np
from matchms.importing import load_from_mgf
path_data = "/Users/pma/Dropbox/Research_UNIGE/git_repos/spectral_tmap/benchmark_data/"  # enter path to downloaded mgf file
file_mgf = os.path.join(path_data, 
                        "DNP_ISDB_Apocynaceae_pos.mgf")
spectrums = list(load_from_mgf(file_mgf))

len(spectrums)

spectrums[0].metadata
spectrums[0].peaks.intensities

spectrums[4].get("smiles")


## Let's have a closer look at the metadata

inchikeys = [s.get("inchikey") for s in spectrums]
found_inchikeys = np.sum([1 for x in inchikeys if x is not None])
print(f"Found {int(found_inchikeys)} inchikeys in metadata")


## and at the peaks

numbers_of_peaks = [len(s.peaks.mz) for s in spectrums]
from matplotlib import pyplot as plt
plt.figure(figsize=(5,4), dpi=150)
plt.hist(numbers_of_peaks, 20, edgecolor="white")
plt.title("Peaks per spectrum (before filtering)")
plt.xlabel("Number of peaks in spectrum")
plt.ylabel("Number of spectra")

## pipeline

from matchms.filtering import default_filters
from matchms.filtering import repair_inchi_inchikey_smiles
from matchms.filtering import derive_inchikey_from_inchi
from matchms.filtering import derive_smiles_from_inchi
from matchms.filtering import derive_inchi_from_smiles
from matchms.filtering import harmonize_undefined_inchi
from matchms.filtering import harmonize_undefined_inchikey
from matchms.filtering import harmonize_undefined_smiles
def metadata_processing(spectrum):
    spectrum = default_filters(spectrum)
    spectrum = repair_inchi_inchikey_smiles(spectrum)
    spectrum = derive_inchi_from_smiles(spectrum)
    spectrum = derive_smiles_from_inchi(spectrum)
    spectrum = derive_inchikey_from_inchi(spectrum)
    spectrum = harmonize_undefined_smiles(spectrum)
    spectrum = harmonize_undefined_inchi(spectrum)
    spectrum = harmonize_undefined_inchikey(spectrum)
    return spectrum

from matchms.filtering import default_filters
from matchms.filtering import normalize_intensities
from matchms.filtering import select_by_intensity
from matchms.filtering import select_by_mz
def peak_processing(spectrum):
    spectrum = default_filters(spectrum)
    spectrum = normalize_intensities(spectrum)
    spectrum = select_by_intensity(spectrum, intensity_from=0.01)
    spectrum = select_by_mz(spectrum, mz_from=10, mz_to=1000)
    return spectrum

spectrums = [metadata_processing(s) for s in spectrums]
spectrums = [peak_processing(s) for s in spectrums]

inchikeys = [s.get("inchikey") for s in spectrums]
inchikeys[:10]


## scoring function 

from matchms import calculate_scores
from matchms.similarity import CosineGreedy
similarity_measure = CosineGreedy(tolerance=0.005)


scores = calculate_scores(spectrums, spectrums, similarity_measure, is_symmetric=True)

# checking the scores

scores.scores[:5, :5]["matches"]
scores.scores[:5, :5]["score"]


best_matches = scores.scores_by_query(spectrums[5], sort=True)[:10]
print([x[1] for x in best_matches])


[x[0].get("smiles") for x in best_matches]

from rdkit import Chem
from rdkit.Chem import Draw
for i, smiles in enumerate([x[0].get("smiles") for x in    best_matches]):
    m = Chem.MolFromSmiles(smiles)
    Draw.MolToFile(m, f"compound_{i}.png")

    

plt.figure(figsize=(6,6), dpi=150)
plt.imshow(scores.scores[:200, :200]["score"], cmap="viridis")
plt.colorbar(shrink=0.7)
plt.title("Modified Cosine spectra similarities")
plt.xlabel("Spectrum #ID")
plt.ylabel("Spectrum #ID")


## Modified cosines scores

from matchms.similarity import ModifiedCosine
similarity_measure = ModifiedCosine(tolerance=0.005)
scores_mod = calculate_scores(spectrums, spectrums, similarity_measure,
                          is_symmetric=True)


## library match

import pandas as pd
from matchms.similarity import PrecursorMzMatch
similarity_score = PrecursorMzMatch(tolerance=0.01, tolerance_type="Dalton")
scores = calculate_scores(spectrums, spectrums, similarity_score)
indices = np.where(np.asarray(scores.scores))
idx_row, idx_col = indices
cosine_greedy = CosineGreedy(tolerance=0.01)
data = []
for (x,y) in zip(idx_row,idx_col):
    if x<y:
        msms_score, n_matches = cosine_greedy.pair(spectrums[x], spectrums[y])[()]
        if (msms_score>0.2) & (n_matches>10):
            data.append({'msms_score':msms_score,
                         'matched_peaks':n_matches,
                         'experiment_id':x,
                         'reference_id':y})
df = pd.DataFrame(data) 

# aparte ... how to access a 0d array

boh = cosine_greedy.pair(spectrums[x], spectrums[y])
boh[()][0]


spectrums

spectrums[1].metadata

spectrums[2256].metadata

## Florians answer

from matchms import calculate_scores
from matchms.similarity import PrecursorMzMatch, CosineGreedy

precursor_match = PrecursorMzMatch(tolerance=0.01, tolerance_type="Dalton")
cosine_greedy = CosineGreedy(tolerance=0.01)
scores = calculate_scores(spectrums, spectrums, precursor_match)

scores_combined = []
for score in scores:
    if score[2]:
        cosine_score, cosine_matches = cosine_greedy.pair(score[0], score[1])[()]
        scores_combined.append(list(score) + [cosine_score, cosine_matches])

