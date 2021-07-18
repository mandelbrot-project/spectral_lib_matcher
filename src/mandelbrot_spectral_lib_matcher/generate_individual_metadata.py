import pandas as pd
import os
import glob

# Import metadata
df_meta = pd.read_csv("../../Desktop/PF_resolved_species_plantparts_corrected_ms_filename_with_inj_date.tsv", sep='\t')
df_meta['sample_id'] = df_meta['MS_filename'].str.replace('.mzXML', '')
df_meta['sample_type'] = 'sample'


df_meta = df_meta[['sample_id', 'sample_type', 'SUBSTANCE_NAME', 'kingdom_cof', 'phylum_cof', 'class_cof',
'order_cof', 'family_cof', 'genus_cof', 'species_cof', 'corrected', 'broad_organ', 'tissue', 'subsystem',
'PLATESET', 'MS_filename', 'injection_date']]

df_meta.rename(columns={
    "SUBSTANCE_NAME": "sample_substance_name",
    "kingdom_cof": "organism_kingdom",
    "phylum_cof": "organism_phylum",
    "class_cof": "organism_class",
    "order_cof": "organism_order",
    "family_cof": "organism_family",
    "genus_cof": "organism_genus",
    "species_cof": "organism_species",
    "corrected": "organism_organe",
    "broad_organ": "organism_broad_organe",
    "tissue": "organism_tissue",
    "subsystem": "organism_subsystem",
    "PLATESET": "sample_plate_id",
    "MS_filename": "ms_filename",
    "injection_date": "ms_injection_date",
    }, inplace=True )

df_bio = pd.read_csv("../../Desktop/PF-collection MTS final 22.05.2019_pour_Bioscore.csv", sep=';', 
usecols=['leish_donovani_10ugml', 'leish_donovani_2ugml', 'tryp_brucei_rhodesiense_10ugml',
       'tryp_brucei_rhodesiense_2ugml', 'tryp_cruzi_10ugml', 'l6_cytotoxicity_10ugml', 'MS_filename'])

df_bio.rename(columns={
    "leish_donovani_10ugml": "bio_leish_donovani_10ugml_inhibition",
    "leish_donovani_2ugml": "bio_leish_donovani_2ugml_inhibition",
    "tryp_brucei_rhodesiense_10ugml": "bio_tryp_brucei_rhodesiense_10ugml_inhibition",
    "tryp_brucei_rhodesiense_2ugml": "bio_tryp_brucei_rhodesiense_2ugml_inhibition",
    "tryp_cruzi_10ugml": "bio_tryp_cruzi_10ugml_inhibition",
    "l6_cytotoxicity_10ugml": "bio_l6_cytotoxicity_10ugml_inhibition",
    }, inplace=True )

df_meta_bio = df_meta.merge(df_bio, left_on='ms_filename', right_on='MS_filename')
df_meta_bio = df_meta_bio.drop('MS_filename', axis=1)

# Add metadata for QC and blanks
plates = list(set(df_meta['sample_plate_id'].to_list()))
qc_positions = ['_A01', '_B01', '_C01', '_D01', '_E01', '_F01','_G01', '_H01']
blank_positions = ['_A12', '_B12', '_C12', '_D12', '_E12', '_F12','_G12', '_H12']

# Dict plate:date
df_for_plate_date = df_meta_bio[['sample_plate_id', 'ms_injection_date']].drop_duplicates()
plate_date_dict = pd.Series(df_for_plate_date.ms_injection_date.values,index=df_for_plate_date.sample_plate_id).to_dict()

qc_list = []
blank_list = []

for plate in plates:
    for qc_position in qc_positions:
        dic_qc = {}
        dic_qc['sample_id'] = plate+qc_position
        dic_qc['sample_plate_id'] = plate
        dic_qc['ms_filename'] = plate+qc_position+'.mzXML'
        dic_qc['sample_type'] = 'qc'
        dic_qc['sample_substance_name'] = 'qc_mix'    
        qc_list.append(dic_qc)

    for blank_position in blank_positions:
        dic_blank = {}
        dic_blank['sample_id'] = plate+blank_position
        dic_blank['sample_plate_id'] = plate
        dic_blank['ms_filename'] =plate+blank_position+'.mzXML'
        dic_blank['sample_type'] = 'blank'
        dic_blank['sample_substance_name'] = 'blank'    
        qc_list.append(dic_blank)

qc_df = pd.DataFrame(qc_list)
blank_df = pd.DataFrame(blank_list)

df_meta_bio = df_meta_bio.append(qc_df)
df_meta_bio = df_meta_bio.append(blank_df)

df_meta_bio.ms_injection_date = df_meta_bio.ms_injection_date.fillna(df_meta_bio.sample_plate_id.map(plate_date_dict))
df_meta_bio.to_csv("//farma-ad2/FARMA-Network/Recherche/COMMON FASIE-FATHO/PF_project/201109_VGF_pos_new_treatment/VGF_individual_files_pos/VGF_clean_metadata_with_bio_with_qc_and_blanks.tsv", sep='\t', index=False)


sample_dir = "//farma-ad2/FARMA-Network/Recherche/COMMON FASIE-FATHO/PF_project/201109_VGF_pos_new_treatment/VGF_individual_files_pos/"
samples_dir = [x[0] for x in os.walk(sample_dir)]
samples_dir.remove(sample_dir)

for sample_dir in samples_dir:
    os.chdir(sample_dir)
    sample = sample_dir.split(sample_dir,1)[1]
    df_meta_bio_sub = df_meta_bio[df_meta_bio['sample_id']==sample]
    metadata = sample + '_metadata.tsv'
    df_meta_bio_sub.to_csv(metadata, sep='\t', index=False)

