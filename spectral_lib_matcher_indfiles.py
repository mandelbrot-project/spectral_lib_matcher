# Required global libs

import os
import sys
import time
import numpy as np
import pandas as pd
import networkx as nx


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

# query_file_path = '/Users/pma/tmp/bafu_ecometabo/FBMN_bafu_ecometabo_pos/spectra/specs_ms.mgf'
# db_file_path = '/Users/pma/tmp/ISDB_DNP_msmatchready.mgf'
# parent_mz_tol = 0.01
# msms_mz_tol = 0.01
# min_cos = 0.2
# min_peaks = 6
# output_file_path = '/Users/pma/tmp/lena_matched.out'

# path_to_mgf = '/Users/pma/tmp/vgf_ind_files/'
# db_file_path = '/Users/pma/tmp/ISDB_DNP_msmatchready.mgf'
# parent_mz_tol = 0.01
# msms_mz_tol = 0.01
# min_cos = 0.2
# min_peaks = 6
# mn_parent_mz_tol = 2000
# mn_msms_mz_tol = 0.01
# mn_min_cos = 0.6
# mn_min_peaks = 6

# defining the command line arguments
try:
    path_to_mgf = sys.argv[1]
    db_file_path = sys.argv[2]
    parent_mz_tol = sys.argv[3]
    msms_mz_tol = sys.argv[4]
    min_cos = sys.argv[5]
    min_peaks = sys.argv[6]
    mn_parent_mz_tol = sys.argv[7]
    mn_msms_mz_tol = sys.argv[8]
    mn_min_cos = sys.argv[9]
    mn_min_peaks = sys.argv[10]
    #output_file_path = sys.argv[11]
    #output_file_path_mn = sys.argv[12]

    print('Parsing spectral file '
          + path_to_mgf
          + ' against spectral database: '
          + db_file_path
          + '.\n'
          +'\n'
          + ' This spectral matching is done with: \n' 
          + '   - a parent mass tolerance of ' + str(parent_mz_tol) + ' Da.' + '\n'
          + '   - a msms mass tolerance of ' + str(msms_mz_tol) + ' Da.' + '\n'
          + '   - a minimal cosine of ' + str(min_cos) + '\n'
          + '   - a minimal matching peaks number of ' + str(min_peaks) + '\n'
          + '\n For each spectra a MN calculation is done with: \n' 
          + '   - a parent mass tolerance of ' + str(mn_parent_mz_tol) + ' Da.' + '\n'
          + '   - a msms mass tolerance of ' + str(mn_msms_mz_tol) + ' Da.' + '\n'
          + '   - a minimal cosine of ' + str(mn_min_cos) + '\n'
          + '   - a minimal matching peaks number of ' + str(mn_min_peaks) + '\n'
          +'\n'
          + 'Results will be outputed in each spectral file respective subfolders in ' + path_to_mgf  + '\n')  
except:
    print(
        '''Please add input and output file path as first and second argument, InChI column header as third argument and finally the number of cpus you want to use.
        Example :
        python spectral_lib_matcher.py /Users/pma/tmp/Lena_metabo_local/FBMN_metabo_lena/spectra/fbmn_lena_metabo_specs_ms.mgf /Users/pma/tmp/New_DNP_full_pos.mgf 0.01 0.01 0.2 6 /Users/pma/tmp/lena_matched.out''')


# python spectral_lib_matcher.py /Users/pma/Dropbox/Research_UNIGE/Projets/Ongoing/MEMO/GNPS_output_GNPS_3/spectra/specs_ms.mgf /Users/pma/tmp/ISDB_DNP_msmatchready.mgf 0.01 0.01 0.2 6 /Users/pma/Dropbox/Research_UNIGE/Projets/Ongoing/MEMO/GNPS_output_GNPS_3/ISDB_results.out
# python spectral_lib_matcher.py /Users/pma/tmp/vgf_ind_files/VGF157_B11/VGF157_B11.mgf /Users/pma/tmp/ISDB_DNP_msmatchready.mgf 0.01 0.01 0.2 6 /Users/pma/tmp/vgf_ind_files/VGF157_B11/VGF157_B11_results.out
# python spectral_lib_matcher.py /Users/pma/tmp/vgf_ind_files/VGF157_B11/VGF157_B11.mgf /Users/pma/tmp/ISDB_DNP_msmatchready.mgf 0.01 0.01 0.2 6 2000 0.01 0.6 6 /Users/pma/tmp/vgf_ind_files/VGF157_B11/VGF157_B11_results.out /Users/pma/tmp/vgf_ind_files/VGF157_B11/VGF157_B11_mn.out
# python spectral_lib_matcher_indfiles.py /Users/pma/tmp/vgf_ind_files/ /Users/pma/tmp/ISDB_DNP_msmatchready.mgf 0.01 0.01 0.2 6 2000 0.01 0.6 6


