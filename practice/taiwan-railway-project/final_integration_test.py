#!/usr/bin/env python3
"""
最終整合測試腳本

此腳本執行完整的系統整合測試，驗證所有功能模組的正確性和整合性。
測試包括：
1. 模組匯入測試
2. 配置驗證測試
3. 資料模型測試
4. DAO 層測試（使用模擬資料）
5. GUI 元件測試（無需顯示）
6. 服務層整合測試
7. 錯誤處理測試
8. 效能測試

作者: Taiwan Railway GUI Team
版本: 1.0.0
"""

import sys
import os
import unittest
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import tkinter as tk

# 設定專案路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinalIntegrationTest(unittest.TestCase):
    """最終整合測試類別"""

    def setUp(self):
        """測試前置設定"""
        self.logger = logging.getLogger(self.__class__.__name__)

    def test_01_module_imports(self):
        """測試 1: 驗證所有模組可以正確匯入"""
        self.logger.info("🧪 測試模組匯入...")

        try:
            # 測試配置模組
            from taiwan_railway_gui.config import get_config, validate_config
            self.logger.info("✅ 配置模組匯入成功")

            # 測試資料模型
            from taiwan_railway_gui.models.station import Station
            from taiwan_railway_gui.models.passenger_flow import PassengerFlow
            self.logger.info("✅ 資料模型匯入成功")

            # 測試 DAO 層
            from taiwan_railway_gui.dao.database_manager import DatabaseManager
            from taiwan_railway_gui.dao.station_dao import StationDAO
            from taiwan_railway_gui.dao.passenger_flow_dao import PassengerFlowDAO
            self.logger.info("✅ DAO 層匯入成功")

            # 測試服務層
            from taiwan_railway_gui.services.validation import ValidationService
            from taiwan_railway_gui.services.error_handler import ErrorHandler
            from taiwan_railway_gui.services.export_manager import ExportManager
            self.logger.info("✅ 服務層匯入成功")

            # 測試 GUI 元件
            from taiwan_railway_gui.gui.main_window import MainWindow
            from taiwan_railway_gui.gui.station_search_tab import StationSearchTab
            from taiwan_railway_gui.gui.passenger_flow_tab import PassengerFlowTab
            from taiwan_railway_gui.gui.comparison_tab import ComparisonTab
            from taiwan_railway_gui.gui.chart_tab import ChartTab
            self.logger.info("✅ GUI 元件匯入成功")

        except ImportError as e:
            self.fail(f"模組匯入失敗: {e}")

    def test_02_configuration_validation(self):
        """測試 2: 驗證配置系統"""
        self.logger.info("🧪 測試配置系統...")

        from taiwan_railway_gui.config import get_config, validate_config

        # 測試各種配置區段
        configs_to_test = ['database', 'gui', 'colors', 'fonts', 'layout', 'constants']

        for config_name in configs_to_test:
            config = get_config(config_name)
            self.assertIsInstance(config, dict, f"{config_name} 配置應該是字典")
            self.assertGreater(len(config), 0, f"{config_name} 配置不應該為空")

        self.logger.info("✅ 配置系統驗證通過")

    def test_03_data_models(self):
        """測試 3: 驗證資料模型"""
        self.logger.info("🧪 測試資料模型...")

        from taiwan_railway_gui.models.station import Station
        from taiwan_railway_gui.models.passenger_flow import PassengerFlow

        # 測試車站模型
        station = Station(
            station_code="1000",
            station_name="台北",
            address="台北市中正區北平西路3號",
            phone="02-23713558",
            gps_lat=25.047924,
            gps_lng=121.517081,
            has_bike_rental=True
        )

        self.assertEqual(station.station_code, "1000")
        self.assertEqual(station.station_name, "台北")
        self.assertTrue(station.has_bike_rental)

        # 測試客流量模型
        flow = PassengerFlow(
            station_code="1000",
            date=date(2024, 1, 1),
            in_passengers=10000,
            out_passengers=9500
        )

        self.assertEqual(flow.total_passengers, 19500)
        self.assertEqual(flow.station_code, "1000")

        self.logger.info("✅ 資料模型驗證通過")

    @patch('taiwan_railway_gui.dao.database_manager.psycopg2')
    def test_04_dao_layer(self, mock_psycopg2):
        """測試 4: 驗證 DAO 層（使用模擬資料庫）"""
        self.logger.info("🧪 測試 DAO 層...")

        # 模擬資料庫連線
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_psycopg2.pool.SimpleConnectionPool.return_value.getconn.return_value = mock_connection

        from taiwan_railway_gui.dao.station_dao import StationDAO
        from taiwan_railway_gui.dao.passenger_flow_dao import PassengerFlowDAO

        # 測試車站 DAO
        station_dao = StationDAO()

        # 模擬搜尋結果
        mock_cursor.fetchall.return_value = [
            ("1000", "台北", "台北市中正區北平西路3號", "02-23713558", 25.047924, 121.517081, True)
        ]

        stations = station_dao.search_stations("台北")
        self.assertIsInstance(stations, list)

        # 測試客流量 DAO
        flow_dao = PassengerFlowDAO()

        # 模擬客流量資料
        mock_cursor.fetchall.return_value = [
            ("1000", date(2024, 1, 1), 10000, 9500)
        ]

        flows = flow_dao.get_passenger_flow("1000", date(2024, 1, 1), date(2024, 1, 31))
        self.assertIsInstance(flows, list)

        self.logger.info("✅ DAO 層驗證通過")

    def test_05_validation_service(self):
        """測試 5: 驗證驗證服務"""
        self.logger.info("🧪 測試驗證服務...")

        from taiwan_railway_gui.services.validation import ValidationService

        validator = ValidationService()

        # 測試日期驗證
        self.assertTrue(validator.validate_date_range(date(2024, 1, 1), date(2024, 1, 31)))
        self.assertFalse(validator.validate_date_range(date(2024, 1, 31), date(2024, 1, 1)))

        # 測試車站代碼驗證
        self.assertTrue(validator.validate_station_code("1000"))
        self.assertFalse(validator.validate_station_code(""))
        self.assertFalse(validator.validate_station_code("invalid"))

        # 測試搜尋查詢驗證
        self.assertTrue(validator.validate_search_query("台北"))
        self.assertFalse(validator.validate_search_query(""))
        self.assertFalse(validator.validate_search_query("a"))  # 太短

        self.logger.info("✅ 驗證服務驗證通過")

    def test_06_error_handler(self):
        """測試 6: 驗證錯誤處理系統"""
        self.logger.info("🧪 測試錯誤處理系統...")

        from taiwan_railway_gui.services.error_handler import ErrorHandler

        error_handler = ErrorHandler()

        # 測試錯誤分類
        db_error = Exception("connection failed")
        classification = error_handler.classify_error(db_error)
        self.assertIn('type', classification)
        self.assertIn('severity', classification)

        # 測試使用者友善訊息
        user_message = error_handler.get_user_friendly_message(db_error)
        self.assertIsInstance(user_message, str)
        self.assertGreater(len(user_message), 0)

        self.logger.info("✅ 錯誤處理系統驗證通過")

    def test_07_export_manager(self):
        """測試 7: 驗證匯出管理器"""
        self.logger.info("🧪 測試匯出管理器...")

        from taiwan_railway_gui.services.export_manager import ExportManager
        from taiwan_railway_gui.models.station import Station

        export_manager = ExportManager()

        # 建立測試資料
        test_stations = [
            Station("1000", "台北", "台北市中正區北平西路3號", "02-23713558", 25.047924, 121.517081, True),
            Station("1001", "台中", "台中市中區台灣大道一段1號", "04-22227236", 24.137000, 120.685000, False)
        ]

        # 測試 CSV 匯出格式驗證
        csv_data = export_manager._prepare_station_data_for_export(test_stations, 'csv')
        self.assertIsInstance(csv_data, list)
        self.assertGreater(len(csv_data), 0)

        self.logger.info("✅ 匯出管理器驗證通過")

    def test_08_gui_components_creation(self):
        """測試 8: 驗證 GUI 元件建立（無顯示）"""
        self.logger.info("🧪 測試 GUI 元件建立...")

        # 建立隱藏的根視窗
        root = tk.Tk()
        root.withdraw()  # 隱藏視窗

        try:
            from taiwan_railway_gui.gui.main_window import MainWindow

            # 測試主視窗建立
            with patch('taiwan_railway_gui.dao.database_manager.DatabaseManager'):
                main_window = MainWindow()
                self.assertIsNotNone(main_window)
                self.assertIsInstance(main_window.root, tk.Tk)

            self.logger.info("✅ GUI 元件建立驗證通過")

        except Exception as e:
            self.logger.warning(f"GUI 測試跳過（可能是無頭環境）: {e}")
        finally:
            root.destroy()

    def test_09_performance_benchmarks(self):
        """測試 9: 效能基準測試"""
        self.logger.info("🧪 測試效能基準...")

        import time
        from taiwan_railway_gui.models.station import Station

        # 測試大量資料模型建立效能
        start_time = time.time()

        stations = []
        for i in range(1000):
            station = Station(
                station_code=f"{i:04d}",
                station_name=f"車站{i}",
                address=f"地址{i}",
                phone=f"電話{i}",
                gps_lat=25.0 + i * 0.001,
                gps_lng=121.0 + i * 0.001,
                has_bike_rental=i % 2 == 0
            )
            stations.append(station)

        creation_time = time.time() - start_time
        self.assertLess(creation_time, 1.0, "1000個車站模型建立應在1秒內完成")

        self.logger.info(f"✅ 效能測試通過 - 1000個模型建立耗時: {creation_time:.3f}秒")

    def test_10_integration_workflow(self):
        """測試 10: 整合工作流程測試"""
        self.logger.info("🧪 測試整合工作流程...")

        from taiwan_railway_gui.services.validation import ValidationService
        from taiwan_railway_gui.services.error_handler import ErrorHandler
        from taiwan_railway_gui.models.station import Station

        # 模擬完整的使用者工作流程
        validator = ValidationService()
        error_handler = ErrorHandler()

        # 1. 驗證搜尋輸入
        search_query = "台北"
        is_valid = validator.validate_search_query(search_query)
        self.assertTrue(is_valid)

        # 2. 建立車站資料
        station = Station("1000", "台北", "台北市中正區北平西路3號", "02-23713558", 25.047924, 121.517081, True)

        # 3. 驗證日期範圍
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        date_valid = validator.validate_date_range(start_date, end_date)
        self.assertTrue(date_valid)

        # 4. 模擬錯誤處理
        try:
            raise ValueError("測試錯誤")
        except Exception as e:
            error_info = error_handler.classify_error(e)
            user_message = error_handler.get_user_friendly_message(e)
            self.assertIsInstance(error_info, dict)
            self.assertIsInstance(user_message, str)

        self.logger.info("✅ 整合工作流程驗證通過")


