# Required global libs

import os
import sys
import numpy as np
import pandas as pd

# loading the files

from matchms.importing import load_from_mgf



# defining the command line arguments
try:
    query_file_path = sys.argv[1]
    db_file_path = sys.argv[2]
    parent_mz_tol = sys.argv[3]
    msms_mz_tol = sys.argv[4]
    min_cos = sys.argv[5]
    min_peaks = sys.argv[6]
    output_file_path = sys.argv[7]

    print('Parsing spectral file '
          + query_file_path
          + ' against spectral database: '
          + db_file_path
          + '.\n This spectral matching is done with: \n' 
          + '   - a parent mass tolerance of ' + parent_mz_tol + '\n '
          + '   - a msms mass tolerance of ' + msms_mz_tol + '\n '
          + '   - a minimal cosine of ' + min_cos + '\n '
          + '   - a minimal matching peaks number of ' + min_peaks + '\n '
          + 'Results will be outputed in ' + ouput_file_path)
except:
    print(
        '''Please add input and output file path as first and second argument, InChI column header as third argument and finally the number of cpus you want to use.
        Example :
        python spectral_lib_matcher.py /Users/pma/tmp/Lena_metabo_local/FBMN_metabo_lena/spectra/fbmn_lena_metabo_specs_ms.mgf /Users/pma/tmp/New_DNP_full_pos.mgf 0.01 0.01 0.2 6 /Users/pma/tmp/lena_matched.out''')



path_data_query = "/Users/pma/tmp/Lena_metabo_local/FBMN_metabo_lena/spectra/"  # enter path to downloaded mgf file
path_data_db = "/Users/pma/tmp/"  # enter path to downloaded mgf file

file_mgf_query = os.path.join(path_data_query, 
                        "fbmn_lena_metabo_specs_ms.mgf")

spectrums_query = list(load_from_mgf(query_file_path))

file_mgf_db = os.path.join(path_data_db, 
                        "New_DNP_full_pos.mgf")
spectrums_db = list(load_from_mgf(db_file_path))


# len(spectrums_query)
# len(spectrums_db)

# spectrums_query[0].metadata

# spectrums_db[0].metadata

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




#%%time
from matchms.similarity import PrecursorMzMatch
from matchms import calculate_scores
from matchms.similarity import CosineGreedy

similarity_score = PrecursorMzMatch(tolerance=parent_mz_tol, tolerance_type="Dalton")
scores = calculate_scores(spectrums_query, spectrums_db_cleaned, similarity_score)
indices = np.where(np.asarray(scores.scores))
idx_row, idx_col = indices
cosine_greedy = CosineGreedy(tolerance=msms_mz_tol)
data = []
for (x,y) in zip(idx_row,idx_col):
    if x<y:
        msms_score, n_matches = cosine_greedy.pair(spectrums_query[x], spectrums_db_cleaned[y])[()]
        if (msms_score>min_cos) & (n_matches>min_peaks):
            data.append({'msms_score':msms_score,
                         'matched_peaks':n_matches,
                         'experiment_id':x,
                         'reference_id':y,
                         'inchikey': spectrums_db_cleaned[y].get("inchikey")})
df = pd.DataFrame(data)


df.to_csv(output_file_path, sep = '\t')

