import unittest
from unittest.mock import patch
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import dirty_dealer_path
import ingest
from transform import validate_row

class TestValidation(unittest.TestCase):

    def test_generate_file_hash(self):
        dirty_dealer_hash = "06a774cc887a598952eb0b915ea26409c049c6724c992d3d32a1617fe21e90b9"
        self.assertTrue(ingest.generate_file_hash(dirty_dealer_path) == dirty_dealer_hash)

    def test_validate_row_dealer_valid(self):
        file_name = "dealer.csv"
        row = {'dealer_id':'1','dealer_code':'DLR-00001','dealer_name':'Coimbatore Auto Parts - 1','city':'Coimbatore','state':'TN','region':'SOUTH','dealer_type':'RETAIL','created_date':'2024-08-11','is_active':'true','email':'dealer1@example.com','phone':'+91-9855165986','credit_terms_days':'30'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets=None)
        self.assertTrue(error is None)

    def test_validate_row_dealer_missing_reqd(self):
        file_name = "dealer.csv"
        row = {'dealer_id':'','dealer_code':'DLR-00001','dealer_name':'Coimbatore Auto Parts - 1','city':'Coimbatore','state':'TN','region':'SOUTH','dealer_type':'RETAIL','created_date':'2024-08-11','is_active':'true','email':'dealer1@example.com','phone':'+91-9855165986','credit_terms_days':'30'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets=None)
        self.assertTrue(error == "E001_MISSING_REQUIRED")

    def test_validate_row_dealer_bad_int(self):
        file_name = "dealer.csv"
        row = {'dealer_id':'1','dealer_code':'DLR-00001','dealer_name':'Coimbatore Auto Parts - 1','city':'Coimbatore','state':'TN','region':'SOUTH','dealer_type':'RETAIL','created_date':'2024-08-11','is_active':'true','email':'dealer1@example.com','phone':'+91-9855165986','credit_terms_days':'30,'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets=None)
        self.assertTrue(error == "E002_BAD_TYPE")

    def test_validate_row_dealer_bad_date(self):
        file_name = "dealer.csv"
        row = {'dealer_id':'1','dealer_code':'DLR-00001','dealer_name':'Coimbatore Auto Parts - 1','city':'Coimbatore','state':'TN','region':'SOUTH','dealer_type':'RETAIL','created_date':'2024-80-11','is_active':'true','email':'dealer1@example.com','phone':'+91-9855165986','credit_terms_days':'30'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets=None)
        self.assertTrue(error == "E002_BAD_TYPE")

    def test_validate_row_product_valid(self):
        file_name = "product.csv"
        row = {'product_id':'1 ','sku':'SKU-TF-00001','product_name':'Transmission Filter M - BrandB Series-1','category':'TRANSMISSION_FILTER','subcategory':'TRANSMISSION_M','brand':'BrandB','uom':'EA','unit_cost':'27.45','unit_price':'49.41','weight_kg':'1.36','is_discontinued':'false','created_date':'2025-11-28'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets=None)
        self.assertTrue(error is None)

    def test_validate_row_product_valid_missing_reqd(self):
        file_name = "product.csv"
        row = {'product_id':'1 ','sku':None,'product_name':'Transmission Filter M - BrandB Series-1','category':'TRANSMISSION_FILTER','subcategory':'TRANSMISSION_M','brand':'BrandB','uom':'EA','unit_cost':'27.45','unit_price':'49.41','weight_kg':'1.36','is_discontinued':'false','created_date':'2025-11-28'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets=None)
        self.assertTrue(error == "E001_MISSING_REQUIRED")

    def test_validate_row_product_valid_bad_int(self):
        file_name = "product.csv"
        row = {'product_id':'1.','sku':'SKU-TF-00001','product_name':'Transmission Filter M - BrandB Series-1','category':'TRANSMISSION_FILTER','subcategory':'TRANSMISSION_M','brand':'BrandB','uom':'EA','unit_cost':'27.45','unit_price':'49.41','weight_kg':'1.36','is_discontinued':'false','created_date':'2025-11-28'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets=None)
        self.assertTrue(error == "E002_BAD_TYPE")

    def test_validate_row_product_bad_float(self):
        file_name = "product.csv"
        row = {'product_id':'1 ','sku':'SKU-TF-00001','product_name':'Transmission Filter M - BrandB Series-1','category':'TRANSMISSION_FILTER','subcategory':'TRANSMISSION_M','brand':'BrandB','uom':'EA','unit_cost':'27.45','unit_price':'49.41','weight_kg':'1,36','is_discontinued':'false','created_date':'2025-11-28'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets=None)
        self.assertTrue(error == "E002_BAD_TYPE")

    def test_validate_row_product_valid_bad_date(self):
        file_name = "product.csv"
        row = {'product_id':'1 ','sku':'SKU-TF-00001','product_name':'Transmission Filter M - BrandB Series-1','category':'TRANSMISSION_FILTER','subcategory':'TRANSMISSION_M','brand':'BrandB','uom':'EA','unit_cost':'27.45','unit_price':'49.41','weight_kg':'1.36','is_discontinued':'false','created_date':'2025/11/08'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets=None)
        self.assertTrue(error == "E002_BAD_TYPE")

    def test_validate_row_product_valid_invalid_range(self):
        file_name = "product.csv"
        row = {'product_id':'1 ','sku':'SKU-TF-00001','product_name':'Transmission Filter M - BrandB Series-1','category':'TRANSMISSION_FILTER','subcategory':'TRANSMISSION_M','brand':'BrandB','uom':'EA','unit_cost':'0.0','unit_price':'49.41','weight_kg':'1.36','is_discontinued':'false','created_date':'2025-11-28'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets=None)
        self.assertTrue(error == "E003_OUT_OF_RANGE")

    def test_validate_row_inventory_valid(self):
        file_name = "inventory.csv"
        row = {'inventory_id':'INV-20251130-00001','snapshot_date':'2025-11-30','dealer_id':'40','product_id':'134','on_hand_qty':'17','on_order_qty':'0','reorder_point':'16','reorder_qty':'60','last_restock_date':'2025-11-22','last_sale_date':'2025-11-03'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets=None)
        self.assertTrue(error is None)

    def test_validate_row_inventory_missing_reqd(self):
        file_name = "inventory.csv"
        row = {'inventory_id':'INV-20251130-00001','snapshot_date':'2025-11-30','dealer_id':'40','product_id':'134','on_hand_qty':None,'on_order_qty':'0','reorder_point':'16','reorder_qty':'60','last_restock_date':'2025-11-22','last_sale_date':'2025-11-03'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets={"product_id":set([134]),"dealer_id":set([40])})
        self.assertTrue(error == "E001_MISSING_REQUIRED")

    def test_validate_row_inventory_bad_int(self):
        file_name = "inventory.csv"
        row = {'inventory_id':'INV-20251130-00001','snapshot_date':'2025-11-30','dealer_id':'4,0','product_id':'134','on_hand_qty':'17','on_order_qty':'0','reorder_point':'16','reorder_qty':'60','last_restock_date':'2025-11-22','last_sale_date':'2025-11-03'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets={"product_id":set([134]),"dealer_id":set([40])})
        self.assertTrue(error == "E002_BAD_TYPE")

    def test_validate_row_inventory_bad_date(self):
        file_name = "inventory.csv"
        row = {'inventory_id':'INV-20251130-00001','snapshot_date':'2025-11-30','dealer_id':'40','product_id':'134','on_hand_qty':'17','on_order_qty':'0','reorder_point':'16','reorder_qty':'60','last_restock_date':'2025-11a-22','last_sale_date':'2025-11-03'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets={"product_id":set([134]),"dealer_id":set([40])})
        self.assertTrue(error == "E002_BAD_TYPE")

    def test_validate_row_inventory_invalid_range(self):
        file_name = "inventory.csv"
        row = {'inventory_id':'INV-20251130-00001','snapshot_date':'2025-11-30','dealer_id':'40','product_id':'134','on_hand_qty':'-1','on_order_qty':'0','reorder_point':'16','reorder_qty':'60','last_restock_date':'2025-11-22','last_sale_date':'2025-11-03'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets={"product_id":set([134]),"dealer_id":set([40])})
        self.assertTrue(error)

    def test_validate_row_inventory_invalid_product_fk(self):
        file_name = "inventory.csv"
        row = {'inventory_id':'INV-20251130-00001','snapshot_date':'2025-11-30','dealer_id':'40','product_id':'124','on_hand_qty':'17','on_order_qty':'0','reorder_point':'16','reorder_qty':'60','last_restock_date':'2025-11-22','last_sale_date':'2025-11-03'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets={"product_id":set([134]),"dealer_id":set([40])})
        self.assertTrue(error == "E004_FK_VIOLATION")

    def test_validate_row_inventory_invalid_dealer_fk(self):
        file_name = "inventory.csv"
        row = {'inventory_id':'INV-20251130-00001','snapshot_date':'2025-11-30','dealer_id':'41','product_id':'124','on_hand_qty':'17','on_order_qty':'0','reorder_point':'16','reorder_qty':'60','last_restock_date':'2025-11-22','last_sale_date':'2025-11-03'}
        row_no = 1
        val_row, error = validate_row(file_name,row,row_no,id_sets={"product_id":set([134]),"dealer_id":set([40])})
        self.assertTrue(error == "E004_FK_VIOLATION")


if __name__ == "__main__":
    unittest.main()