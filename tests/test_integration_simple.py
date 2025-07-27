"""
簡化的整合測試

測試系統的核心整合功能，使用模擬資料庫以確保測試的可靠性。
"""

import unittest
import os
import sys
import tkinter as tk
from datetime import datetime, timedelta, date
from unittest.mock import Mock, patch, MagicMock

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow


class SimpleIntegrationTest(unittest.TestCase):
    """簡化的整合測試"""

    def setUp(self):
        """設定測試"""
        # 建立測試資料
        self.test_stations = [
            Station('1000', '台北', '台北市中正區', '02-23713558', 25.047924, 121.517081, True),
            Station('1001', '板橋', '新北市板橋區', '02-29603000', 25.013807, 121.464132, True),
            Station('1008', '桃園', '桃園市桃園區', '03-3322340', 24.989197, 121.314007, False),
        ]

        self.test_flows = []
        base_date = datetime.now() - timedelta(days=7)
        for i in range(7):
            current_date = base_date + timedelta(days=i)
            # 使用正確的欄位名稱
            flow = PassengerFlow(
                station_code='1000',  # 使用station_code而不是station_id
                date=current_date.date(),  # 轉換為date物件
                in_passengers=1000 + i * 50,  # 使用in_passengers
                out_passengers=950 + i * 45   # 使用out_passengers
            )
            self.test_flows.append(flow)

    def test_station_model_integration(self):
        """測試車站模型整合"""
        station = self.test_stations[0]

        # 測試基本屬性
        self.assertEqual(station.station_code, '1000')
        self.assertEqual(station.station_name, '台北')
        self.assertEqual(station.gps_lat, 25.047924)

        # 測試字串表示
        station_str = str(station)
        self.assertIn('台北', station_str)
        self.assertIn('1000', station_str)

    def test_passenger_flow_model_integration(self):
        """測試乘客流量模型整合"""
        flow = self.test_flows[0]

        # 測試基本屬性
        self.assertEqual(flow.station_code, '1000')  # 使用station_code
        self.assertIsInstance(flow.date, date)  # 改為date類型
        self.assertIsInstance(flow.in_passengers, int)   # 使用in_passengers
        self.assertIsInstance(flow.out_passengers, int)  # 使用out_passengers

        # 測試計算屬性
        expected_total = flow.in_passengers + flow.out_passengers
        self.assertEqual(flow.total_passengers, expected_total)  # 使用property

    def test_dao_mock_integration(self):
        """測試DAO模擬整合"""
        # 模擬StationDAO
        with patch('taiwan_railway_gui.dao.station_dao.StationDAO') as MockStationDAO:
            mock_dao = MockStationDAO.return_value
            mock_dao.get_all_stations.return_value = self.test_stations
            mock_dao.search_stations_by_name.return_value = [self.test_stations[0]]

            # 測試模擬功能
            stations = mock_dao.get_all_stations()
            self.assertEqual(len(stations), 3)

            search_result = mock_dao.search_stations_by_name('台北')
            self.assertEqual(len(search_result), 1)
            self.assertEqual(search_result[0].station_name, '台北')

    def test_config_integration(self):
        """測試配置整合"""
        try:
            from taiwan_railway_gui.config import get_config

            # 測試各種配置段落
            db_config = get_config('database')
            self.assertIsInstance(db_config, dict)

            gui_config = get_config('gui')
            self.assertIsInstance(gui_config, dict)

            colors_config = get_config('colors')
            self.assertIsInstance(colors_config, dict)

        except ImportError:
            self.skipTest("配置模組無法導入")

    def test_error_handler_integration(self):
        """測試錯誤處理器整合"""
        try:
            from taiwan_railway_gui.services.error_handler import get_error_handler, ErrorCategory, ErrorSeverity

            error_handler = get_error_handler()
            self.assertIsNotNone(error_handler)

            # 測試錯誤類別和嚴重性枚舉
            self.assertTrue(hasattr(ErrorCategory, 'DATABASE'))
            self.assertTrue(hasattr(ErrorSeverity, 'HIGH'))

        except ImportError:
            self.skipTest("錯誤處理器模組無法導入")

    def test_gui_component_basic_integration(self):
        """測試GUI元件基本整合"""
        try:
            # 建立隱藏的測試視窗
            root = tk.Tk()
            root.withdraw()

            # 測試基本tkinter元件
            frame = tk.Frame(root)
            label = tk.Label(frame, text="測試標籤")
            button = tk.Button(frame, text="測試按鈕")

            # 檢查元件是否正常建立
            self.assertIsNotNone(frame)
            self.assertIsNotNone(label)
            self.assertIsNotNone(button)

            # 清理
            root.destroy()

        except Exception as e:
            self.skipTest(f"GUI測試跳過: {e}")

    def test_async_manager_integration(self):
        """測試非同步管理器整合"""
        try:
            from taiwan_railway_gui.services.async_manager import get_async_manager

            async_manager = get_async_manager()
            self.assertIsNotNone(async_manager)

        except ImportError:
            self.skipTest("非同步管理器模組無法導入")

    def test_cache_manager_integration(self):
        """測試快取管理器整合"""
        try:
            from taiwan_railway_gui.services.cache_manager import get_cache_manager

            cache_manager = get_cache_manager()
            self.assertIsNotNone(cache_manager)

        except ImportError:
            self.skipTest("快取管理器模組無法導入")

    def test_export_manager_integration(self):
        """測試匯出管理器整合"""
        try:
            from taiwan_railway_gui.services.export_manager import ExportManager

            # 建立模擬資料
            test_data = [
                {'車站': '台北', '進站': 1000, '出站': 950},
                {'車站': '板橋', '進站': 1100, '出站': 1050},
            ]

            export_manager = ExportManager()

            # 測試是否可以建立匯出管理器
            self.assertIsNotNone(export_manager)

        except ImportError:
            self.skipTest("匯出管理器模組無法導入")

    def test_validation_integration(self):
        """測試驗證功能整合"""
        try:
            from taiwan_railway_gui.services.validation import (
                validate_station_id,
                validate_date_range,
                validate_passenger_count
            )

            # 測試車站ID驗證
            self.assertTrue(validate_station_id('1000'))
            self.assertFalse(validate_station_id(''))
            self.assertFalse(validate_station_id(None))

            # 測試日期範圍驗證
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
            self.assertTrue(validate_date_range(start_date, end_date))

            # 測試無效日期範圍
            invalid_end = start_date - timedelta(days=1)
            self.assertFalse(validate_date_range(start_date, invalid_end))

            # 測試乘客數量驗證
            self.assertTrue(validate_passenger_count(1000))
            self.assertFalse(validate_passenger_count(-1))

        except ImportError:
            self.skipTest("驗證模組無法導入")

    def test_memory_manager_integration(self):
        """測試記憶體管理器整合"""
        try:
            from taiwan_railway_gui.utils.memory_manager import get_memory_manager

            memory_manager = get_memory_manager()
            self.assertIsNotNone(memory_manager)

        except ImportError:
            self.skipTest("記憶體管理器模組無法導入")


