import unittest
from unittest.mock import patch

from transform import check_required,check_range,generate_file_hash
import ingest

class TestValidation(unittest.TestCase):

    def test_check_required_valid_field(self):
        row = {"dealer_id":1,"dealer_code":"DLR-00001","region":"SOUTH","credit_terms_days":10}
        errors = check_required(row)
        self.assertFalse(errors)

    def test_check_required_missing_dealer_id(self):
        row = {"dealer_id":None,"dealer_code":"DLR-00001","region":"SOUTH","credit_terms_days":0}
        errors = check_required(row)
        self.assertTrue(errors)

    def test_check_required_missing_dealer_code(self):
        row = {"dealer_id":1,"dealer_code":None,"region":"SOUTH","credit_terms_days":0}
        errors = check_required(row)
        self.assertTrue(errors)

    def test_check_required_missing_region(self):
        row = {"dealer_id":1,"dealer_code":"DLR-00001","region":None,"credit_terms_days":0}
        errors = check_required(row)
        self.assertTrue(errors)

    def test_check_required_missing_credit_terms_days(self):
        row = {"dealer_id":1,"dealer_code":"DLR-00001","region":"SOUTH","credit_terms_days":None}
        errors = check_required(row)
        self.assertTrue(errors)

    def test_check_range_valid_credit_term(self):
        row = {"dealer_id":1,"dealer_code":"DLR-00001","region":"SOUTH","credit_terms_days":10}
        errors = check_range(row)
        self.assertFalse(errors)

    def test_check_range_negative_credit_term(self):
        row = {"dealer_id":1,"dealer_code":"DLR-00001","region":"SOUTH","credit_terms_days":-10}
        errors = check_range(row)
        self.assertTrue(errors)

    def test_generate_file_hash(self):
        file_path = "/home/name04/Desktop/Anjaneya/02_Bootcamp/04_Python/Bootcamp_Python/01_Data/clean/dealer.csv"
        file_hash = "8841818014e4df36c13597e29fea2ad787dcf9df3b37f7cc8157b2532162fbbb"
        consistent = True
        for i in range(3):
            hash = generate_file_hash(file_path)
            consistent = (consistent and (hash == file_hash))
        self.assertTrue(consistent)

    @patch("ingest.download_from_s3")
    def test_download_from_s3(self,mock_download_from_s3):
        mock_download_from_s3.return_value = "dealer.csv"
        result = ingest.download_from_s3("raw-bucket")
        assert result == "dealer.csv"
        mock_download_from_s3.assert_called_once()

if __name__ == "__main__":
    unittest.main()