### loading filtering functions

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

# # It looks like the cleaning stage of the db is mandatory. Something to do with precursor mz.
# I tried to export the cleaned spectral_db as mgf using the save_as_mgf() function However upon reloading the problems appears.
# So it need inline cleaning. Have to check this or raise an issue on matchms git if reproducible.
print('Cleaning the spectral database metadata fields ...')

spectrums_db = list(load_from_mgf(db_file_path))

with nostdout():
    spectrums_db_cleaned = [metadata_processing(s) for s in spectrums_db]
    # spectrums_db_cleaned = [peak_processing(s) for s in spectrums_db_cleaned]

print('A total of %s clean spectra were found in the spectral library.' % len(spectrums_db_cleaned))

#save_as_mgf(spectrums_db_cleaned, '/Users/pma/tmp/ISDB_DNP_msmatchready.mgf')


# timer is started
start_time = time.time()

# Here we work on the batch loading of the mgf files


# We traverse the directory using os.walk

for root, dirs, files in os.walk(path_to_mgf):
    for file in files:
        if file.endswith(".mgf"):

            base = os.path.basename(root)

            print('Treating file ' + base)
            

            spectrums_query = list(load_from_mgf(os.path.join(root, file)))


            print('%s spectra were found in the query file.' % len(spectrums_query))


            # len(spectrums_query)
            # len(spectrums_db)

            # spectrums_query[4198].metadata

            # spectrums_query[345].metadata


            # spectrums_db[0].metadata

            

            with nostdout():
                spectrums_query = [metadata_processing(s) for s in spectrums_query]
                spectrums_query = [peak_processing(s) for s in spectrums_query]

            


            print('Proceeding to the MN calc for ' + base)
            #%%time
            from matchms.similarity import PrecursorMzMatch
            from matchms import calculate_scores
            from matchms.similarity import CosineGreedy

            similarity_score = PrecursorMzMatch(tolerance=float(mn_parent_mz_tol), tolerance_type="Dalton")
            scores = calculate_scores(spectrums_query, spectrums_query, similarity_score)
            indices = np.where(np.asarray(scores.scores))
            idx_row, idx_col = indices
            cosine_greedy = CosineGreedy(tolerance=float(mn_msms_mz_tol))
            data = []
            for (x,y) in zip(idx_row,idx_col):
                if x<y:
                    msms_score, n_matches = cosine_greedy.pair(spectrums_query[x], spectrums_query[y])[()]
                    if (msms_score>float(mn_min_cos)) & (n_matches>int(mn_min_peaks)):
                        data.append({'msms_score':msms_score,
                                    'matched_peaks':n_matches,
                                    'feature_id':x + 1,
                                    'reference_id':y + 1})
            df = pd.DataFrame(data)
            

            # calculating component index in the g

            G = nx.from_pandas_edgelist(df, 'feature_id', 'reference_id')

            # nx.connected_components(G)
            # [len(c) for c in sorted(nx.connected_components(G), key=len, reverse=True)]
            # [list(c) for c in sorted(nx.connected_components(G), key=len, reverse=True)]
            # largest_cc = max(nx.connected_components(G), key=len)

            def connected_component_subgraphs(G):
                for c in nx.connected_components(G):
                    yield G.subgraph(c)

            components = connected_component_subgraphs(G)

            comp_dict = {idx: comp.nodes() for idx, comp in enumerate(components)}
            # print(comp_dict)


            attr = {n: {'component_id' : comp_id} for comp_id, nodes in comp_dict.items() for n in nodes}

            comp = pd.DataFrame.from_dict(attr, orient = 'index')

            comp.reset_index(inplace = True)
            comp.rename(columns={'index': 'feature_id'}, inplace=True)

            comp.to_csv(root + '/' + base + '_mn_nodes.txt', sep = '\t', index = False)

            df.to_csv(root + '/' + base + '_mn_edges.txt', sep = '\t', index = False)

            print('Proceeding to the spectral match for ' + base)
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
                                    'feature_id':x + 1,
                                    'reference_id':y + 1,
                                    'inchikey': spectrums_db_cleaned[y].get("inchikey")})
            df = pd.DataFrame(data)


            df.to_csv(root + '/' + base + '_results.txt', sep = '\t')

print('Finished in %s seconds.' % (time.time() - start_time))
#print('You can check your results in here %s' % output_file_path)


# %%

