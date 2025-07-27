"""
車站搜尋功能單元測試

測試車站搜尋分頁的各種功能。
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from taiwan_railway_gui.gui.station_search_tab import StationSearchTab
from taiwan_railway_gui.models.station import Station


class TestStationSearchTab(unittest.TestCase):
    """測試車站搜尋分頁"""

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
            )
        ]

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    @patch('taiwan_railway_gui.gui.station_search_tab.create_station_dao')
    def test_station_search_tab_creation(self, mock_create_dao):
        """測試車站搜尋分頁建立"""
        # 模擬 DAO
        mock_dao = Mock()
        mock_dao.get_all_stations.return_value = self.test_stations[:1]  # 限制返回數量
        mock_create_dao.return_value = mock_dao

        # 建立分頁
        tab = StationSearchTab(self.root)

        # 檢查基本屬性
        self.assertIsNotNone(tab.station_dao)
        self.assertIsNotNone(tab.search_entry)
        self.assertIsNotNone(tab.results_listbox)
        self.assertIsNotNone(tab.search_button)
        self.assertIsNotNone(tab.clear_button)

        # 檢查初始載入
        mock_dao.get_all_stations.assert_called_once()

    @patch('taiwan_railway_gui.gui.station_search_tab.create_station_dao')
    def test_search_functionality(self, mock_create_dao):
        """測試搜尋功能"""
        # 模擬 DAO
        mock_dao = Mock()
        mock_dao.get_all_stations.return_value = []
        mock_dao.search_stations.return_value = [self.test_stations[0]]
        mock_create_dao.return_value = mock_dao

        # 建立分頁
        tab = StationSearchTab(self.root)

        # 設定搜尋查詢
        tab.search_entry.insert(0, "台北")

        # 執行搜尋
        tab.perform_search()

        # 檢查搜尋被呼叫
        mock_dao.search_stations.assert_called_with("台北")

        # 檢查結果更新
        self.assertEqual(len(tab.search_results), 1)
        self.assertEqual(tab.search_results[0].station_name, "台北車站")

    @patch('taiwan_railway_gui.gui.station_search_tab.create_station_dao')
    def test_station_selection(self, mock_create_dao):
        """測試車站選擇"""
        # 模擬 DAO
        mock_dao = Mock()
        mock_dao.get_all_stations.return_value = []
        mock_create_dao.return_value = mock_dao

        # 建立分頁
        tab = StationSearchTab(self.root)

        # 設定搜尋結果
        tab.search_results = self.test_stations
        tab.update_results_display()

        # 模擬選擇第一個車站
        tab.results_listbox.selection_set(0)
        tab.on_station_selected(None)

        # 檢查選中的車站
        self.assertEqual(tab.selected_station, self.test_stations[0])

        # 檢查詳細資訊顯示
        self.assertEqual(tab.info_vars['station_code'].get(), '1000')
        self.assertEqual(tab.info_vars['station_name'].get(), '台北車站')

        # 檢查按鈕狀態
        self.assertEqual(str(tab.view_flow_button['state']), 'normal')
        self.assertEqual(str(tab.copy_info_button['state']), 'normal')

    @patch('taiwan_railway_gui.gui.station_search_tab.create_station_dao')
    def test_clear_search(self, mock_create_dao):
        """測試清除搜尋"""
        # 模擬 DAO
        mock_dao = Mock()
        mock_dao.get_all_stations.return_value = self.test_stations[:1]
        mock_create_dao.return_value = mock_dao

        # 建立分頁
        tab = StationSearchTab(self.root)

        # 設定搜尋內容
        tab.search_entry.insert(0, "測試搜尋")
        tab.search_results = [self.test_stations[0]]
        tab.selected_station = self.test_stations[0]

        # 清除搜尋
        tab.clear_search()

        # 檢查搜尋框已清空
        self.assertEqual(tab.search_entry.get(), "")

        # 檢查結果已清除
        self.assertEqual(len(tab.search_results), 1)  # 重新載入初始資料

        # 檢查選中車站已清除
        self.assertIsNone(tab.selected_station)

    @patch('taiwan_railway_gui.gui.station_search_tab.create_station_dao')
    def test_copy_station_info(self, mock_create_dao):
        """測試複製車站資訊"""
        # 模擬 DAO
        mock_dao = Mock()
        mock_dao.get_all_stations.return_value = []
        mock_create_dao.return_value = mock_dao

        # 建立分頁
        tab = StationSearchTab(self.root)

        # 設定選中車站
        tab.selected_station = self.test_stations[0]

        # 執行複製
        tab.copy_station_info()

        # 檢查剪貼簿內容（簡單檢查是否包含車站名稱）
        clipboard_content = tab.frame.clipboard_get()
        self.assertIn("台北車站", clipboard_content)
        self.assertIn("1000", clipboard_content)

    @patch('taiwan_railway_gui.gui.station_search_tab.create_station_dao')
    def test_refresh_data(self, mock_create_dao):
        """測試重新整理資料"""
        # 模擬 DAO
        mock_dao = Mock()
        mock_dao.get_all_stations.return_value = self.test_stations
        mock_dao.clear_cache = Mock()
        mock_create_dao.return_value = mock_dao

        # 建立分頁
        tab = StationSearchTab(self.root)

        # 執行重新整理
        tab.refresh_data()

        # 檢查快取被清除
        mock_dao.clear_cache.assert_called_once()

    @patch('taiwan_railway_gui.gui.station_search_tab.create_station_dao')
    def test_update_results_display(self, mock_create_dao):
        """測試結果顯示更新"""
        # 模擬 DAO
        mock_dao = Mock()
        mock_dao.get_all_stations.return_value = []
        mock_create_dao.return_value = mock_dao

        # 建立分頁
        tab = StationSearchTab(self.root)

        # 設定搜尋結果
        tab.search_results = self.test_stations

        # 更新顯示
        tab.update_results_display()

        # 檢查清單框內容
        self.assertEqual(tab.results_listbox.size(), 2)

        # 檢查結果統計
        self.assertEqual(tab.results_count_var.get(), "共 2 個結果")

    @patch('taiwan_railway_gui.gui.station_search_tab.create_station_dao')
    def test_view_passenger_flow(self, mock_create_dao):
        """測試查看客流量功能"""
        # 模擬 DAO
        mock_dao = Mock()
        mock_dao.get_all_stations.return_value = []
        mock_create_dao.return_value = mock_dao

        # 模擬主視窗
        mock_main_window = Mock()

        # 建立分頁
        tab = StationSearchTab(self.root, mock_main_window)

        # 設定選中車站
        tab.selected_station = self.test_stations[0]

        # 執行查看客流量
        tab.view_passenger_flow()

        # 檢查主視窗方法被呼叫
        mock_main_window.switch_to_tab.assert_called_with('passenger_flow')

    @patch('taiwan_railway_gui.gui.station_search_tab.create_station_dao')
    @patch('tkinter.filedialog.asksaveasfilename')
    @patch('builtins.open', create=True)
    def test_export_data(self, mock_open, mock_filedialog, mock_create_dao):
        """測試資料匯出"""
        # 模擬 DAO
        mock_dao = Mock()
        mock_dao.get_all_stations.return_value = []
        mock_create_dao.return_value = mock_dao

        # 模擬檔案對話框
        mock_filedialog.return_value = "test_export.csv"

        # 模擬檔案寫入
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        # 建立分頁
        tab = StationSearchTab(self.root)

        # 設定搜尋結果
        tab.search_results = [self.test_stations[0]]

        # 執行匯出
        tab.export_data()

        # 檢查檔案對話框被呼叫
        mock_filedialog.assert_called_once()

        # 檢查檔案被開啟
        mock_open.assert_called_once_with("test_export.csv", 'w', newline='', encoding='utf-8')


if __name__ == '__main__':
    unittest.main()