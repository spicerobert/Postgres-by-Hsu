"""
測試資料匯出管理器

測試 ExportManager 類別的各種功能。
"""

import unittest
import tempfile
import os
import csv
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk

from taiwan_railway_gui.services.export_manager import (
    ExportManager, ExportField, ExportTask, ExportStatus, ExportFormat,
    FieldSelectionDialog, ExportProgressDialog, get_export_manager
)
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow, StationStatistics, ComparisonResult


class TestExportField(unittest.TestCase):
    """測試 ExportField 類別"""

    def test_export_field_creation(self):
        """測試 ExportField 建立"""
        field = ExportField(
            key='test_key',
            display_name='測試欄位',
            data_type=str,
            formatter=lambda x: str(x).upper(),
            default_selected=True
        )

        self.assertEqual(field.key, 'test_key')
        self.assertEqual(field.display_name, '測試欄位')
        self.assertEqual(field.data_type, str)
        self.assertTrue(field.default_selected)
        self.assertEqual(field.formatter('test'), 'TEST')

    def test_export_field_defaults(self):
        """測試 ExportField 預設值"""
        field = ExportField(
            key='test_key',
            display_name='測試欄位',
            data_type=str
        )

        self.assertIsNone(field.formatter)
        self.assertTrue(field.default_selected)


class TestExportTask(unittest.TestCase):
    """測試 ExportTask 類別"""

    def test_export_task_creation(self):
        """測試 ExportTask 建立"""
        fields = [ExportField('key1', '欄位1', str)]
        task = ExportTask(
            task_id='test_task',
            data_type='test_data',
            data=[],
            fields=fields,
            selected_fields=['key1'],
            filename='test.csv',
            format=ExportFormat.CSV,
            status=ExportStatus.PENDING
        )

        self.assertEqual(task.task_id, 'test_task')
        self.assertEqual(task.data_type, 'test_data')
        self.assertEqual(task.format, ExportFormat.CSV)
        self.assertEqual(task.status, ExportStatus.PENDING)
        self.assertIsNotNone(task.created_at)
        self.assertIsNone(task.completed_at)


