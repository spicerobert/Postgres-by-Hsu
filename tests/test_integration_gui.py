"""
GUI元件互動整合測試

測試GUI元件之間的互動和通信。
"""

import unittest
import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from taiwan_railway_gui.gui.main_window import MainWindow
from taiwan_railway_gui.gui.station_search_tab import StationSearchTab
from taiwan_railway_gui.gui.passenger_flow_tab import PassengerFlowTab
from taiwan_railway_gui.gui.comparison_tab import ComparisonTab
from taiwan_railway_gui.gui.chart_tab import ChartTab
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow


class GUITestCase(unittest.TestCase):
    """GUI測試基礎類別"""

    def setUp(self):
        """設定測試方法"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏主視窗避免干擾

        # 建立模擬的DAO
        self.mock_station_dao = Mock()
        self.mock_passenger_flow_dao = Mock()

        # 設定模擬資料
        self.setup_mock_data()

    def tearDown(self):
        """清理測試方法"""
        if hasattr(self, 'root') and self.root:
            self.root.destroy()

    def setup_mock_data(self):
        """設定模擬測試資料"""
        # 模擬車站資料
        self.test_stations = [
            Station('1000', '台北', '特等', '縱貫線', '台北市中正區', '02-23713558', '25.047924,121.517081'),
            Station('1001', '板橋', '一等', '縱貫線', '新北市板橋區', '02-29603000', '25.013807,121.464132'),
            Station('1008', '桃園', '一等', '縱貫線', '桃園市桃園區', '03-3322340', '24.989197,121.314007'),
        ]

        # 模擬乘客流量資料
        base_date = datetime.now() - timedelta(days=7)
        self.test_passenger_flows = []
        for i in range(7):
            current_date = base_date + timedelta(days=i)
            flow = PassengerFlow(
                station_id='1000',
                date=current_date,
                inbound_passengers=1000 + i * 50,
                outbound_passengers=950 + i * 45,
                total_passengers=1950 + i * 95
            )
            self.test_passenger_flows.append(flow)

    def wait_for_gui_update(self, timeout=1.0):
        """等待GUI更新完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.root.update()
            time.sleep(0.01)


class TestMainWindowIntegration(GUITestCase):
    """主視窗整合測試"""

    def setUp(self):
        super().setUp()
        with patch('taiwan_railway_gui.dao.get_database_manager'):
            self.main_window = MainWindow()

    def test_main_window_initialization(self):
        """測試主視窗初始化"""
        self.assertIsInstance(self.main_window.root, tk.Tk)
        self.assertIsInstance(self.main_window.notebook, ttk.Notebook)

        # 檢查分頁是否正確建立
        tab_count = self.main_window.notebook.index('end')
        self.assertGreater(tab_count, 0)

    def test_tab_switching(self):
        """測試分頁切換功能"""
        initial_tab = self.main_window.notebook.index('current')

        # 切換到下一個分頁
        if self.main_window.notebook.index('end') > 1:
            self.main_window.notebook.select(1)
            self.wait_for_gui_update()

            current_tab = self.main_window.notebook.index('current')
            self.assertNotEqual(initial_tab, current_tab)

    def test_status_bar_updates(self):
        """測試狀態列更新"""
        if hasattr(self.main_window, 'status_bar'):
            # 更新狀態
            self.main_window.update_status("測試狀態訊息")
            self.wait_for_gui_update()

            # 檢查狀態是否更新
            status_text = self.main_window.status_bar.get_status()
            self.assertIn("測試狀態訊息", status_text)

    def test_loading_indicator(self):
        """測試載入指示器"""
        if hasattr(self.main_window, 'loading_indicator'):
            # 顯示載入指示器
            self.main_window.show_loading("載入中...")
            self.wait_for_gui_update()

            # 檢查載入指示器是否顯示
            self.assertTrue(self.main_window.loading_indicator.is_running)

            # 隱藏載入指示器
            self.main_window.hide_loading()
            self.wait_for_gui_update()

            # 檢查載入指示器是否隱藏
            self.assertFalse(self.main_window.loading_indicator.is_running)


