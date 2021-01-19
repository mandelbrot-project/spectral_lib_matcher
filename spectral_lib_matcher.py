# Required global libs

import os
import sys
import time
import numpy as np
import pandas as pd

# loading the files

from matchms.importing import load_from_mgf
from matchms.exporting import save_as_mgf

# define a warning silencer
# I added this because of annoying stdout prints after the spectra cleaning function.
# To be removed for additional infos. //TODO Add a switch.
# see https://stackoverflow.com/a/2829036 for the nostdout 

import contextlib
import io

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = io.StringIO()
    yield
    sys.stdout = save_stdout

# query_file_path = '/Users/pma/tmp/Lena_metabo_local/FBMN_metabo_lena/spectra/fbmn_lena_metabo_specs_ms.mgf'
# db_file_path = '/Users/pma/tmp/ISDB_DNP_msmatchready.mgf'
# parent_mz_tol = 0.01
# msms_mz_tol = 0.01
# min_cos = 0.2
# min_peaks = 6
# output_file_path = '/Users/pma/tmp/lena_matched.out'


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
          + '   - a parent mass tolerance of ' + str(parent_mz_tol) + '\n'
          + '   - a msms mass tolerance of ' + str(msms_mz_tol) + '\n'
          + '   - a minimal cosine of ' + str(min_cos) + '\n'
          + '   - a minimal matching peaks number of ' + str(min_peaks) + '\n'
          + 'Results will be outputed in ' + output_file_path)
except:
    print(
        '''Please add input and output file path as first and second argument, InChI column header as third argument and finally the number of cpus you want to use.
        Example :
        python spectral_lib_matcher.py /Users/pma/tmp/Lena_metabo_local/FBMN_metabo_lena/spectra/fbmn_lena_metabo_specs_ms.mgf /Users/pma/tmp/New_DNP_full_pos.mgf 0.01 0.01 0.2 6 /Users/pma/tmp/lena_matched.out''')


# timer is started
start_time = time.time()


path_data_query = "/Users/pma/tmp/Lena_metabo_local/FBMN_metabo_lena/spectra/"  # enter path to downloaded mgf file
path_data_db = "/Users/pma/tmp/"  # enter path to downloaded mgf file

file_mgf_query = os.path.join(path_data_query, 
                        "fbmn_lena_metabo_specs_ms.mgf")

spectrums_query = list(load_from_mgf(query_file_path))

file_mgf_db = os.path.join(path_data_db, 
                        "New_DNP_full_pos.mgf")
spectrums_db = list(load_from_mgf(db_file_path))

print('%s spectra were found in the query file.' % len(spectrums_query))

print('They will be matched against the %s spectra of the spectral library.' % len(spectrums_db))

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

with nostdout():
    spectrums_query = [metadata_processing(s) for s in spectrums_query]
    spectrums_query = [peak_processing(s) for s in spectrums_query]

# # It looks like the cleaning stage of the db is mandatory. Something to do with precursor mz.
# I tried to export the cleaned spectral_db as mgf using the save_as_mgf() function However upon reloading the problems appears.
# So it need inline cleaning. Have to check this or raise an issue on matchms git if reproducible.
print('Cleaning the spectral database metadata fields ...')

with nostdout():
    spectrums_db_cleaned = [metadata_processing(s) for s in spectrums_db]
    # spectrums_db_cleaned = [peak_processing(s) for s in spectrums_db_cleaned]

#save_as_mgf(spectrums_db_cleaned, '/Users/pma/tmp/ISDB_DNP_msmatchready.mgf')


print('Proceeding to the spectral match ...')
#%%time
from matchms.similarity import PrecursorMzMatch
from matchms import calculate_scores
from matchms.similarity import CosineGreedy

similarity_score = PrecursorMzMatch(tolerance=float(parent_mz_tol), tolerance_type="Dalton")
scores = calculate_scores(spectrums_query, spectrums_db_cleaned, similarity_score)
indices = np.where(np.asarray(scores.scores))
idx_row, idx_col = indices
cosine_greedy = CosineGreedy(tolerance=float(msms_mz_tol))
data = []
for (x,y) in zip(idx_row,idx_col):
    if x<y:
        msms_score, n_matches = cosine_greedy.pair(spectrums_query[x], spectrums_db_cleaned[y])[()]
        if (msms_score>float(min_cos)) & (n_matches>int(min_peaks)):
            data.append({'msms_score':msms_score,
                         'matched_peaks':n_matches,
                         'experiment_id':x,
                         'reference_id':y,
                         'inchikey': spectrums_db_cleaned[y].get("inchikey")})
df = pd.DataFrame(data)


df.to_csv(output_file_path, sep = '\t')

print('Finished in %s seconds.' % (time.time() - start_time))
print('You can check your results in here %s' % output_file_path)


# %%
