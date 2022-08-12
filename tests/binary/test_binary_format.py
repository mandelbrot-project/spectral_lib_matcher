import pytest
import shutil
from mandelbrot_spectral_lib_matcher.binary import write_binary_database, read_binary_database
from mandelbrot_spectral_lib_matcher.processor import process, process_query, minimal_process_query
from matchms.importing import load_from_mgf


class TestBinaryDatabase:
    database = minimal_process_query(process_query(load_from_mgf("tests/data/database.mgf")))
    query = process_query(load_from_mgf("tests/data/fake_sample.mgf"))

    @pytest.fixture(scope='module')
    def write_database(self, tmpdir, delete=True):
        filename = tmpdir.join("test_db_1.mdbl")
        with open(filename, "wb") as file:
            write_binary_database(self.database, file)
        if delete:
            tmpdir.remove()
        else:
            return filename

    @pytest.fixture(scope='module')
    def read_database(self, tmpdir):
        filename = self.write_database(tmpdir, delete=False)
        with open(filename, "rb") as file:
            bin_database = read_binary_database(file)
        df = process(self.query, bin_database, 0.01, 0.01, 0.2, 6)
        tmpdir.remove()
        assert df.iloc[0, :].matched_peaks == 85

    def test_cosine(self):
        df = process(self.query, self.database, 0.01, 0.01, 0.2, 6)
        assert abs(df.iloc[0, :].msms_score - 0.738847) <= 0.000001
