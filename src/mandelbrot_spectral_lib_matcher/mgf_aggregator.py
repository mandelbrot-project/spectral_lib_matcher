import glob
import os
import pandas as pd
import sys
from matchms.exporting import save_as_mgf
from matchms.importing import load_from_mgf
from time import sleep


sample_dir = "C:/Users/gaudrya.FARMA/Desktop/VGF_individual_files_pos/"

samples_dir = [x[0] for x in os.walk(sample_dir)]
samples_dir.remove(sample_dir)
spectrums = []
i = 1
j = 1

n_bar = 50
n_iter = len(samples_dir)
for sample_directory in samples_dir:
    k = j / n_iter
    sys.stdout.write('\r')
    sys.stdout.write(f"[{'=' * int(n_bar * k):{n_bar}s}] {int(100 * k)}%")
    sys.stdout.flush()
    j += 1
    sleep(0.05)

    os.chdir(sample_directory)
    sample = sample_directory.split(sample_dir, 1)[1]
    mgf_file = glob.glob('*.mgf')[0]
    sample_spec = list(load_from_mgf(mgf_file))
    for spectrum in sample_spec:
        original_feat_id = sample + '_feature_' + spectrum.metadata['scans']
        spectrum.set('original_feature_id', original_feat_id)
        spectrum.set('feature_id', i)
        spectrum.set('scans', i)
        i += 1
    spectrums = spectrums + sample_spec

os.chdir(sample_dir)
metadata_df = pd.DataFrame(s.metadata for s in spectrums)

metadata_df.to_csv('vgf_pos_aggregated_metadata.csv', index=False)
save_as_mgf(spectrums, "vgf_pos_aggregated_spectra.mgf")
