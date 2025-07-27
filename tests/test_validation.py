"""
驗證服務單元測試

測試 ValidationService 的各種驗證功能。
"""

import unittest
from datetime import date, timedelta
from taiwan_railway_gui.services.validation import ValidationService


class TestValidationService(unittest.TestCase):
    """測試驗證服務"""

    def setUp(self):
        """設定測試環境"""
        self.validator = ValidationService()
        self.today = date.today()

    def test_validate_date_range_valid(self):
        """測試有效日期範圍"""
        start_date = self.today - timedelta(days=30)
        end_date = self.today - timedelta(days=1)

        is_valid, error_msg = self.validator.validate_date_range(start_date, end_date)
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")

    def test_validate_date_range_invalid_order(self):
        """測試無效日期順序"""
        start_date = self.today - timedelta(days=1)
        end_date = self.today - timedelta(days=30)

        is_valid, error_msg = self.validator.validate_date_range(start_date, end_date)
        self.assertFalse(is_valid)
        self.assertIn("開始日期不能晚於結束日期", error_msg)

    def test_validate_date_range_future_date(self):
        """測試未來日期"""
        start_date = self.today + timedelta(days=1)
        end_date = self.today + timedelta(days=30)

        is_valid, error_msg = self.validator.validate_date_range(start_date, end_date)
        self.assertFalse(is_valid)
        self.assertIn("未來日期", error_msg)

    def test_validate_date_range_too_old(self):
        """測試過於久遠的日期"""
        start_date = date(1990, 1, 1)
        end_date = date(1990, 1, 31)

        is_valid, error_msg = self.validator.validate_date_range(start_date, end_date)
        self.assertFalse(is_valid)
        self.assertIn("不能早於", error_msg)

    def test_validate_date_range_too_long(self):
        """測試過長的日期範圍"""
        start_date = self.today - timedelta(days=800)
        end_date = self.today - timedelta(days=1)

        is_valid, error_msg = self.validator.validate_date_range(start_date, end_date)
        self.assertFalse(is_valid)
        self.assertIn("不能超過", error_msg)

    def test_validate_station_code_valid(self):
        """測試有效車站代碼"""
        valid_codes = ['1000', '1001', '2345', '999']

        for code in valid_codes:
            is_valid, error_msg = self.validator.validate_station_code(code)
            self.assertTrue(is_valid, f"車站代碼 {code} 應該有效")
            self.assertEqual(error_msg, "")

    def test_validate_station_code_invalid(self):
        """測試無效車站代碼"""
        invalid_codes = ['', 'ABC', '12A', 'abc123', None]

        for code in invalid_codes:
            if code is not None:
                is_valid, error_msg = self.validator.validate_station_code(code)
                self.assertFalse(is_valid, f"車站代碼 {code} 應該無效")
                self.assertNotEqual(error_msg, "")

    def test_validate_station_code_empty(self):
        """測試空車站代碼"""
        is_valid, error_msg = self.validator.validate_station_code("")
        self.assertFalse(is_valid)
        self.assertIn("不能為空", error_msg)

    def test_validate_search_query_valid(self):
        """測試有效搜尋查詢"""
        valid_queries = ['台北', '1000', '台北車站', '板橋', '']

        for query in valid_queries:
            is_valid, error_msg = self.validator.validate_search_query(query)
            self.assertTrue(is_valid, f"搜尋查詢 '{query}' 應該有效")
            self.assertEqual(error_msg, "")

    def test_validate_search_query_invalid(self):
        """測試無效搜尋查詢"""
        invalid_queries = [
            '<script>alert("test")</script>',
            "'; DROP TABLE stations; --",
            'a' * 51,  # 過長
            'test/*comment*/',
        ]

        for query in invalid_queries:
            is_valid, error_msg = self.validator.validate_search_query(query)
            self.assertFalse(is_valid, f"搜尋查詢 '{query}' 應該無效")
            self.assertNotEqual(error_msg, "")

    def test_validate_station_list_valid(self):
        """測試有效車站列表"""
        valid_lists = [
            ['1000'],
            ['1000', '1001'],
            ['1000', '1001', '1002', '1003', '1004'],  # 最多5個
        ]

        for station_list in valid_lists:
            is_valid, error_msg = self.validator.validate_station_list(station_list)
            self.assertTrue(is_valid, f"車站列表 {station_list} 應該有效")
            self.assertEqual(error_msg, "")

    def test_validate_station_list_invalid(self):
        """測試無效車站列表"""
        # 空列表
        is_valid, error_msg = self.validator.validate_station_list([])
        self.assertFalse(is_valid)
        self.assertIn("不能為空", error_msg)

        # 超過5個車站
        too_many = ['1000', '1001', '1002', '1003', '1004', '1005']
        is_valid, error_msg = self.validator.validate_station_list(too_many)
        self.assertFalse(is_valid)
        self.assertIn("最多只能選擇 5 個", error_msg)

        # 重複車站
        duplicates = ['1000', '1001', '1000']
        is_valid, error_msg = self.validator.validate_station_list(duplicates)
        self.assertFalse(is_valid)
        self.assertIn("重複", error_msg)

        # 包含無效車站代碼
        invalid_codes = ['1000', 'ABC', '1002']
        is_valid, error_msg = self.validator.validate_station_list(invalid_codes)
        self.assertFalse(is_valid)
        self.assertIn("無效", error_msg)

    def test_validate_passenger_count_valid(self):
        """測試有效乘客數量"""
        valid_counts = [0, 100, 1000, 50000, 99999]

        for count in valid_counts:
            is_valid, error_msg = self.validator.validate_passenger_count(count)
            self.assertTrue(is_valid, f"乘客數量 {count} 應該有效")
            self.assertEqual(error_msg, "")

    def test_validate_passenger_count_invalid(self):
        """測試無效乘客數量"""
        # 負數
        is_valid, error_msg = self.validator.validate_passenger_count(-1)
        self.assertFalse(is_valid)
        self.assertIn("不能為負數", error_msg)

        # 異常高的數值
        is_valid, error_msg = self.validator.validate_passenger_count(200000)
        self.assertFalse(is_valid)
        self.assertIn("異常高", error_msg)

        # 非整數
        is_valid, error_msg = self.validator.validate_passenger_count(100.5)
        self.assertFalse(is_valid)
        self.assertIn("必須是整數", error_msg)

    def test_validate_export_filename_valid(self):
        """測試有效匯出檔案名稱"""
        valid_names = [
            'export_data.csv',
            '台鐵資料_2024.csv',
            'station_data',
            'report-2024-01-01.csv'
        ]

        for filename in valid_names:
            is_valid, error_msg = self.validator.validate_export_filename(filename)
            self.assertTrue(is_valid, f"檔案名稱 '{filename}' 應該有效")
            self.assertEqual(error_msg, "")

    def test_validate_export_filename_invalid(self):
        """測試無效匯出檔案名稱"""
        invalid_names = [
            '',  # 空字串
            '   ',  # 只有空白
            'file<name>.csv',  # 包含不允許字元
            'CON.csv',  # 保留名稱
            'a' * 256,  # 過長
        ]

        for filename in invalid_names:
            is_valid, error_msg = self.validator.validate_export_filename(filename)
            self.assertFalse(is_valid, f"檔案名稱 '{filename}' 應該無效")
            self.assertNotEqual(error_msg, "")


if __name__ == '__main__':
    unittest.main()