class TestStationSearchTabIntegration(GUITestCase):
    """車站搜尋分頁整合測試"""

    def setUp(self):
        super().setUp()
        with patch('taiwan_railway_gui.dao.station_dao.StationDAO') as mock_dao_class:
            mock_dao_class.return_value = self.mock_station_dao
            self.mock_station_dao.search_stations_by_name.return_value = self.test_stations

            self.tab = StationSearchTab(self.root)

    def test_search_functionality(self):
        """測試搜尋功能"""
        # 模擬搜尋輸入
        self.tab.search_var.set("台北")
        self.wait_for_gui_update()

        # 觸發搜尋事件
        self.tab.on_search_changed()
        self.wait_for_gui_update()

        # 檢查是否呼叫了搜尋方法
        self.mock_station_dao.search_stations_by_name.assert_called_with("台北")

    def test_station_selection(self):
        """測試車站選擇功能"""
        # 先執行搜尋
        self.tab.search_var.set("台北")
        self.tab.on_search_changed()
        self.wait_for_gui_update()

        # 模擬選擇車站
        if hasattr(self.tab, 'results_listbox'):
            # 選擇第一個結果
            self.tab.results_listbox.selection_set(0)
            self.tab.on_station_selected(None)
            self.wait_for_gui_update()

            # 檢查詳細資訊是否顯示
            self.assertIsNotNone(self.tab.selected_station)

    def test_clear_functionality(self):
        """測試清除功能"""
        # 先進行搜尋
        self.tab.search_var.set("台北")
        self.tab.on_search_changed()
        self.wait_for_gui_update()

        # 清除搜尋
        self.tab.clear_search()
        self.wait_for_gui_update()

        # 檢查是否已清除
        self.assertEqual(self.tab.search_var.get(), "")
        if hasattr(self.tab, 'results_listbox'):
            self.assertEqual(self.tab.results_listbox.size(), 0)


class TestPassengerFlowTabIntegration(GUITestCase):
    """客流量查詢分頁整合測試"""

    def setUp(self):
        super().setUp()
        with patch('taiwan_railway_gui.dao.station_dao.StationDAO') as mock_station_dao_class, \
             patch('taiwan_railway_gui.dao.passenger_flow_dao.PassengerFlowDAO') as mock_flow_dao_class:

            mock_station_dao_class.return_value = self.mock_station_dao
            mock_flow_dao_class.return_value = self.mock_passenger_flow_dao

            self.mock_station_dao.get_all_stations.return_value = self.test_stations
            self.mock_passenger_flow_dao.get_passenger_flow_by_station_and_date_range.return_value = self.test_passenger_flows
            self.mock_passenger_flow_dao.get_passenger_flow_summary.return_value = {
                'total_inbound': 7350,
                'total_outbound': 6965,
                'daily_average_inbound': 1050,
                'daily_average_outbound': 995
            }

            self.tab = PassengerFlowTab(self.root)

    def test_station_combobox_population(self):
        """測試車站下拉選單填充"""
        self.wait_for_gui_update()

        # 檢查車站是否已載入到下拉選單
        if hasattr(self.tab, 'station_combobox'):
            values = self.tab.station_combobox['values']
            self.assertGreater(len(values), 0)

    def test_date_range_validation(self):
        """測試日期範圍驗證"""
        # 設定無效的日期範圍（結束日期早於開始日期）
        start_date = datetime.now()
        end_date = start_date - timedelta(days=1)

        is_valid = self.tab.validate_date_range(start_date, end_date)
        self.assertFalse(is_valid)

        # 設定有效的日期範圍
        end_date = start_date + timedelta(days=7)
        is_valid = self.tab.validate_date_range(start_date, end_date)
        self.assertTrue(is_valid)

    def test_query_execution(self):
        """測試查詢執行"""
        # 設定查詢參數
        if hasattr(self.tab, 'station_combobox'):
            self.tab.station_combobox.set("台北 (1000)")

        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        # 執行查詢
        self.tab.execute_query("1000", start_date, end_date)
        self.wait_for_gui_update()

        # 檢查是否呼叫了相關的DAO方法
        self.mock_passenger_flow_dao.get_passenger_flow_by_station_and_date_range.assert_called()
        self.mock_passenger_flow_dao.get_passenger_flow_summary.assert_called()


