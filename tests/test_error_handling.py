"""
錯誤處理系統測試

測試統一錯誤處理機制、使用者友善訊息轉換、
多層級驗證和優雅降級功能。
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
import tempfile
import os
from taiwan_railway_gui.services.error_handler import (
    ErrorHandler, ErrorCategory, ErrorSeverity, ErrorInfo, get_error_handler, handle_error
)
from taiwan_railway_gui.services.validation import (
    ValidationService, ValidationLevel, ValidationResult, create_validation_service
)


class TestErrorHandler(unittest.TestCase):
    """錯誤處理器測試"""

    def setUp(self):
        """測試前設定"""
        self.error_handler = ErrorHandler()

    def test_error_classification(self):
        """測試錯誤分類"""
        # 資料庫錯誤
        db_error = Exception("connection failed to database")
        error_info = self.error_handler.handle_error(db_error)
        self.assertEqual(error_info.category, ErrorCategory.DATABASE)

        # 驗證錯誤
        validation_error = Exception("invalid date format")
        error_info = self.error_handler.handle_error(validation_error)
        self.assertEqual(error_info.category, ErrorCategory.VALIDATION)

        # 檔案 I/O 錯誤
        file_error = Exception("file not found")
        error_info = self.error_handler.handle_error(file_error)
        self.assertEqual(error_info.category, ErrorCategory.FILE_IO)

    def test_severity_assessment(self):
        """測試嚴重程度評估"""
        # 致命錯誤
        critical_error = MemoryError("out of memory")
        error_info = self.error_handler.handle_error(critical_error)
        self.assertEqual(error_info.severity, ErrorSeverity.CRITICAL)

        # 嚴重錯誤
        high_error = Exception("database connection failed")
        error_info = self.error_handler.handle_error(high_error)
        self.assertEqual(error_info.severity, ErrorSeverity.HIGH)

        # 輕微錯誤
        low_error = Exception("validation failed")
        error_info = self.error_handler.handle_error(low_error)
        self.assertEqual(error_info.severity, ErrorSeverity.LOW)

    def test_user_friendly_messages(self):
        """測試使用者友善訊息"""
        # 連線失敗錯誤
        connection_error = Exception("connection_failed to database")
        error_info = self.error_handler.handle_error(connection_error)
        self.assertIn("無法連接到資料庫", error_info.user_message)
        self.assertIn("檢查網路連線", error_info.suggested_actions)

        # 無效日期範圍錯誤
        date_error = Exception("invalid_date_range specified")
        error_info = self.error_handler.handle_error(date_error)
        self.assertIn("日期範圍不正確", error_info.user_message)

    def test_error_history(self):
        """測試錯誤歷史記錄"""
        # 產生一些錯誤
        error1 = Exception("test error 1")
        error2 = Exception("test error 2")

        self.error_handler.handle_error(error1)
        self.error_handler.handle_error(error2)

        # 檢查歷史記錄
        history = self.error_handler.get_error_history()
        self.assertEqual(len(history), 2)

        # 檢查篩選功能
        db_history = self.error_handler.get_error_history(category=ErrorCategory.DATABASE)
        validation_history = self.error_handler.get_error_history(category=ErrorCategory.VALIDATION)

        # 清除歷史記錄
        self.error_handler.clear_error_history()
        history = self.error_handler.get_error_history()
        self.assertEqual(len(history), 0)

    def test_error_callbacks(self):
        """測試錯誤回調"""
        callback_called = False
        callback_error_info = None

        def test_callback(error_info):
            nonlocal callback_called, callback_error_info
            callback_called = True
            callback_error_info = error_info

        # 註冊回調
        self.error_handler.register_error_callback(ErrorCategory.DATABASE, test_callback)

        # 觸發資料庫錯誤
        db_error = Exception("database connection failed")
        error_info = self.error_handler.handle_error(db_error, category=ErrorCategory.DATABASE)

        # 檢查回調是否被呼叫
        self.assertTrue(callback_called)
        self.assertEqual(callback_error_info.error_id, error_info.error_id)

    def test_error_statistics(self):
        """測試錯誤統計"""
        # 產生不同類型的錯誤
        self.error_handler.handle_error(Exception("db error"), category=ErrorCategory.DATABASE)
        self.error_handler.handle_error(Exception("validation error"), category=ErrorCategory.VALIDATION)
        self.error_handler.handle_error(Exception("file error"), category=ErrorCategory.FILE_IO)

        # 取得統計資訊
        stats = self.error_handler.get_error_statistics()

        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['by_category']['database'], 1)
        self.assertEqual(stats['by_category']['validation'], 1)
        self.assertEqual(stats['by_category']['file_io'], 1)

    def test_fallback_error_handling(self):
        """測試降級錯誤處理"""
        # 模擬錯誤處理器本身發生錯誤的情況
        with patch.object(self.error_handler, '_classify_error', side_effect=Exception("handler error")):
            original_error = Exception("original error")
            error_info = self.error_handler.handle_error(original_error)

            # 應該返回降級錯誤資訊
            self.assertEqual(error_info.category, ErrorCategory.SYSTEM)
            self.assertEqual(error_info.severity, ErrorSeverity.CRITICAL)
            self.assertIn("系統發生嚴重錯誤", error_info.user_message)

    def test_global_error_handler(self):
        """測試全域錯誤處理器"""
        # 測試單例模式
        handler1 = get_error_handler()
        handler2 = get_error_handler()
        self.assertIs(handler1, handler2)

        # 測試便利函數
        error = Exception("test error")
        error_info = handle_error(error)
        self.assertIsInstance(error_info, ErrorInfo)


class TestEnhancedValidation(unittest.TestCase):
    """增強驗證服務測試"""

    def setUp(self):
        """測試前設定"""
        self.validation_service = ValidationService()

    def test_multi_level_date_validation(self):
        """測試多層級日期驗證"""
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)

        # 基本驗證
        result = self.validation_service.validate_with_level(
            (start_date, end_date), 'date_range', ValidationLevel.BASIC
        )
        self.assertTrue(result.is_valid)

        # 業務邏輯驗證
        result = self.validation_service.validate_with_level(
            (start_date, end_date), 'date_range', ValidationLevel.BUSINESS
        )
        self.assertTrue(result.is_valid)

        # 嚴格驗證
        result = self.validation_service.validate_with_level(
            (start_date, end_date), 'date_range', ValidationLevel.STRICT
        )
        self.assertTrue(result.is_valid)
        self.assertGreater(len(result.warnings), 0)  # 應該有警告

    def test_invalid_date_range_validation(self):
        """測試無效日期範圍驗證"""
        # 日期順序錯誤
        start_date = date(2023, 12, 31)
        end_date = date(2023, 1, 1)

        result = self.validation_service.validate_with_level(
            (start_date, end_date), 'date_range', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "invalid_date_order")
        self.assertIsNotNone(result.corrected_value)

        # 未來日期
        future_start = date(2030, 1, 1)
        future_end = date(2030, 12, 31)

        result = self.validation_service.validate_with_level(
            (future_start, future_end), 'date_range', ValidationLevel.BUSINESS
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "future_date")

    def test_station_code_validation(self):
        """測試車站代碼驗證"""
        # 有效代碼
        result = self.validation_service.validate_with_level(
            "1001", 'station_code', ValidationLevel.BUSINESS
        )
        self.assertTrue(result.is_valid)

        # 無效格式
        result = self.validation_service.validate_with_level(
            "abc", 'station_code', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "invalid_format")

        # 空值
        result = self.validation_service.validate_with_level(
            "", 'station_code', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "required_field")

        # 長度過長
        result = self.validation_service.validate_with_level(
            "12345678901", 'station_code', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "too_long")

    def test_search_query_validation(self):
        """測試搜尋查詢驗證"""
        # 有效查詢
        result = self.validation_service.validate_with_level(
            "台北", 'search_query', ValidationLevel.BUSINESS
        )
        self.assertTrue(result.is_valid)

        # 空查詢（允許）
        result = self.validation_service.validate_with_level(
            "", 'search_query', ValidationLevel.BASIC
        )
        self.assertTrue(result.is_valid)
        self.assertGreater(len(result.warnings), 0)

        # 危險字元
        result = self.validation_service.validate_with_level(
            "test<script>", 'search_query', ValidationLevel.BUSINESS
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "forbidden_chars")

        # 危險關鍵字
        result = self.validation_service.validate_with_level(
            "DROP TABLE", 'search_query', ValidationLevel.BUSINESS
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "forbidden_words")

    def test_station_list_validation(self):
        """測試車站列表驗證"""
        # 有效列表
        result = self.validation_service.validate_with_level(
            ["1001", "1002", "1003"], 'station_list', ValidationLevel.BUSINESS
        )
        self.assertTrue(result.is_valid)

        # 空列表
        result = self.validation_service.validate_with_level(
            [], 'station_list', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "empty_list")

        # 過多項目
        result = self.validation_service.validate_with_level(
            ["1001", "1002", "1003", "1004", "1005", "1006"], 'station_list', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "too_many_items")

        # 重複項目
        result = self.validation_service.validate_with_level(
            ["1001", "1002", "1001"], 'station_list', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "duplicate_values")
        self.assertIsNotNone(result.corrected_value)

    def test_passenger_count_validation(self):
        """測試乘客數量驗證"""
        # 有效數量
        result = self.validation_service.validate_with_level(
            5000, 'passenger_count', ValidationLevel.BUSINESS
        )
        self.assertTrue(result.is_valid)

        # 負數
        result = self.validation_service.validate_with_level(
            -100, 'passenger_count', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "value_too_small")

        # 異常高的數值
        result = self.validation_service.validate_with_level(
            150000, 'passenger_count', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "value_too_large")

        # 高數值警告
        result = self.validation_service.validate_with_level(
            60000, 'passenger_count', ValidationLevel.BUSINESS
        )
        self.assertTrue(result.is_valid)
        self.assertGreater(len(result.warnings), 0)

    def test_filename_validation(self):
        """測試檔案名稱驗證"""
        # 有效檔案名稱
        result = self.validation_service.validate_with_level(
            "report.csv", 'filename', ValidationLevel.BUSINESS
        )
        self.assertTrue(result.is_valid)

        # 空檔案名稱
        result = self.validation_service.validate_with_level(
            "", 'filename', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "empty_filename")

        # 禁用字元
        result = self.validation_service.validate_with_level(
            "file<name>.csv", 'filename', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "forbidden_chars")
        self.assertIsNotNone(result.corrected_value)

        # 保留名稱
        result = self.validation_service.validate_with_level(
            "CON.txt", 'filename', ValidationLevel.BASIC
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "reserved_name")

        # 中文檔案名稱警告
        result = self.validation_service.validate_with_level(
            "報告.csv", 'filename', ValidationLevel.STRICT
        )
        self.assertTrue(result.is_valid)
        self.assertGreater(len(result.warnings), 0)

    def test_backward_compatibility(self):
        """測試向後相容性"""
        # 測試原有的方法仍然可用
        is_valid, error_msg = self.validation_service.validate_date_range(
            date(2023, 1, 1), date(2023, 12, 31)
        )
        self.assertTrue(is_valid)

        is_valid, error_msg = self.validation_service.validate_station_code("1001")
        self.assertTrue(is_valid)

        is_valid, error_msg = self.validation_service.validate_search_query("台北")
        self.assertTrue(is_valid)

    def test_validation_service_creation(self):
        """測試驗證服務建立"""
        service = create_validation_service()
        self.assertIsInstance(service, ValidationService)


class TestErrorHandlingIntegration(unittest.TestCase):
    """錯誤處理整合測試"""

    def setUp(self):
        """測試前設定"""
        self.error_handler = get_error_handler()
        self.validation_service = create_validation_service()

    def test_validation_error_handling(self):
        """測試驗證錯誤處理整合"""
        # 建立一個會拋出異常的驗證情境
        try:
            # 故意傳入錯誤的參數類型
            self.validation_service.validate_with_level(
                None, 'invalid_type', ValidationLevel.BASIC
            )
        except Exception as e:
            error_info = self.error_handler.handle_error(
                e,
                context={"validation_type": "invalid_type"},
                category=ErrorCategory.VALIDATION
            )

            self.assertEqual(error_info.category, ErrorCategory.VALIDATION)
            self.assertIn("驗證", error_info.user_message)

    def test_database_error_simulation(self):
        """測試資料庫錯誤模擬"""
        # 模擬資料庫連線錯誤
        db_error = Exception("psycopg2.OperationalError: connection failed")
        error_info = self.error_handler.handle_error(db_error)

        self.assertEqual(error_info.category, ErrorCategory.DATABASE)
        self.assertEqual(error_info.severity, ErrorSeverity.HIGH)
        self.assertIn("資料庫", error_info.user_message)

    def test_file_io_error_simulation(self):
        """測試檔案 I/O 錯誤模擬"""
        # 模擬檔案不存在錯誤
        file_error = FileNotFoundError("file not found: report.csv")
        error_info = self.error_handler.handle_error(file_error)

        self.assertEqual(error_info.category, ErrorCategory.FILE_IO)
        self.assertIn("檔案", error_info.user_message)

    def test_graceful_degradation_scenario(self):
        """測試優雅降級情境"""
        # 模擬一個需要降級處理的錯誤
        critical_error = MemoryError("out of memory")
        error_info = self.error_handler.handle_error(critical_error)

        self.assertEqual(error_info.severity, ErrorSeverity.CRITICAL)
        self.assertIn("記憶體", error_info.user_message)
        self.assertIn("重新啟動", error_info.suggested_actions)

    def test_error_context_preservation(self):
        """測試錯誤上下文保存"""
        context = {
            "user_action": "search_stations",
            "query": "台北",
            "timestamp": datetime.now().isoformat()
        }

        error = Exception("search failed")
        error_info = self.error_handler.handle_error(error, context=context)

        self.assertEqual(error_info.context["user_action"], "search_stations")
        self.assertEqual(error_info.context["query"], "台北")

    def test_concurrent_error_handling(self):
        """測試並發錯誤處理"""
        import threading
        import time

        errors = []

        def generate_error(error_id):
            try:
                time.sleep(0.1)  # 模擬一些處理時間
                raise Exception(f"concurrent error {error_id}")
            except Exception as e:
                error_info = self.error_handler.handle_error(e)
                errors.append(error_info)

        # 建立多個執行緒同時產生錯誤
        threads = []
        for i in range(5):
            thread = threading.Thread(target=generate_error, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有執行緒完成
        for thread in threads:
            thread.join()

        # 檢查所有錯誤都被正確處理
        self.assertEqual(len(errors), 5)

        # 檢查錯誤歷史記錄
        history = self.error_handler.get_error_history()
        self.assertGreaterEqual(len(history), 5)


if __name__ == '__main__':
    unittest.main()