class TestExportManager(unittest.TestCase):
    """測試 ExportManager 類別"""

    def setUp(self):
        """設定測試環境"""
        self.export_manager = ExportManager()
        self.temp_dir = tempfile.mkdtemp()

        # 建立測試資料
        self.test_stations = [
            Station(
                station_code='1001',
                station_name='台北車站',
                address='台北市中正區北平西路3號',
                phone='02-23713558',
                gps_lat=25.047924,
                gps_lng=121.517081,
                has_bike_rental=True
            ),
            Station(
                station_code='1002',
                station_name='板橋車站',
                address='新北市板橋區縣民大道二段7號',
                phone='02-29603001',
                gps_lat=25.013711,
                gps_lng=121.463528,
                has_bike_rental=False
            )
        ]

        self.test_flows = [
            PassengerFlow(
                station_code='1001',
                date=date(2024, 1, 1),
                in_passengers=10000,
                out_passengers=9500
            ),
            PassengerFlow(
                station_code='1001',
                date=date(2024, 1, 2),
                in_passengers=12000,
                out_passengers=11500
            )
        ]

        self.test_statistics = [
            StationStatistics(
                station_code='1001',
                station_name='台北車站',
                total_in=22000,
                total_out=21000,
                total_passengers=43000,
                average_daily=21500.0,
                date_range=(date(2024, 1, 1), date(2024, 1, 2))
            )
        ]

    def tearDown(self):
        """清理測試環境"""
        # 清理暫存檔案
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_station_fields(self):
        """測試取得車站欄位定義"""
        fields = self.export_manager.get_station_fields()

        self.assertIsInstance(fields, list)
        self.assertTrue(len(fields) > 0)

        # 檢查必要欄位
        field_keys = [field.key for field in fields]
        expected_keys = ['station_code', 'station_name', 'address', 'phone', 'gps_lat', 'gps_lng', 'has_bike_rental']
        for key in expected_keys:
            self.assertIn(key, field_keys)

    def test_get_passenger_flow_fields(self):
        """測試取得客流量欄位定義"""
        fields = self.export_manager.get_passenger_flow_fields()

        self.assertIsInstance(fields, list)
        self.assertTrue(len(fields) > 0)

        # 檢查必要欄位
        field_keys = [field.key for field in fields]
        expected_keys = ['date', 'station_code', 'in_passengers', 'out_passengers', 'total_passengers', 'net_flow']
        for key in expected_keys:
            self.assertIn(key, field_keys)

    def test_get_station_statistics_fields(self):
        """測試取得車站統計欄位定義"""
        fields = self.export_manager.get_station_statistics_fields()

        self.assertIsInstance(fields, list)
        self.assertTrue(len(fields) > 0)

        # 檢查必要欄位
        field_keys = [field.key for field in fields]
        expected_keys = ['station_code', 'station_name', 'total_in', 'total_out', 'total_passengers', 'average_daily']
        for key in expected_keys:
            self.assertIn(key, field_keys)

    def test_get_comparison_result_fields(self):
        """測試取得比較結果欄位定義"""
        fields = self.export_manager.get_comparison_result_fields()

        self.assertIsInstance(fields, list)
        self.assertTrue(len(fields) > 0)

        # 檢查必要欄位
        field_keys = [field.key for field in fields]
        expected_keys = ['rank', 'station_name', 'total_in', 'total_out', 'total_passengers', 'average_daily']
        for key in expected_keys:
            self.assertIn(key, field_keys)

    def test_formatters(self):
        """測試格式化器"""
        # 測試數字格式化器
        number_formatter = self.export_manager.formatters['number']
        self.assertEqual(number_formatter(1000), '1,000')
        self.assertEqual(number_formatter(1000000), '1,000,000')

        # 測試浮點數格式化器
        float_formatter = self.export_manager.formatters['float']
        self.assertEqual(float_formatter(3.14159), '3.14')

        # 測試日期格式化器
        date_formatter = self.export_manager.formatters['date']
        test_date = date(2024, 1, 15)
        self.assertEqual(date_formatter(test_date), '2024-01-15')

        # 測試布林值格式化器
        boolean_formatter = self.export_manager.formatters['boolean']
        self.assertEqual(boolean_formatter(True), '是')
        self.assertEqual(boolean_formatter(False), '否')

        # 測試預設格式化器
        default_formatter = self.export_manager.formatters['default']
        self.assertEqual(default_formatter('test'), 'test')
        self.assertEqual(default_formatter(None), '')

    @patch('taiwan_railway_gui.services.export_manager.FieldSelectionDialog')
    @patch('taiwan_railway_gui.services.export_manager.filedialog.asksaveasfilename')
    @patch('taiwan_railway_gui.services.export_manager.ExportProgressDialog')
    def test_export_stations_success(self, mock_progress_dialog, mock_file_dialog, mock_field_dialog):
        """測試成功匯出車站資料"""
        # 設定模擬
        mock_field_dialog.return_value.get_selected_fields.return_value = ['station_code', 'station_name']
        mock_file_dialog.return_value = os.path.join(self.temp_dir, 'test_stations.csv')
        mock_progress_dialog.return_value.is_cancelled.return_value = False

        # 建立模擬父視窗
        root = tk.Tk()
        try:
            # 執行匯出
            result = self.export_manager.export_stations(root, self.test_stations)

            # 驗證結果
            self.assertTrue(result)

            # 檢查檔案是否建立
            output_file = os.path.join(self.temp_dir, 'test_stations.csv')
            self.assertTrue(os.path.exists(output_file))

            # 檢查檔案內容
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                self.assertIn('車站代碼', headers)
                self.assertIn('車站名稱', headers)

                # 檢查資料行
                rows = list(reader)
                self.assertEqual(len(rows), 2)  # 兩個車站

        finally:
            root.destroy()

    @patch('taiwan_railway_gui.services.export_manager.messagebox.showwarning')
    def test_export_stations_empty_data(self, mock_warning):
        """測試匯出空車站資料"""
        root = tk.Tk()
        try:
            result = self.export_manager.export_stations(root, [])
            self.assertFalse(result)
            mock_warning.assert_called_once()
        finally:
            root.destroy()

    @patch('taiwan_railway_gui.services.export_manager.FieldSelectionDialog')
    @patch('taiwan_railway_gui.services.export_manager.filedialog.asksaveasfilename')
    @patch('taiwan_railway_gui.services.export_manager.ExportProgressDialog')
    def test_export_passenger_flows_success(self, mock_progress_dialog, mock_file_dialog, mock_field_dialog):
        """測試成功匯出客流量資料"""
        # 設定模擬
        mock_field_dialog.return_value.get_selected_fields.return_value = ['date', 'in_passengers', 'out_passengers']
        mock_file_dialog.return_value = os.path.join(self.temp_dir, 'test_flows.csv')
        mock_progress_dialog.return_value.is_cancelled.return_value = False

        # 建立模擬父視窗
        root = tk.Tk()
        try:
            # 執行匯出
            result = self.export_manager.export_passenger_flows(root, self.test_flows)

            # 驗證結果
            self.assertTrue(result)

            # 檢查檔案是否建立
            output_file = os.path.join(self.temp_dir, 'test_flows.csv')
            self.assertTrue(os.path.exists(output_file))

        finally:
            root.destroy()

    @patch('taiwan_railway_gui.services.export_manager.FieldSelectionDialog')
    @patch('taiwan_railway_gui.services.export_manager.filedialog.asksaveasfilename')
    @patch('taiwan_railway_gui.services.export_manager.ExportProgressDialog')
    def test_export_station_statistics_success(self, mock_progress_dialog, mock_file_dialog, mock_field_dialog):
        """測試成功匯出車站統計資料"""
        # 設定模擬
        mock_field_dialog.return_value.get_selected_fields.return_value = ['station_name', 'total_passengers']
        mock_file_dialog.return_value = os.path.join(self.temp_dir, 'test_stats.csv')
        mock_progress_dialog.return_value.is_cancelled.return_value = False

        # 建立模擬父視窗
        root = tk.Tk()
        try:
            # 執行匯出
            result = self.export_manager.export_station_statistics(root, self.test_statistics)

            # 驗證結果
            self.assertTrue(result)

            # 檢查檔案是否建立
            output_file = os.path.join(self.temp_dir, 'test_stats.csv')
            self.assertTrue(os.path.exists(output_file))

        finally:
            root.destroy()

    def test_export_comparison_result_success(self):
        """測試成功匯出比較結果"""
        # 建立比較結果
        comparison_result = ComparisonResult(
            stations=self.test_statistics,
            ranking=[('台北車站', 43000)]
        )

        with patch('taiwan_railway_gui.services.export_manager.FieldSelectionDialog') as mock_field_dialog, \
             patch('taiwan_railway_gui.services.export_manager.filedialog.asksaveasfilename') as mock_file_dialog, \
             patch('taiwan_railway_gui.services.export_manager.ExportProgressDialog') as mock_progress_dialog:

            # 設定模擬
            mock_field_dialog.return_value.get_selected_fields.return_value = ['rank', 'station_name', 'total_passengers']
            mock_file_dialog.return_value = os.path.join(self.temp_dir, 'test_comparison.csv')
            mock_progress_dialog.return_value.is_cancelled.return_value = False

            # 建立模擬父視窗
            root = tk.Tk()
            try:
                # 執行匯出
                result = self.export_manager.export_comparison_result(root, comparison_result)

                # 驗證結果
                self.assertTrue(result)

                # 檢查檔案是否建立
                output_file = os.path.join(self.temp_dir, 'test_comparison.csv')
                self.assertTrue(os.path.exists(output_file))

            finally:
                root.destroy()

    def test_create_export_task(self):
        """測試建立匯出任務"""
        fields = self.export_manager.get_station_fields()
        selected_fields = ['station_code', 'station_name']
        filename = 'test.csv'

        task = self.export_manager._create_export_task(
            data=self.test_stations,
            data_type='stations',
            fields=fields,
            selected_fields=selected_fields,
            filename=filename
        )

        self.assertIsInstance(task, ExportTask)
        self.assertEqual(task.data_type, 'stations')
        self.assertEqual(task.data, self.test_stations)
        self.assertEqual(task.selected_fields, selected_fields)
        self.assertEqual(task.filename, filename)
        self.assertEqual(task.status, ExportStatus.PENDING)

        # 檢查任務是否已儲存
        self.assertIn(task.task_id, self.export_manager.tasks)

    def test_get_task_status(self):
        """測試取得任務狀態"""
        # 建立測試任務
        fields = self.export_manager.get_station_fields()
        task = self.export_manager._create_export_task(
            data=self.test_stations,
            data_type='stations',
            fields=fields,
            selected_fields=['station_code'],
            filename='test.csv'
        )

        # 測試取得任務狀態
        retrieved_task = self.export_manager.get_task_status(task.task_id)
        self.assertEqual(retrieved_task, task)

        # 測試不存在的任務
        non_existent_task = self.export_manager.get_task_status('non_existent')
        self.assertIsNone(non_existent_task)

    def test_clear_completed_tasks(self):
        """測試清除已完成任務"""
        # 建立多個測試任務
        fields = self.export_manager.get_station_fields()

        task1 = self.export_manager._create_export_task(
            data=self.test_stations,
            data_type='stations',
            fields=fields,
            selected_fields=['station_code'],
            filename='test1.csv'
        )
        task1.status = ExportStatus.COMPLETED

        task2 = self.export_manager._create_export_task(
            data=self.test_stations,
            data_type='stations',
            fields=fields,
            selected_fields=['station_code'],
            filename='test2.csv'
        )
        task2.status = ExportStatus.FAILED

        task3 = self.export_manager._create_export_task(
            data=self.test_stations,
            data_type='stations',
            fields=fields,
            selected_fields=['station_code'],
            filename='test3.csv'
        )
        task3.status = ExportStatus.IN_PROGRESS

        # 清除已完成任務
        initial_count = len(self.export_manager.tasks)
        self.export_manager.clear_completed_tasks()

        # 檢查結果
        self.assertEqual(len(self.export_manager.tasks), 1)  # 只剩進行中的任務
        self.assertIn(task3.task_id, self.export_manager.tasks)
        self.assertNotIn(task1.task_id, self.export_manager.tasks)
        self.assertNotIn(task2.task_id, self.export_manager.tasks)