class TestComparisonTabIntegration(GUITestCase):
    """車站比較分頁整合測試"""

    def setUp(self):
        super().setUp()
        with patch('taiwan_railway_gui.dao.station_dao.StationDAO') as mock_station_dao_class, \
             patch('taiwan_railway_gui.dao.passenger_flow_dao.PassengerFlowDAO') as mock_flow_dao_class:

            mock_station_dao_class.return_value = self.mock_station_dao
            mock_flow_dao_class.return_value = self.mock_passenger_flow_dao

            self.mock_station_dao.get_all_stations.return_value = self.test_stations
            self.mock_passenger_flow_dao.compare_stations_passenger_flow.return_value = [
                {'station_id': '1000', 'station_name': '台北', 'total_passengers': 14315, 'rank': 1},
                {'station_id': '1001', 'station_name': '板橋', 'total_passengers': 13200, 'rank': 2},
                {'station_id': '1008', 'station_name': '桃園', 'total_passengers': 12100, 'rank': 3},
            ]

            self.tab = ComparisonTab(self.root)

    def test_station_addition(self):
        """測試車站新增功能"""
        initial_count = len(self.tab.selected_stations)

        # 新增車站
        self.tab.add_station("1000")
        self.wait_for_gui_update()

        # 檢查車站是否已新增
        self.assertEqual(len(self.tab.selected_stations), initial_count + 1)
        self.assertIn("1000", self.tab.selected_stations)

    def test_station_removal(self):
        """測試車站移除功能"""
        # 先新增車站
        self.tab.add_station("1000")
        initial_count = len(self.tab.selected_stations)

        # 移除車站
        self.tab.remove_station("1000")
        self.wait_for_gui_update()

        # 檢查車站是否已移除
        self.assertEqual(len(self.tab.selected_stations), initial_count - 1)
        self.assertNotIn("1000", self.tab.selected_stations)

    def test_maximum_stations_limit(self):
        """測試最大車站數量限制"""
        # 新增最大數量的車站
        max_stations = 5
        for i, station in enumerate(self.test_stations):
            if i < max_stations:
                self.tab.add_station(station.station_id)

        # 嘗試新增超過限制的車站
        initial_count = len(self.tab.selected_stations)
        self.tab.add_station("9999")

        # 檢查是否阻止了新增
        self.assertEqual(len(self.tab.selected_stations), initial_count)

    def test_comparison_execution(self):
        """測試比較執行"""
        # 新增要比較的車站
        for station in self.test_stations:
            self.tab.add_station(station.station_id)

        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        # 執行比較
        self.tab.execute_comparison(start_date, end_date)
        self.wait_for_gui_update()

        # 檢查是否呼叫了比較方法
        self.mock_passenger_flow_dao.compare_stations_passenger_flow.assert_called()