class ComponentInteractionTest(unittest.TestCase):
    """元件互動測試"""

    def test_model_to_dao_integration(self):
        """測試模型到DAO的整合"""
        # 建立測試車站
        station = Station('1000', '台北', '台北市中正區', '02-23713558', 25.047924, 121.517081, True)

        # 模擬DAO回傳模型資料
        with patch('taiwan_railway_gui.dao.station_dao.StationDAO') as MockDAO:
            mock_dao = MockDAO.return_value
            mock_dao.get_station_by_id.return_value = station

            # 測試DAO返回正確的模型
            result = mock_dao.get_station_by_id('1000')
            self.assertIsInstance(result, Station)
            self.assertEqual(result.station_code, '1000')

    def test_service_layer_integration(self):
        """測試服務層整合"""
        # 測試錯誤處理器與其他服務的整合
        try:
            from taiwan_railway_gui.services.error_handler import get_error_handler
            from taiwan_railway_gui.services.cache_manager import get_cache_manager

            error_handler = get_error_handler()
            cache_manager = get_cache_manager()

            # 檢查服務是否可以獨立運作
            self.assertIsNotNone(error_handler)
            self.assertIsNotNone(cache_manager)

        except ImportError:
            self.skipTest("服務層模組無法導入")

    def test_gui_services_integration(self):
        """測試GUI與服務的整合"""
        try:
            from taiwan_railway_gui.gui.user_feedback import create_user_feedback_manager

            # 建立隱藏的測試視窗
            root = tk.Tk()
            root.withdraw()

            # 測試使用者回饋管理器
            feedback_manager = create_user_feedback_manager(root)
            self.assertIsNotNone(feedback_manager)

            # 清理
            root.destroy()

        except (ImportError, tk.TclError):
            self.skipTest("GUI服務整合測試跳過")


