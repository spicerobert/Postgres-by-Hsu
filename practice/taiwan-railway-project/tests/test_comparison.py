"""
車站比較功能單元測試

測試車站比較分頁的各種功能。
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
from taiwan_railway_gui.gui.comparison_tab import ComparisonTab, StationSelector
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import StationStatistics, ComparisonResult


class TestStationSelector(unittest.TestCase):
    """測試車站選擇器"""

    def setUp(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏視窗

        # 建立測試車站資料
        self.test_stations = [
            Station(
                station_code='1000',
                station_name='台北車站',
                address='台北市中正區北平西路3號',
                phone='02-2371-3558',
                gps_lat=25.0478,
                gps_lng=121.5170,
                has_bike_rental=True
            ),
            Station(
                station_code='1001',
                station_name='板橋車站',
                address='新北市板橋區縣民大道二段7號',
                phone='02-2960-3001',
                gps_lat=25.0138,
                gps_lng=121.4627,
                has_bike_rental=False
            ),
            Station(
                station_code='1002',
                station_name='桃園車站',
                address='桃園市桃園區中正路1號',
                phone='03-332-8989',
                gps_lat=24.9893,
                gps_lng=121.3133,
                has_bike_rental=True
            )
        ]

        self.station_selector = StationSelector(self.root, self.test_stations, max_selections=5)

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    def test_station_selector_creation(self):
        """測試車站選擇器建立"""
        self.assertIsNotNone(self.station_selector.frame)
        self.assertIsNotNone(self.station_selector.station_listbox)
        self.assertIsNotNone(self.station_selector.selected_listbox)
        self.assertIsNotNone(self.station_selector.add_button)
        self.assertIsNotNone(self.station_selector.remove_button)

        # 檢查車站清單載入
        self.assertEqual(self.station_selector.station_listbox.size(), 3)

    def test_add_station(self):
        """測試加入車站"""
        # 選擇第一個車站
        self.station_selector.station_listbox.selection_set(0)
        self.station_selector.add_station()

        # 檢查車站已加入
        selected = self.station_selector.get_selected_stations()
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].station_code, '1000')

        # 檢查顯示更新
        self.assertEqual(self.station_selector.selected_listbox.size(), 1)
        self.assertEqual(self.station_selector.status_var.get(), "已選 1/5 個車站")

    def test_remove_station(self):
        """測試移除車站"""
        # 先加入一個車站
        self.station_selector.station_listbox.selection_set(0)
        self.station_selector.add_station()

        # 移除車站
        self.station_selector.selected_listbox.selection_set(0)
        self.station_selector.remove_station()

        # 檢查車站已移除
        selected = self.station_selector.get_selected_stations()
        self.assertEqual(len(selected), 0)
        self.assertEqual(self.station_selector.selected_listbox.size(), 0)
        self.assertEqual(self.station_selector.status_var.get(), "已選 0/5 個車站")

    def test_max_selection_limit(self):
        """測試最大選擇數量限制"""
        # 設定較小的限制進行測試
        selector = StationSelector(self.root, self.test_stations, max_selections=2)

        # 加入兩個車站
        selector.station_listbox.selection_set(0)
        selector.add_station()
        selector.station_listbox.selection_set(1)
        selector.add_station()

        # 檢查已達限制
        self.assertEqual(len(selector.get_selected_stations()), 2)
        self.assertEqual(str(selector.add_button['state']), 'disabled')

        # 嘗試加入第三個車站（應該被阻止）
        selector.station_listbox.selection_set(2)
        selector.add_station()
        self.assertEqual(len(selector.get_selected_stations()), 2)  # 仍然是2個

    def test_duplicate_selection_prevention(self):
        """測試防止重複選擇"""
        # 加入同一個車站兩次
        self.station_selector.station_listbox.selection_set(0)
        self.station_selector.add_station()
f.station_selector.station_listbox.selection_set(0)
        self.station_selector.add_station()

        # 檢查只有一個車站被加入
        selected = self.station_selector.get_selected_stations()
        self.assertEqual(len(selected), 1)

    def test_clear_selection(self):
        """測試清除選擇"""
        # 加入幾個車站
        for i in range(2):
            self.station_selector.station_listbox.selection_set(i)
            self.station_selector.add_station()

        # 清除選擇
        self.station_selector.clear_selection()

        # 檢查已清除
        self.assertEqual(len(self.station_selector.get_selected_stations()), 0)
        self.assertEqual(self.station_selector.selected_listbox.size(), 0)
        self.assertEqual(self.station_selector.status_var.get(), "已選 0/5 個車站")


class TestComparisonTab(unittest.TestCase):
    """測試車站比較分頁"""

    def setUp(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏視窗

        # 建立測試資料
        self.test_stations = [
            Station(
                station_code='1000',
                station_name='台北車站',
                address='台北市中正區北平西路3號',
                phone='02-2371-3558',
                gps_lat=25.0478,
                gps_lng=121.5170,
                has_bike_rental=True
            ),
            Station(
                station_code='1001',
                station_name='板橋車站',
                address='新北市板橋區縣民大道二段7號',
                phone='02-2960-3001',
                gps_lat=25.0138,
                gps_lng=121.4627,
                has_bike_rental=False
            ),
            Station(
                station_code='1002',
                station_name='桃園車站',
                address='桃園市桃園區中正路1號',
                phone='03-332-8989',
                gps_lat=24.9893,
                gps_lng=121.3133,
                has_bike_rental=True
            )
        ]

        self.test_statistics = [
            StationStatistics(
                station_code='1000',
                station_name='台北車站',
                total_in=100000,
                total_out=95000,
                total_passengers=195000,
                average_daily=6500.0,
                date_range=(date(2024, 1, 1), date(2024, 1, 30))
            ),
            StationStatistics(
                station_code='1001',
                station_name='板橋車站',
                total_in=80000,
                total_out=78000,
                total_passengers=158000,
                average_daily=5266.67,
                date_range=(date(2024, 1, 1), date(2024, 1, 30))
            ),
            StationStatistics(
                station_code='1002',
                station_name='桃園車站',
                total_in=60000,
                total_out=58000,
                total_passengers=118000,
                average_daily=3933.33,
                date_range=(date(2024, 1, 1), date(2024, 1, 30))
            )
        ]

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    @patch('taiwan_railway_gui.gui.comparison_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.comparison_tab.create_passenger_flow_dao')
    def test_comparison_tab_creation(self, mock_create_flow_dao, mock_create_station_dao):
        """測試車站比較分頁建立"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = self.test_stations
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = ComparisonTab(self.root)

        # 檢查基本屬性
        self.assertIsNotNone(tab.station_dao)
        self.assertIsNotNone(tab.passenger_flow_dao)
        self.assertIsNotNone(tab.start_date_picker)
        self.assertIsNotNone(tab.end_date_picker)
        self.assertIsNotNone(tab.compare_button)
        self.assertIsNotNone(tab.results_tree)

        # 檢查車站載入
        mock_station_dao.get_all_stations.assert_called_once()

    @patch('taiwan_railway_gui.gui.comparison_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.comparison_tab.create_passenger_flow_dao')
    def test_perform_comparison(self, mock_create_flow_dao, mock_create_station_dao):
        """測試執行比較"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = self.test_stations
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_flow_dao.get_multiple_station_statistics.return_value = self.test_statistics
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = ComparisonTab(self.root)

        # 等待車站選擇器建立
        tab.root.update()

        # 模擬選擇車站
        if tab.station_selector:
            # 手動設定選中的車站
            tab.station_selector.selected_stations = self.test_stations[:2]
            tab.station_selector.update_selected_display()

        # 設定日期範圍
        tab.start_date_picker.set_date(date(2024, 1, 1))
        tab.end_date_picker.set_date(date(2024, 1, 30))

        # 執行比較
        tab.perform_comparison()

        # 檢查 DAO 方法被呼叫
        expected_codes = ['1000', '1001']
        mock_flow_dao.get_multiple_station_statistics.assert_called_with(
            expected_codes, date(2024, 1, 1), date(2024, 1, 30)
        )

    @patch('taiwan_railway_gui.gui.comparison_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.comparison_tab.create_passenger_flow_dao')
    def test_update_results_display(self, mock_create_flow_dao, mock_create_station_dao):
        """測試更新結果顯示"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = ComparisonTab(self.root)

        # 設定測試比較結果
        tab.comparison_result = ComparisonResult(self.test_statistics, [])

        # 更新顯示
        tab.update_results_display()

        # 檢查結果樹狀檢視
        children = tab.results_tree.get_children()
        self.assertEqual(len(children), 3)

        # 檢查排名資訊
        ranking_info = tab.ranking_info_var.get()
        self.assertIn("台北車站", ranking_info)  # 應該是排名第一
        self.assertIn("195,000", ranking_info)

    @patch('taiwan_railway_gui.gui.comparison_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.comparison_tab.create_passenger_flow_dao')
    def test_sort_results(self, mock_create_flow_dao, mock_create_station_dao):
        """測試結果排序"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = ComparisonTab(self.root)

        # 設定測試比較結果
        tab.comparison_result = ComparisonResult(self.test_statistics.copy(), [])

        # 按車站名稱排序
        tab.sort_results('station_name')

        # 檢查排序結果（按字母順序）
        station_names = [s.station_name for s in tab.comparison_result.stations]
        expected_order = ['台北車站', '板橋車站', '桃園車站']
        self.assertEqual(station_names, expected_order)

    @patch('taiwan_railway_gui.gui.comparison_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.comparison_tab.create_passenger_flow_dao')
    def test_clear_results(self, mock_create_flow_dao, mock_create_station_dao):
        """測試清除結果"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = ComparisonTab(self.root)

        # 設定測試資料
        tab.comparison_result = ComparisonResult(self.test_statistics, [])
        tab.export_button.config(state=tk.NORMAL)

        # 清除結果
        tab.clear_results()

        # 檢查結果已清除
        self.assertIsNone(tab.comparison_result)
        self.assertEqual(tab.ranking_info_var.get(), "")
        self.assertEqual(str(tab.export_button['state']), 'disabled')

    @patch('taiwan_railway_gui.gui.comparison_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.comparison_tab.create_passenger_flow_dao')
    @patch('tkinter.filedialog.asksaveasfilename')
    @patch('builtins.open', create=True)
    def test_export_data(self, mock_open, mock_filedialog, mock_create_flow_dao, mock_create_station_dao):
        """測試資料匯出"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 模擬檔案對話框
        mock_filedialog.return_value = "test_comparison.csv"

        # 模擬檔案寫入
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        # 建立分頁
        tab = ComparisonTab(self.root)

        # 設定測試資料
        tab.comparison_result = ComparisonResult(self.test_statistics, [])
        tab.start_date_picker.set_date(date(2024, 1, 1))
        tab.end_date_picker.set_date(date(2024, 1, 30))

        # 執行匯出
        tab.export_data()

        # 檢查檔案對話框被呼叫
        mock_filedialog.assert_called_once()

        # 檢查檔案被開啟
        mock_open.assert_called_once_with("test_comparison.csv", 'w', newline='', encoding='utf-8')


if __name__ == '__main__':
    unittest.main()