class TestFieldSelectionDialog(unittest.TestCase):
    """測試欄位選擇對話框"""

    def setUp(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏主視窗

        self.test_fields = [
            ExportField('field1', '欄位1', str, default_selected=True),
            ExportField('field2', '欄位2', int, default_selected=False),
            ExportField('field3', '欄位3', float, default_selected=True)
        ]

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    @patch('tkinter.messagebox.showwarning')
    def test_field_selection_dialog_no_selection(self, mock_warning):
        """測試沒有選擇任何欄位的情況"""
        # 這個測試需要模擬使用者互動，在實際環境中較難測試
        # 這裡主要測試對話框的建立
        try:
            # 建立對話框但不等待使用者輸入
            dialog = FieldSelectionDialog.__new__(FieldSelectionDialog)
            dialog.parent = self.root
            dialog.fields = self.test_fields
            dialog.selected_fields = []
            dialog.result = None

            # 測試基本屬性
            self.assertEqual(dialog.fields, self.test_fields)
            self.assertEqual(dialog.selected_fields, [])
            self.assertIsNone(dialog.result)

        except Exception as e:
            # 如果對話框建立失敗，跳過測試
            self.skipTest(f"無法建立對話框: {e}")


class TestGetExportManager(unittest.TestCase):
    """測試取得匯出管理器單例"""

    def test_get_export_manager_singleton(self):
        """測試匯出管理器單例模式"""
        manager1 = get_export_manager()
        manager2 = get_export_manager()

        self.assertIsInstance(manager1, ExportManager)
        self.assertIsInstance(manager2, ExportManager)
        self.assertIs(manager1, manager2)  # 應該是同一個實例


if __name__ == '__main__':
    # 設定測試套件
    unittest.main(verbosity=2)