"""
圖表視覺化功能單元測試

測試圖表視覺化分頁的各種功能。
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
from taiwan_railway_gui.gui.chart_tab import ChartTab, ChartCanvas
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow


class TestChartCanvas(unittest.TestCase):
    """測試圖表畫布"""

    def setUp(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏視窗

        # 建立測試資料
        self.test_flows = [
            PassengerFlow('1000', date(2024, 1, 1), 5000, 4800),
            PassengerFlow('1000', date(2024, 1, 2), 5200, 4900),
            PassengerFlow('1000', date(2024, 1, 3), 4800, 4600)
        ]

        self.chart_canvas = ChartCanvas(self.root)

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    def test_chart_canvas_creation(self):
        """測試圖表畫布建立"""
        self.assertIsNotNone(self.chart_canvas.figure)
        self.assertIsNotNone(self.chart_canvas.canvas)
        self.assertIsNotNone(self.chart_canvas.toolbar)
        self.assertIsNone(self.chart_canvas.ax)
        self.assertIsNone(self.chart_canvas.current_data)

    def test_clear_chart(self):
        """測試清除圖表"""
        # 先建立一個圖表
        self.chart_canvas.create_line_chart(self.test_flows, "台北車站")
        self.assertIsNotNone(self.chart_canvas.ax)

        # 清除圖表
        self.chart_canvas.clear_chart()
        self.assertIsNone(self.chart_canvas.ax)

    def test_create_line_chart(self):
        """測試建立線圖"""
        self.chart_canvas.create_line_chart(self.test_flows, "台北車站")

        # 檢查圖表已建立
        self.assertIsNotNone(self.chart_canvas.ax)
        self.assertIsNotNone(self.chart_canvas.current_data)
        self.assertEqual(self.chart_canvas.current_chart_type, 'line')

        # 檢查資料
        self.assertEqual(len(self.chart_canvas.current_data['flows']), 3)
        self.assertEqual(self.chart_canvas.current_data['station_name'], "台北車站")

    def test_create_bar_chart(self):
        """測試建立長條圖"""
        self.chart_canvas.create_bar_chart(self.test_flows, "台北車站")

        # 檢查圖表已建立
        self.assertIsNotNone(self.chart_canvas.ax)
        self.assertIsNotNone(self.chart_canvas.current_data)
        self.assertEqual(self.chart_canvas.current_chart_type, 'bar')

        # 檢查資料
        self.assertEqual(len(self.chart_canvas.current_data['flows']), 3)
        self.assertEqual(self.chart_canvas.current_data['station_name'], "台北車站")

    def test_create_chart_with_no_data(self):
        """測試無資料時建立圖表"""
        self.chart_canvas.create_line_chart([], "台北車站")

        # 應該顯示無資料訊息
        self.assertIsNotNone(self.chart_canvas.ax)

    def test_refresh_chart(self):
        """測試重新整理圖表"""
        # 先建立圖表
        self.chart_canvas.create_line_chart(self.test_flows, "台北車站")
        original_ax = self.chart_canvas.ax

        # 重新整理圖表
        self.chart_canvas.refresh_chart()

        # 圖表應該重新建立
        self.assertIsNotNone(self.chart_canvas.ax)
        self.assertEqual(self.chart_canvas.current_chart_type, 'line')

    @patch('matplotlib.figure.Figure.savefig')
    def test_save_chart(self, mock_savefig):
        """測試儲存圖表"""
        # 先建立圖表
        self.chart_canvas.create_line_chart(self.test_flows, "台北車站")

        # 儲存圖表
        filename = "test_chart.png"
        self.chart_canvas.save_chart(filename)

        # 檢查 savefig 被呼叫
        mock_savefig.assert_called_once_with(
            filename, dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none', pad_inches=0.1
        )


class TestChartTab(unittest.TestCase):
    """測試圖表視覺化分頁"""

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

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    @patch('taiwan_railway_gui.gui.chart_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.chart_tab.create_passenger_flow_dao')
    def test_chart_tab_creation(self, mock_create_flow_dao, mock_create_station_dao):
        """測試圖表視覺化分頁建立"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = self.test_stations
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = ChartTab(self.root)

        # 檢查基本屬性
        self.assertIsNotNone(tab.station_dao)
        self.assertIsNotNone(tab.passenger_flow_dao)
        self.assertIsNotNone(tab.station_combobox)
        self.assertIsNotNone(tab.chart_type_var)
        self.assertIsNotNone(tab.start_date_picker)
        self.assertIsNotNone(tab.end_date_picker)
        self.assertIsNotNone(tab.generate_button)
        self.assertIsNotNone(tab.chart_canvas)

        # 檢查車站載入
        mock_station_dao.get_all_stations.assert_called_once()

    @patch('taiwan_railway_gui.gui.chart_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.chart_tab.create_passenger_flow_dao')
    def test_load_stations(self, mock_create_flow_dao, mock_create_station_dao):
        """測試載入車站清單"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = self.test_stations
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = ChartTab(self.root)

        # 檢查下拉選單內容
        values = tab.station_combobox['values']
        self.assertEqual(len(values), 2)
        self.assertIn('台北車站 (1000)', values)
        self.assertIn('板橋車站 (1001)', values)

    @patch('taiwan_railway_gui.gui.chart_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.chart_tab.create_passenger_flow_dao')
    def test_get_selected_station_code(self, mock_create_flow_dao, mock_create_station_dao):
        """測試取得選中車站代碼"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = ChartTab(self.root)

        # 測試選擇車站
        tab.station_combobox.set("台北車站 (1000)")
        self.assertEqual(tab.get_selected_station_code(), "1000")

        # 測試空選擇
        tab.station_combobox.set("")
        self.assertIsNone(tab.get_selected_station_code())

    @patch('taiwan_railway_gui.gui.chart_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.chart_tab.create_passenger_flow_dao')
    def test_generate_chart(self, mock_create_flow_dao, mock_create_station_dao):
        """測試生成圖表"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = self.test_stations
        mock_station_dao.get_station_by_code.return_value = self.test_stations[0]
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_flow_dao.get_passenger_flow.return_value = self.test_flows
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = ChartTab(self.root)

        # 設定參數
        tab.station_combobox.set("台北車站 (1000)")
        tab.chart_type_var.set("line")
        tab.start_date_picker.set_date(date(2024, 1, 1))
        tab.end_date_picker.set_date(date(2024, 1, 3))

        # 生成圖表
        tab.generate_chart()

        # 檢查 DAO 方法被呼叫
        mock_flow_dao.get_passenger_flow.assert_called_with(
            '1000', date(2024, 1, 1), date(2024, 1, 3)
        )
        mock_station_dao.get_station_by_code.assert_called_with('1000')

    @patch('taiwan_railway_gui.gui.chart_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.chart_tab.create_passenger_flow_dao')
    def test_clear_chart(self, mock_create_flow_dao, mock_create_station_dao):
        """測試清除圖表"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = ChartTab(self.root)

        # 設定測試資料
        tab.current_flows = self.test_flows
        tab.save_button.config(state=tk.NORMAL)

        # 清除圖表
        tab.clear_chart()

        # 檢查結果已清除
        self.assertEqual(len(tab.current_flows), 0)
        self.assertEqual(tab.chart_info_var.get(), "圖表已清除")
        self.assertEqual(str(tab.save_button['state']), 'disabled')

    @patch('taiwan_railway_gui.gui.chart_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.chart_tab.create_passenger_flow_dao')
    def test_refresh_chart(self, mock_create_flow_dao, mock_create_station_dao):
        """測試重新整理圖表"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 建立分頁
        tab = ChartTab(self.root)

        # 模擬有圖表資料
        tab.chart_canvas.current_data = {
            'flows': self.test_flows,
            'station_name': '台北車站',
            'title': None
        }
        tab.chart_canvas.current_chart_type = 'line'

        # 重新整理圖表
        tab.refresh_chart()

        # 檢查圖表已重新整理（這裡主要檢查不會拋出異常）
        self.assertIsNotNone(tab.chart_canvas.current_data)

    @patch('taiwan_railway_gui.gui.chart_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.chart_tab.create_passenger_flow_dao')
    @patch('tkinter.filedialog.asksaveasfilename')
    def test_save_chart(self, mock_filedialog, mock_create_flow_dao, mock_create_station_dao):
        """測試儲存圖表"""
        # 模擬 DAO
        mock_station_dao = Mock()
        mock_station_dao.get_all_stations.return_value = []
        mock_create_station_dao.return_value = mock_station_dao

        mock_flow_dao = Mock()
        mock_create_flow_dao.return_value = mock_flow_dao

        # 模擬檔案對話框
        mock_filedialog.return_value = "test_chart.png"

        # 建立分頁
        tab = ChartTab(self.root)

        # 模擬有圖表資料
        tab.chart_canvas.current_data = {
            'flows': self.test_flows,
            'station_name': '台北車站',
            'title': None
        }
        tab.chart_canvas.current_chart_type = 'line'

        # 模擬 save_chart 方法
        tab.chart_canvas.save_chart = Mock()

        # 儲存圖表
        tab.save_chart()

        # 檢查檔案對話框被呼叫
        mock_filedialog.assert_called_once()

        # 檢查 save_chart 被呼叫
        tab.chart_canvas.save_chart.assert_called_once_with("test_chart.png")


if __name__ == '__main__':
    unittest.main()