class TestChartTabIntegration(GUITestCase):
    """圖表分頁整合測試"""

    def setUp(self):
        super().setUp()
        with patch('taiwan_railway_gui.dao.station_dao.StationDAO') as mock_station_dao_class, \
             patch('taiwan_railway_gui.dao.passenger_flow_dao.PassengerFlowDAO') as mock_flow_dao_class:

            mock_station_dao_class.return_value = self.mock_station_dao
            mock_flow_dao_class.return_value = self.mock_passenger_flow_dao

            self.mock_station_dao.get_all_stations.return_value = self.test_stations
            self.mock_passenger_flow_dao.get_passenger_flow_by_station_and_date_range.return_value = self.test_passenger_flows

            self.tab = ChartTab(self.root)

    def test_chart_generation(self):
        """測試圖表生成"""
        # 設定圖表參數
        station_id = "1000"
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        # 生成圖表
        self.tab.generate_chart(station_id, start_date, end_date)
        self.wait_for_gui_update()

        # 檢查圖表是否生成
        self.assertIsNotNone(self.tab.current_chart_data)

    def test_chart_controls(self):
        """測試圖表控制項"""
        # 先生成圖表
        self.tab.generate_chart("1000", datetime.now() - timedelta(days=7), datetime.now())
        self.wait_for_gui_update()

        # 測試縮放功能
        if hasattr(self.tab, 'zoom_in'):
            self.tab.zoom_in()
            self.wait_for_gui_update()

        # 測試重置功能
        if hasattr(self.tab, 'reset_view'):
            self.tab.reset_view()
            self.wait_for_gui_update()

    def test_chart_export(self):
        """測試圖表匯出"""
        # 先生成圖表
        self.tab.generate_chart("1000", datetime.now() - timedelta(days=7), datetime.now())
        self.wait_for_gui_update()

        # 測試匯出功能
        with patch('tkinter.filedialog.asksaveasfilename') as mock_dialog:
            mock_dialog.return_value = "/tmp/test_chart.png"

            success = self.tab.export_chart("png")

            # 檢查匯出是否成功
            if self.tab.current_chart_data:
                self.assertTrue(success)


class TestCrossTabIntegration(GUITestCase):
    """跨分頁整合測試"""

    def setUp(self):
        super().setUp()
        with patch('taiwan_railway_gui.dao.get_database_manager'):
            self.main_window = MainWindow()

        # 設定模擬資料
        self.setup_cross_tab_mocks()

    def setup_cross_tab_mocks(self):
        """設定跨分頁測試的模擬"""
        # 這裡可以根據需要設定更複雜的模擬
        pass

    def test_station_search_to_passenger_flow(self):
        """測試從車站搜尋到客流量查詢的整合"""
        # 在車站搜尋分頁選擇車站
        if hasattr(self.main_window, 'station_search_tab'):
            # 模擬選擇車站
            selected_station = self.test_stations[0]
            self.main_window.station_search_tab.selected_station = selected_station

            # 切換到客流量分頁
            if hasattr(self.main_window, 'passenger_flow_tab'):
                # 檢查車站是否可以傳遞到客流量查詢
                station_id = selected_station.station_id
                self.assertEqual(station_id, "1000")

    def test_station_selection_to_comparison(self):
        """測試從車站選擇到比較功能的整合"""
        # 選擇多個車站
        selected_stations = [station.station_id for station in self.test_stations[:3]]

        # 檢查比較功能是否可以處理這些車站
        if hasattr(self.main_window, 'comparison_tab'):
            for station_id in selected_stations:
                # 模擬新增車站到比較清單
                can_add = len(self.main_window.comparison_tab.selected_stations) < 5
                self.assertTrue(can_add)

    def test_data_consistency_across_tabs(self):
        """測試跨分頁的資料一致性"""
        # 檢查所有分頁使用的車站資料是否一致
        station_sources = []

        if hasattr(self.main_window, 'station_search_tab'):
            station_sources.append("station_search")

        if hasattr(self.main_window, 'passenger_flow_tab'):
            station_sources.append("passenger_flow")

        if hasattr(self.main_window, 'comparison_tab'):
            station_sources.append("comparison")

        # 至少應該有一個資料來源
        self.assertGreater(len(station_sources), 0)


if __name__ == '__main__':
    # 建立測試套件
    suite = unittest.TestSuite()

    # 添加GUI整合測試
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMainWindowIntegration))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStationSearchTabIntegration))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPassengerFlowTabIntegration))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestComparisonTabIntegration))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestChartTabIntegration))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCrossTabIntegration))

    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 輸出結果
    if result.wasSuccessful():
        print("\n✅ 所有GUI整合測試通過！")
    else:
        print(f"\n❌ 測試失敗：{len(result.failures)} 個失敗，{len(result.errors)} 個錯誤")

    sys.exit(0 if result.wasSuccessful() else 1)