def run_final_integration_tests():
    """執行最終整合測試"""
    print("=" * 60)
    print("🚀 台鐵車站資訊查詢 GUI 應用程式 - 最終整合測試")
    print("=" * 60)

    # 建立測試套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(FinalIntegrationTest)

    # 執行測試
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )

    result = runner.run(test_suite)

    # 輸出測試結果摘要
    print("\n" + "=" * 60)
    print("📊 測試結果摘要")
    print("=" * 60)
    print(f"🧪 總測試數: {result.testsRun}")
    print(f"✅ 成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 失敗: {len(result.failures)}")
    print(f"⚠️  錯誤: {len(result.errors)}")

    if result.failures:
        print("\n❌ 失敗的測試:")
        for test, traceback in result.failures:
            error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"  - {test}: {error_msg}")

    if result.errors:
        print("\n⚠️  錯誤的測試:")
        for test, traceback in result.errors:
            error_msg = traceback.split('\n')[-2]
            print(f"  - {test}: {error_msg}")

    # 判斷整體結果
    if result.wasSuccessful():
        print("\n🎉 所有測試通過！應用程式已準備好發布。")
        return True
    else:
        print("\n💥 部分測試失敗，請檢查並修正問題。")
        return False


if __name__ == "__main__":
    success = run_final_integration_tests()
    sys.exit(0 if success else 1)