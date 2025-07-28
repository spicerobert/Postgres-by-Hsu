"""
圖表匯出功能測試

測試圖表匯出的各種格式和選項。
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from datetime import date, timedelta
from taiwan_railway_gui.gui.chart_tab import ChartTab, ChartCanvas, ExportOptionsDialog
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow


class TestExportOptionsDialog(unittest.TestCase):
    """匯出選項對話框測試"""

    def setUp(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏主視窗

        self.test_chart_data = {
            'station_name': '台北車站',
            'title': '台北車站客流量圖表',
            'flows': []
        }

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    def test_export_options_dialog_creation(self):
        """測試匯出選項對話框建立"""
        dialog = ExportOptionsDialog(self.root, self.test_chart_data)

        # 檢查基本屬性
        self.assertEqual(dialog.chart_data, self.test_chart_data)
        self.assertIsNone(dialog.result)
        self.assertIsNone(dialog.dialog)

    def test_export_options_dialog_default_values(self):
        """測試匯出選項對話框預設值"""
        dialog = ExportOptionsDialog(self.root, self.test_chart_data)

        # 建立對話框但不顯示
        dialog.dialog = tk.Toplevel(self.root)
        dialog._create_widgets()

        # 檢查預設值
        self.assertEqual(dialog.format_var.get(), "PNG")
        self.assertEqual(dialog.dpi_var.get(), "300")
        self.assertEqual(dialog.bg_var.get(), "white")
        self.assertFalse(dialog.transparent_var.get())

        dialog.dialog.destroy()


class TestChartExport(unittest.TestCase):
    """圖表匯出功能測試"""

    def setUp(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏主視窗

        # 建立測試資料
        self.test_station = Station(
            station_code="1001",
            station_name="台北",
            address="台北市中正區北平西路3號",
            phone="02-23713558",
            gps_lat=25.047924,
            gps_lng=121.517081,
            has_bike_rental=True
        )

        self.test_flows = [
            PassengerFlow("1001", date.today() - timedelta(days=2), 1000, 950),
            PassengerFlow("1001", date.today() - timedelta(days=1), 1200, 1100),
            PassengerFlow("1001", date.today(), 1100, 1050)
        ]

        # 建立臨時目錄用於測試檔案
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

        # 清理臨時檔案
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_chart_canvas_save_chart(self):
        """測試圖表畫布儲存功能"""
        # 建立圖表畫布
        canvas = ChartCanvas(self.root)

        # 建立測試圖表
        canvas.create_line_chart(self.test_flows, "台北", "測試圖表")

        # 測試 PNG 格式儲存
        png_file = os.path.join(self.temp_dir, "test_chart.png")
        canvas.save_chart(png_file, format='png', dpi=150)

        self.assertTrue(os.path.exists(png_file))
        self.assertGreater(os.path.getsize(png_file), 0)

    def test_chart_canvas_save_chart_formats(self):
        """測試不同格式的圖表儲存"""
        canvas = ChartCanvas(self.root)
        canvas.create_line_chart(self.test_flows, "台北", "測試圖表")

        formats = [
            ('png', {'format': 'png', 'dpi': 300}),
            ('jpg', {'format': 'jpeg', 'dpi': 300}),
            ('svg', {'format': 'svg', 'dpi': 72}),
            ('pdf', {'format': 'pdf', 'dpi': 300})
        ]

        for ext, params in formats:
            with self.subTest(format=ext):
                filename = os.path.join(self.temp_dir, f"test_chart.{ext}")
                canvas.save_chart(filename, **params)

                self.assertTrue(os.path.exists(filename))
                self.assertGreater(os.path.getsize(filename), 0)

    def test_chart_canvas_save_chart_parameters(self):
        """測試不同儲存參數"""
        canvas = ChartCanvas(self.root)
        canvas.create_line_chart(self.test_flows, "台北", "測試圖表")

        # 測試不同 DPI
        for dpi in [72, 150, 300, 600]:
            with self.subTest(dpi=dpi):
                filename = os.path.join(self.temp_dir, f"test_chart_dpi_{dpi}.png")
                canvas.save_chart(filename, format='png', dpi=dpi)

                self.assertTrue(os.path.exists(filename))
                self.assertGreater(os.path.getsize(filename), 0)

    def test_chart_canvas_save_chart_error_handling(self):
        """測試圖表儲存錯誤處理"""
        canvas = ChartCanvas(self.root)
        canvas.create_line_chart(self.test_flows, "台北", "測試圖表")

        # 測試無效路徑
        invalid_path = "/invalid/path/test.png"
        with self.assertRaises(Exception):
            canvas.save_chart(invalid_path)

    @patch('taiwan_railway_gui.gui.chart_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.chart_tab.create_passenger_flow_dao')
    def test_chart_tab_save_chart(self, mock_flow_dao, mock_station_dao):
        """測試圖表分頁儲存功能"""
        # 設定 mock
        mock_station_dao.return_value.get_all_stations.return_value = [self.test_station]
        mock_station_dao.return_value.get_station_by_code.return_value = self.test_station
        mock_flow_dao.return_value.get_passenger_flow.return_value = self.test_flows

        # 建立圖表分頁
        chart_tab = ChartTab(self.root)

        # 模擬生成圖表
        chart_tab.current_flows = self.test_flows
        chart_tab.chart_canvas.create_line_chart(self.test_flows, "台北", "測試圖表")

        # 測試儲存功能
        with patch('tkinter.filedialog.asksaveasfilename') as mock_dialog:
            test_file = os.path.join(self.temp_dir, "test_export.png")
            mock_dialog.return_value = test_file

            chart_tab.save_chart()

            self.assertTrue(os.path.exists(test_file))
            self.assertGreater(os.path.getsize(test_file), 0)

    @patch('taiwan_railway_gui.gui.chart_tab.create_station_dao')
    @patch('taiwan_railway_gui.gui.chart_tab.create_passenger_flow_dao')
    def test_chart_tab_save_chart_no_data(self, mock_flow_dao, mock_station_dao):
        """測試沒有圖表時的儲存功能"""
        # 設定 mock
        mock_station_dao.return_value.get_all_stations.return_value = [self.test_station]

        # 建立圖表分頁
        chart_tab = ChartTab(self.root)

        # 測試沒有圖表時的儲存
        with patch.object(chart_tab, 'show_warning_message') as mock_warning:
            chart_tab.save_chart()
            mock_warning.assert_called_once()

    def test_get_save_parameters(self):
        """測試儲存參數生成"""
        chart_tab = ChartTab(self.root)

        # 測試 PNG 參數
        png_params = chart_tab._get_save_parameters('.png')
        self.assertEqual(png_params['format'], 'png')
        self.assertIn('transparent', png_params)

        # 測試 JPG 參數
        jpg_params = chart_tab._get_save_parameters('.jpg')
        self.assertEqual(jpg_params['format'], 'jpeg')
        self.assertEqual(jpg_params['facecolor'], 'white')
        self.assertIn('quality', jpg_params)

        # 測試 SVG 參數
        svg_params = chart_tab._get_save_parameters('.svg')
        self.assertEqual(svg_params['format'], 'svg')
        self.assertEqual(svg_params['dpi'], 72)
        self.assertTrue(svg_params['transparent'])

        # 測試 PDF 參數
        pdf_params = chart_tab._get_save_parameters('.pdf')
        self.assertEqual(pdf_params['format'], 'pdf')
        self.assertIn('orientation', pdf_params)

    def test_get_format_info(self):
        """測試格式資訊取得"""
        chart_tab = ChartTab(self.root)

        test_cases = [
            ('.png', 'PNG (可攜式網路圖形)'),
            ('.jpg', 'JPEG (聯合圖像專家組)'),
            ('.jpeg', 'JPEG (聯合圖像專家組)'),
            ('.svg', 'SVG (可縮放向量圖形)'),
            ('.pdf', 'PDF (可攜式文件格式)'),
            ('.unknown', '未知格式')
        ]

        for ext, expected in test_cases:
            with self.subTest(extension=ext):
                result = chart_tab._get_format_info(ext)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()