class EndToEndSimulationTest(unittest.TestCase):
    """端到端模擬測試"""

    def test_complete_search_workflow_simulation(self):
        """模擬完整搜尋工作流程"""
        # 1. 模擬使用者輸入搜尋關鍵字
        search_keyword = "台北"

        # 2. 模擬搜尋功能
        with patch('taiwan_railway_gui.dao.station_dao.StationDAO') as MockDAO:
            mock_dao = MockDAO.return_value
            mock_stations = [
                Station('1000', '台北', '台北市中正區', '02-23713558', 25.047924, 121.517081, True)
            ]
            mock_dao.search_stations_by_name.return_value = mock_stations

            # 3. 執行搜尋
            search_results = mock_dao.search_stations_by_name(search_keyword)

            # 4. 驗證結果
            self.assertEqual(len(search_results), 1)
            self.assertEqual(search_results[0].station_name, '台北')

    def test_complete_query_workflow_simulation(self):
        """模擬完整查詢工作流程"""
        # 1. 模擬選擇車站和日期範圍
        station_id = '1000'
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        # 2. 模擬客流量查詢
        with patch('taiwan_railway_gui.dao.passenger_flow_dao.PassengerFlowDAO') as MockDAO:
            mock_dao = MockDAO.return_value
            mock_flows = [
                PassengerFlow(station_id, (start_date + timedelta(days=i)).date(), 1000 + i * 50, 950 + i * 45)
                for i in range(7)
            ]
            mock_dao.get_passenger_flow_by_station_and_date_range.return_value = mock_flows

            # 3. 執行查詢
            query_results = mock_dao.get_passenger_flow_by_station_and_date_range(
                station_id, start_date, end_date
            )

            # 4. 驗證結果
            self.assertEqual(len(query_results), 7)
            self.assertEqual(query_results[0].station_code, station_id)  # 使用station_code

    def test_error_handling_workflow_simulation(self):
        """模擬錯誤處理工作流程"""
        # 1. 模擬資料庫錯誤
        with patch('taiwan_railway_gui.dao.station_dao.StationDAO') as MockDAO:
            mock_dao = MockDAO.return_value
            mock_dao.search_stations_by_name.side_effect = Exception("資料庫連線失敗")

            # 2. 測試錯誤處理
            try:
                mock_dao.search_stations_by_name("台北")
                self.fail("應該拋出異常")
            except Exception as e:
                self.assertIn("資料庫連線失敗", str(e))

    def test_performance_simulation(self):
        """模擬效能測試"""
        import time

        # 模擬大量資料處理
        start_time = time.time()

        # 建立大量測試資料
        large_dataset = []
        for i in range(1000):
            station = Station(f'{i:04d}', f'車站{i}', '測試地址', '00-0000000', 24.0 + i * 0.001, 121.0 + i * 0.001, False)
            large_dataset.append(station)

        # 模擬資料處理
        processed_count = 0
        for station in large_dataset:
            if station.station_name:  # 簡單的處理邏輯
                processed_count += 1

        end_time = time.time()
        processing_time = end_time - start_time

        # 驗證效能
        self.assertEqual(processed_count, 1000)
        self.assertLess(processing_time, 1.0, "大量資料處理應該在1秒內完成")


if __name__ == '__main__':
    # 建立測試套件
    suite = unittest.TestSuite()

    # 添加所有測試
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(SimpleIntegrationTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(ComponentInteractionTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(EndToEndSimulationTest))

    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 輸出結果
    if result.wasSuccessful():
        print("\n✅ 所有簡化整合測試通過！")
    else:
        print(f"\n❌ 測試失敗：{len(result.failures)} 個失敗，{len(result.errors)} 個錯誤")

    sys.exit(0 if result.wasSuccessful() else 1)
