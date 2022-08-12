#!/usr/bin/env python3

from matchms.importing import load_from_mgf
from mandelbrot_spectral_lib_matcher.processor import process, process_query, minimal_process_query


class TestMatching:
    database = minimal_process_query(process_query(load_from_mgf("tests/data/database.mgf")))
    query = process_query(load_from_mgf("tests/data/fake_sample.mgf"))

    def test_processing(self):
        df = process(self.query, self.database, 0.01, 0.01, 0.2, 6)
        assert df.shape[0] > 0

    def test_matching_peaks(self):
        df = process(self.query, self.database, 0.01, 0.01, 0.2, 6)
        assert df.iloc[0, :].matched_peaks == 85

    def test_cosine(self):
        df = process(self.query, self.database, 0.01, 0.01, 0.2, 6)
        assert abs(df.iloc[0, :].msms_score - 0.738847) <= 0.000001