# Required global libs

import os
import numpy as np
import pandas as pd

# loading the files

from matchms.importing import load_from_mgf


path_data_query = "/Users/pma/tmp/Lena_metabo_local/FBMN_metabo_lena/spectra/"  # enter path to downloaded mgf file
path_data_db = "/Users/pma/tmp/"  # enter path to downloaded mgf file

file_mgf_query = os.path.join(path_data_query, 
                        "fbmn_lena_metabo_specs_ms.mgf")

spectrums_query = list(load_from_mgf(file_mgf_query))

file_mgf_db = os.path.join(path_data_db, 
                        "New_DNP_full_pos.mgf")
spectrums_db = list(load_from_mgf(file_mgf_db))


len(spectrums_query)
len(spectrums_db)

spectrums_query[0].metadata

spectrums_db[0].metadata

### some filtering

from matchms.filtering import default_filters
# from matchms.filtering import repair_inchi_inchikey_smiles
# from matchms.filtering import derive_inchikey_from_inchi
# from matchms.filtering import derive_smiles_from_inchi
# from matchms.filtering import derive_inchi_from_smiles
# from matchms.filtering import harmonize_undefined_inchi
# from matchms.filtering import harmonize_undefined_inchikey
# from matchms.filtering import harmonize_undefined_smiles
def metadata_processing(spectrum):
    spectrum = default_filters(spectrum)
    # spectrum = repair_inchi_inchikey_smiles(spectrum)
    # spectrum = derive_inchi_from_smiles(spectrum)
    # spectrum = derive_smiles_from_inchi(spectrum)
    # spectrum = derive_inchikey_from_inchi(spectrum)
    # spectrum = harmonize_undefined_smiles(spectrum)
    # spectrum = harmonize_undefined_inchi(spectrum)
    # spectrum = harmonize_undefined_inchikey(spectrum)
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

spectrums_query = [metadata_processing(s) for s in spectrums_query]
spectrums_query = [peak_processing(s) for s in spectrums_query]

spectrums_db_cleaned = [metadata_processing(s) for s in spectrums_db]
spectrums_db_cleaned = [peak_processing(s) for s in spectrums_db_cleaned]




%%time
from matchms.similarity import PrecursorMzMatch
similarity_score = PrecursorMzMatch(tolerance=0.01, tolerance_type="Dalton")
scores = calculate_scores(spectrums_query, spectrums_db_cleaned, similarity_score)
indices = np.where(np.asarray(scores.scores))
idx_row, idx_col = indices
cosine_greedy = CosineGreedy(tolerance=0.01)
data = []
for (x,y) in zip(idx_row,idx_col):
    if x<y:
        msms_score, n_matches = cosine_greedy.pair(spectrums_query[x], spectrums_db_cleaned[y])[()]
        if (msms_score>0.2) & (n_matches>1):
            data.append({'msms_score':msms_score,
                         'matched_peaks':n_matches,
                         'experiment_id':x,
                         'reference_id':y,
                         'inchikey': spectrums_db_cleaned[y].get("inchikey")})
df = pd.DataFrame(data)


df.to_csv()

