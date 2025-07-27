"""
客流量查詢功能單元測試

測試客流量查詢分頁的各種功能。
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
from taiwan_railway_gui.gui.passenger_flow_tab import PassengerFlowTab, DatePicker
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow, StationStatistics


class TestDatePicker(unittest.TestCase):
    """測試日期選擇器"""

    def setUp(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏視窗
        self.date_picker = DatePicker(self.root, "測試日期:", date(2024, 1, 15))

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    def test_date_picker_creation(self):
        """測試日期選擇器建立"""
        self.assertIsNotNone(self.date_picker.frame)
        self.assertIsNotNone(self.date_picker.date_entry)
        self.assertIsNotNone(self.date_picker.date_button)
        self.assertEqual(self.date_picker.get_date(), date(2024, 1, 15))

    def test_set_and_get_date(self):
        """測試設定和取得日期"""
        new_date = date(2024, 2, 20)
        self.date_picker.set_date(new_date)
        self.assertEqual(self.date_picker.get_date(), new_date)
        self.assertEqual(self.date_picker.date_var.get(), "2024-02-20")

    def test_validate_date(self):
        """測試日期驗證"""
        # 有效日期
        self.date_picker.date_var.set("2024-03-15")
        self.assertTrue(self.date_picker.validate_date())
        self.assertEqual(self.date_picker.get_date(), date(2024, 3, 15))

        # 無效日期
        original_date = self.date_picker.get_date()
        self.date_picker.date_var.set("invalid-date")
        self.assertFalse(self.date_picker.validate_date())
        self.assertEqual(self.date_picker.get_date(), original_date)


class TestPassengerFlowTab(unittest.TestCase):
    """測試客流量查詢分頁"""

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
            )
        ]

        self.test_flows = [
            PassengerFlow('1000', date(2024, 1, 1), 5000, 4800),
            PassengerFlow('1000', date(2024, 1, 2), 5200, 4900),
            PassengerFlow('1000', date(2024, 1, 3), 4800, 4600)
        ]

        self.test_statistics = StationStatistics(
            station_code='1000',
            station_name='台北車站',
            total_in=15000,
            total_out=14300,
            total_passengers=29300,
            average_daily=9766.67,
            date_range=(date(2024, 1, 1), date(2024, 1, 3))
        )

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_passenger_flow_dao')
    def test_passenger_flow_tab_creation(self, mock_create_flow_dao, mock_create_station_dao):
        """測試客流量查詢分頁建立"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = self.test_stations
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = PassengerFlowTab(self.root)

        # 檢查基本屬性
        self.assertIsNotNone(tab.station_dao)
        self.assertIsNotNone(tab.passenger_flow_dao)
        self.assertIsNotNone(tab.station_combobox)
        self.assertIsNotNone(tab.start_date_picker)
        self.assertIsNotNone(tab.end_date_picker)
        self.assertIsNotNone(tab.query_button)
        self.assertIsNotNone(tab.results_tree)

        # 檢查車站載入
        mock_station_dao.get_all_stations.assert_called_once()

    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_passenger_flow_dao')
    def test_load_stations(self, mock_create_flow_dao, mock_create_station_dao):
        """測試載入車站清單"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = self.test_stations
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = PassengerFlowTab(self.root)

        # 檢查下拉選單內容
        values = tab.station_combobox['values']
        self.assertEqual(len(values), 2)
        self.assertIn('台北車站 (1000)', values)
        self.assertIn('板橋車站 (1001)', values)

    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_passenger_flow_dao')
    def test_get_selected_station_code(self, mock_create_flow_dao, mock_create_station_dao):
        """測試取得選中車站代碼"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁 = PassengerFlowTab(self.root)

        # 測試選擇車站
        tab.station_combobox.set("台北車站 (1000)")
        self.assertEqual(tab.get_selected_station_code(), "1000")

        # 測試空選擇
        tab.station_combobox.set("")
        self.assertIsNone(tab.get_selected_station_code())

    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_passenger_flow_dao')
    def test_set_selected_station(self, mock_create_flow_dao, mock_create_station_dao):
        """測試設定選中車站"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = self.test_stations
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = PassengerFlowTab(self.root)

        # 設定選中車站
        tab.set_selected_station("1001")
        self.assertEqual(tab.station_combobox.get(), "板橋車站 (1001)")

    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_passenger_flow_dao')
    def test_perform_query(self, mock_create_flow_dao, mock_create_station_dao):
        """測試執行查詢"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = self.test_stations
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_flow_dao.get_passenger_flow.return_value = self.test_flows
        mock_flow_dao.get_station_statistics.return_value = self.test_statistics
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = PassengerFlowTab(self.root)

        # 設定查詢參數
        tab.station_combobox.set("台北車站 (1000)")
        tab.start_date_picker.set_date(date(2024, 1, 1))
        tab.end_date_picker.set_date(date(2024, 1, 3))

        # 執行查詢
        tab.perform_query()

        # 檢查 DAO 方法被呼叫
        mock_flow_dao.get_passenger_flow.assert_called_with(
            '1000', date(2024, 1, 1), date(2024, 1, 3)
        )
        mock_flow_dao.get_station_statistics.assert_called_with(
            '1000', date(2024, 1, 1), date(2024, 1, 3)
        )

    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_passenger_flow_dao')
    def test_update_results_display(self, mock_create_flow_dao, mock_create_station_dao):
        """測試更新結果顯示"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = PassengerFlowTab(self.root)

        # 設定測試資料
        tab.current_flows = self.test_flows

        # 更新顯示
        tab.update_results_display()

        # 檢查結果樹狀檢視
        children = tab.results_tree.get_children()
        self.assertEqual(len(children), 3)

        # 檢查結果統計
        self.assertEqual(tab.results_count_var.get(), "共 3 筆記錄")

    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_passenger_flow_dao')
    def test_update_statistics_display(self, mock_create_flow_dao, mock_create_station_dao):
        """測試更新統計顯示"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = PassengerFlowTab(self.root)

        # 設定測試統計資料
        tab.current_statistics = self.test_statistics

        # 更新顯示
        tab.update_statistics_display()

        # 檢查統計標籤
        self.assertEqual(tab.stats_vars['total_in'].get(), "15,000")
        self.assertEqual(tab.stats_vars['total_out'].get(), "14,300")
        self.assertEqual(tab.stats_vars['total_passengers'].get(), "29,300")
        self.assertEqual(tab.stats_vars['average_daily'].get(), "9,766.7")

    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_passenger_flow_dao')
    def test_sort_results(self, mock_create_flow_dao, mock_create_station_dao):
        """測試結果排序"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = PassengerFlowTab(self.root)

        # 設定測試資料
        tab.current_flows = self.test_flows.copy()

        # 按進站人數排序
        tab.sort_results('in_passengers')

        # 檢查排序結果（升序）
        self.assertEqual(tab.current_flows[0].in_passengers, 4800)
        self.assertEqual(tab.current_flows[1].in_passengers, 5000)
        self.assertEqual(tab.current_flows[2].in_passengers, 5200)

        # 再次排序（降序）
        tab.sort_results('in_passengers')
        self.assertEqual(tab.current_flows[0].in_passengers, 5200)
        self.assertEqual(tab.current_flows[1].in_passengers, 5000)
        self.assertEqual(tab.current_flows[2].in_passengers, 4800)

    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_passenger_flow_dao')
    def test_clear_results(self, mock_create_flow_dao, mock_create_station_dao):
        """測試清除結果"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = PassengerFlowTab(self.root)

        # 設定測試資料
        tab.current_flows = self.test_flows
        tab.current_statistics = self.test_statistics
        tab.export_button.config(state=tk.NORMAL)

        # 清除結果
        tab.clear_results()

        # 檢查結果已清除
        self.assertEqual(len(tab.current_flows), 0)
        self.assertIsNone(tab.current_statistics)
        self.assertEqual(str(tab.export_button['state']), 'disabled')

    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.passenger_flow_tab.create_passenger_flow_dao')
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
        mock_filedialog.return_value = "test_export.csv"

        # 模擬檔案寫入
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        # 建立分頁
        tab = PassengerFlowTab(self.root)

        # 設定測試資料
        tab.current_flows = [self.test_flows[0]]
        tab.current_statistics = self.test_statistics
        tab.station_combobox.set("台北車站 (1000)")

        # 執行匯出
        tab.export_data()

        # 檢查檔案對話框被呼叫
        mock_filedialog.assert_called_once()

        # 檢查檔案被開啟
        mock_open.assert_called_once_with("test_export.csv", 'w', newline='', encoding='utf-8')


if __name__ == '__main__':
    unittest.main()