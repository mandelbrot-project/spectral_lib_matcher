import pandas as pd
import os
import glob
from matchms.importing import load_from_mgf
from matchms.exporting import save_as_mgf


sample_dir = "C:/Users/gaudrya.FARMA/Desktop/VGF_individual_files_pos/"

samples_dir = [x[0] for x in os.walk(sample_dir)]
samples_dir.remove(sample_dir)
spectrums = []
i = 0

for sample_directory in samples_dir:
    os.chdir(sample_directory)
    sample = sample_directory.split(sample_dir,1)[1]
    mgf_file = glob.glob('*.mgf')[0]
    sample_spec = list(load_from_mgf(mgf_file))
    for spectrum in sample_spec:
        spectrum.set('feature_id', i)
        new_scan = sample + '_feature_' + spectrum.metadata['scans'] 
        spectrum.set('scans', new_scan)
        i += 1
    spectrums = spectrums + sample_spec

os.chdir(sample_dir)

save_as_mgf(spectrums, "aggregated_mgf.mgf")
