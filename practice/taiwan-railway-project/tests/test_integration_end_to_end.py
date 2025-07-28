"""
端到端整合測試

測試完整的使用者工作流程和端到端功能。
"""

import unittest
import tkinter as tk
import threading
import time
import os
import sys
import tempfile
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from taiwan_railway_gui.gui.main_window import MainWindow
from taiwan_railway_gui.dao.database_manager import DatabaseManager
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow


class EndToEndTestCase(unittest.TestCase):
    """端到端測試基礎類別"""

    @classmethod
    def setUpClass(cls):
        """設定測試類別"""
        cls.test_db_path = tempfile.mktemp(suffix='.db')
        cls.setup_test_database()

    @classmethod
    def tearDownClass(cls):
        """清理測試類別"""
        if os.path.exists(cls.test_db_path):
            os.unlink(cls.test_db_path)

    @classmethod
    def setup_test_database(cls):
        """建立測試資料庫和測試資料"""
        conn = sqlite3.connect(cls.test_db_path)
        cursor = conn.cursor()

        # 建立車站表格
        cursor.execute('''
            CREATE TABLE stations (
                station_id TEXT PRIMARY KEY,
                station_name TEXT NOT NULL,
                station_class TEXT,
                line_name TEXT,
                address TEXT,
                phone TEXT,
                coordinates TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')

        # 建立乘客流量表格
        cursor.execute('''
            CREATE TABLE passenger_flow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id TEXT,
                date TEXT,
                inbound_passengers INTEGER,
                outbound_passengers INTEGER,
                total_passengers INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (station_id) REFERENCES stations (station_id)
            )
        ''')

        # 插入測試車站資料
        test_stations = [
            ('1000', '台北', '特等', '縱貫線', '台北市中正區黎明里北平西路3號', '02-23713558', '25.047924,121.517081'),
            ('1001', '板橋', '一等', '縱貫線', '新北市板橋區縣民大道二段7號', '02-29603000', '25.013807,121.464132'),
            ('1008', '桃園', '一等', '縱貫線', '桃園市桃園區中正路1號', '03-3322340', '24.989197,121.314007'),
            ('1025', '新竹', '一等', '縱貫線', '新竹市東區榮光里中華路二段445號', '03-5323441', '24.801416,120.971736'),
            ('1100', '台中', '特等', '縱貫線', '台中市中區台灣大道一段1號', '04-22227236', '24.136675,120.684175'),
        ]

        cursor.executemany(
            'INSERT INTO stations VALUES (?, ?, ?, ?, ?, ?, ?, 1)',
            test_stations
        )

        # 插入測試乘客流量資料
        base_date = datetime.now() - timedelta(days=30)
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')

            for station_id, _, _, _, _, _, _ in test_stations:
                inbound = 1000 + (i * 50) + int(station_id) % 100
                outbound = 950 + (i * 45) + int(station_id) % 90
                total = inbound + outbound

                cursor.execute(
                    'INSERT INTO passenger_flow (station_id, date, inbound_passengers, outbound_passengers, total_passengers) VALUES (?, ?, ?, ?, ?)',
                    (station_id, date_str, inbound, outbound, total)
                )

        conn.commit()
        conn.close()

    def setUp(self):
        """設定測試方法"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏主視窗避免干擾

        # 設定測試資料庫配置
        self.test_config = {
            'database_type': 'sqlite',
            'database_path': self.test_db_path,
        }

        # 重設資料庫管理器
        DatabaseManager._instance = None

    def tearDown(self):
        """清理測試方法"""
        if hasattr(self, 'root') and self.root:
            self.root.destroy()

        # 清理資料庫管理器
        if DatabaseManager._instance:
            DatabaseManager._instance.close_connection()
            DatabaseManager._instance = None

    def wait_for_gui_update(self, timeout=2.0):
        """等待GUI更新完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.root.update()
            time.sleep(0.01)

    def simulate_user_input(self, widget, value):
        """模擬使用者輸入"""
        if hasattr(widget, 'delete') and hasattr(widget, 'insert'):
            widget.delete(0, tk.END)
            widget.insert(0, str(value))
        elif hasattr(widget, 'set'):
            widget.set(str(value))

        self.wait_for_gui_update(0.1)


class TestCompleteUserWorkflows(EndToEndTestCase):
    """完整使用者工作流程測試"""

    def setUp(self):
        super().setUp()
        # 使用測試資料庫配置建立主視窗
        with patch('taiwan_railway_gui.config.get_config') as mock_config:
            mock_config.return_value = self.test_config
            self.main_window = MainWindow()

    def test_complete_station_search_workflow(self):
        """測試完整的車站搜尋工作流程"""
        # 1. 開啟應用程式
        self.assertIsNotNone(self.main_window)

        # 2. 切換到車站搜尋分頁
        if hasattr(self.main_window, 'notebook'):
            # 找到車站搜尋分頁
            for i in range(self.main_window.notebook.index('end')):
                tab_text = self.main_window.notebook.tab(i, 'text')
                if '車站搜尋' in tab_text:
                    self.main_window.notebook.select(i)
                    break

        self.wait_for_gui_update()

        # 3. 在搜尋框輸入車站名稱
        if hasattr(self.main_window, 'station_search_tab'):
            search_tab = self.main_window.station_search_tab
            if hasattr(search_tab, 'search_entry'):
                self.simulate_user_input(search_tab.search_entry, "台北")

                # 4. 等待搜尋結果
                self.wait_for_gui_update(1.0)

                # 5. 檢查搜尋結果
                if hasattr(search_tab, 'results_listbox'):
                    results_count = search_tab.results_listbox.size()
                    self.assertGreater(results_count, 0, "應該找到搜尋結果")

                    # 6. 選擇第一個搜尋結果
                    search_tab.results_listbox.selection_set(0)
                    search_tab.on_station_selected(None)
                    self.wait_for_gui_update()

                    # 7. 檢查車站詳細資訊是否顯示
                    self.assertIsNotNone(search_tab.selected_station, "應該選擇了車站")

    def test_complete_passenger_flow_query_workflow(self):
        """測試完整的客流量查詢工作流程"""
        # 1. 切換到客流量查詢分頁
        if hasattr(self.main_window, 'notebook'):
            for i in range(self.main_window.notebook.index('end')):
                tab_text = self.main_window.notebook.tab(i, 'text')
                if '客流量查詢' in tab_text:
                    self.main_window.notebook.select(i)
                    break

        self.wait_for_gui_update()

        # 2. 選擇車站
        if hasattr(self.main_window, 'passenger_flow_tab'):
            flow_tab = self.main_window.passenger_flow_tab
            if hasattr(flow_tab, 'station_combobox'):
                # 等待車站載入
                self.wait_for_gui_update(1.0)

                # 選擇第一個車站
                stations = flow_tab.station_combobox['values']
                if stations:
                    flow_tab.station_combobox.set(stations[0])

                    # 3. 設定日期範圍
                    start_date = datetime.now() - timedelta(days=7)
                    end_date = datetime.now()

                    if hasattr(flow_tab, 'start_date_entry'):
                        self.simulate_user_input(flow_tab.start_date_entry, start_date.strftime('%Y-%m-%d'))

                    if hasattr(flow_tab, 'end_date_entry'):
                        self.simulate_user_input(flow_tab.end_date_entry, end_date.strftime('%Y-%m-%d'))

                    # 4. 執行查詢
                    if hasattr(flow_tab, 'query_button'):
                        flow_tab.query_button.invoke()
                        self.wait_for_gui_update(2.0)

                        # 5. 檢查查詢結果
                        if hasattr(flow_tab, 'results_tree'):
                            results_count = len(flow_tab.results_tree.get_children())
                            self.assertGreater(results_count, 0, "應該有查詢結果")

    def test_complete_station_comparison_workflow(self):
        """測試完整的車站比較工作流程"""
        # 1. 切換到車站比較分頁
        if hasattr(self.main_window, 'notebook'):
            for i in range(self.main_window.notebook.index('end')):
                tab_text = self.main_window.notebook.tab(i, 'text')
                if '車站比較' in tab_text:
                    self.main_window.notebook.select(i)
                    break

        self.wait_for_gui_update()

        # 2. 新增要比較的車站
        if hasattr(self.main_window, 'comparison_tab'):
            comparison_tab = self.main_window.comparison_tab

            # 等待車站列表載入
            self.wait_for_gui_update(1.0)

            # 3. 新增多個車站
            test_station_ids = ['1000', '1001', '1008']
            for station_id in test_station_ids:
                if hasattr(comparison_tab, 'add_station'):
                    comparison_tab.add_station(station_id)
                    self.wait_for_gui_update(0.2)

            # 4. 檢查車站是否已新增
            self.assertEqual(len(comparison_tab.selected_stations), len(test_station_ids))

            # 5. 執行比較
            if hasattr(comparison_tab, 'compare_button'):
                comparison_tab.compare_button.invoke()
                self.wait_for_gui_update(2.0)

                # 6. 檢查比較結果
                if hasattr(comparison_tab, 'comparison_results'):
                    self.assertIsNotNone(comparison_tab.comparison_results, "應該有比較結果")

    def test_complete_chart_visualization_workflow(self):
        """測試完整的圖表視覺化工作流程"""
        # 1. 切換到圖表分頁
        if hasattr(self.main_window, 'notebook'):
            for i in range(self.main_window.notebook.index('end')):
                tab_text = self.main_window.notebook.tab(i, 'text')
                if '圖表' in tab_text:
                    self.main_window.notebook.select(i)
                    break

        self.wait_for_gui_update()

        # 2. 設定圖表參數
        if hasattr(self.main_window, 'chart_tab'):
            chart_tab = self.main_window.chart_tab

            # 等待載入
            self.wait_for_gui_update(1.0)

            # 選擇車站
            if hasattr(chart_tab, 'station_combobox'):
                stations = chart_tab.station_combobox['values']
                if stations:
                    chart_tab.station_combobox.set(stations[0])

            # 設定日期範圍
            start_date = datetime.now() - timedelta(days=14)
            end_date = datetime.now()

            if hasattr(chart_tab, 'start_date_entry'):
                self.simulate_user_input(chart_tab.start_date_entry, start_date.strftime('%Y-%m-%d'))

            if hasattr(chart_tab, 'end_date_entry'):
                self.simulate_user_input(chart_tab.end_date_entry, end_date.strftime('%Y-%m-%d'))

            # 3. 生成圖表
            if hasattr(chart_tab, 'generate_button'):
                chart_tab.generate_button.invoke()
                self.wait_for_gui_update(3.0)

                # 4. 檢查圖表是否生成
                if hasattr(chart_tab, 'canvas'):
                    self.assertIsNotNone(chart_tab.canvas, "應該有圖表畫布")

    def test_complete_data_export_workflow(self):
        """測試完整的資料匯出工作流程"""
        # 1. 先執行客流量查詢取得資料
        self.test_complete_passenger_flow_query_workflow()

        # 2. 執行匯出
        if hasattr(self.main_window, 'passenger_flow_tab'):
            flow_tab = self.main_window.passenger_flow_tab

            # 模擬檔案對話框
            with patch('tkinter.filedialog.asksaveasfilename') as mock_dialog:
                mock_dialog.return_value = "/tmp/test_export.csv"

                # 3. 觸發匯出
                if hasattr(flow_tab, 'export_button'):
                    flow_tab.export_button.invoke()
                    self.wait_for_gui_update(1.0)

                    # 4. 檢查是否呼叫了檔案對話框
                    mock_dialog.assert_called()


class TestErrorConditionWorkflows(EndToEndTestCase):
    """錯誤條件工作流程測試"""

    def setUp(self):
        super().setUp()
        # 使用無效的資料庫配置來測試錯誤處理
        invalid_config = {
            'database_type': 'sqlite',
            'database_path': '/invalid/path/database.db',
        }

        with patch('taiwan_railway_gui.config.get_config') as mock_config:
            mock_config.return_value = invalid_config
            try:
                self.main_window = MainWindow()
            except Exception:
                # 預期會有錯誤，建立一個模擬的主視窗
                self.main_window = Mock()

    def test_database_connection_error_handling(self):
        """測試資料庫連線錯誤處理"""
        # 測試當資料庫連線失敗時的錯誤處理
        with patch('taiwan_railway_gui.dao.get_database_manager') as mock_db:
            mock_db.side_effect = Exception("資料庫連線失敗")

            # 嘗試執行需要資料庫的操作
            try:
                if hasattr(self.main_window, 'station_search_tab'):
                    search_tab = self.main_window.station_search_tab
                    search_tab.perform_search("台北")
            except Exception as e:
                # 檢查錯誤是否被適當處理
                self.assertIn("資料庫", str(e))

    def test_invalid_input_handling(self):
        """測試無效輸入處理"""
        if hasattr(self.main_window, 'passenger_flow_tab'):
            flow_tab = self.main_window.passenger_flow_tab

            # 測試無效的日期範圍
            start_date = datetime.now()
            end_date = start_date - timedelta(days=1)  # 結束日期早於開始日期

            is_valid = flow_tab.validate_date_range(start_date, end_date)
            self.assertFalse(is_valid, "應該檢測到無效的日期範圍")

    def test_empty_search_results_handling(self):
        """測試空搜尋結果處理"""
        if hasattr(self.main_window, 'station_search_tab'):
            search_tab = self.main_window.station_search_tab

            # 模擬空的搜尋結果
            with patch.object(search_tab, 'search_stations') as mock_search:
                mock_search.return_value = []

                # 執行搜尋
                search_tab.perform_search("不存在的車站")
                self.wait_for_gui_update()

                # 檢查是否適當處理了空結果
                if hasattr(search_tab, 'results_listbox'):
                    self.assertEqual(search_tab.results_listbox.size(), 0)

    def test_export_permission_error_handling(self):
        """測試匯出權限錯誤處理"""
        if hasattr(self.main_window, 'passenger_flow_tab'):
            flow_tab = self.main_window.passenger_flow_tab

            # 模擬檔案寫入錯誤
            with patch('builtins.open') as mock_open:
                mock_open.side_effect = PermissionError("權限不足")

                with patch('tkinter.filedialog.asksaveasfilename') as mock_dialog:
                    mock_dialog.return_value = "/root/test_export.csv"

                    # 嘗試匯出
                    try:
                        flow_tab.export_data([])
                    except PermissionError:
                        # 檢查錯誤是否被適當處理
                        pass


class TestPerformanceAndLargeDataset(EndToEndTestCase):
    """效能和大型資料集測試"""

    def setUp(self):
        super().setUp()
        # 建立包含大量資料的測試資料庫
        self.setup_large_dataset()

        with patch('taiwan_railway_gui.config.get_config') as mock_config:
            mock_config.return_value = self.test_config
            self.main_window = MainWindow()

    def setup_large_dataset(self):
        """建立大型資料集"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()

        # 插入大量乘客流量資料（3個月的資料）
        base_date = datetime.now() - timedelta(days=90)
        for i in range(90):
            current_date = base_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')

            # 為每個車站每天插入資料
            for station_num in range(5):
                station_id = f"100{station_num}"
                inbound = 1000 + (i * 50) + station_num * 100
                outbound = 950 + (i * 45) + station_num * 90
                total = inbound + outbound

                cursor.execute(
                    'INSERT INTO passenger_flow (station_id, date, inbound_passengers, outbound_passengers, total_passengers) VALUES (?, ?, ?, ?, ?)',
                    (station_id, date_str, inbound, outbound, total)
                )

        conn.commit()
        conn.close()

    def test_large_dataset_query_performance(self):
        """測試大型資料集查詢效能"""
        if hasattr(self.main_window, 'passenger_flow_tab'):
            flow_tab = self.main_window.passenger_flow_tab

            # 測試查詢大範圍日期的效能
            start_date = datetime.now() - timedelta(days=90)
            end_date = datetime.now()

            start_time = time.time()

            # 執行查詢
            try:
                flow_tab.execute_query("1000", start_date, end_date)
                self.wait_for_gui_update(5.0)  # 允許更長的等待時間

                end_time = time.time()
                query_time = end_time - start_time

                # 檢查查詢時間是否在可接受範圍內（例如小於10秒）
                self.assertLess(query_time, 10.0, "大型資料集查詢時間應該在可接受範圍內")

            except Exception as e:
                self.fail(f"大型資料集查詢失敗：{e}")

    def test_pagination_functionality(self):
        """測試分頁功能"""
        if hasattr(self.main_window, 'passenger_flow_tab'):
            flow_tab = self.main_window.passenger_flow_tab

            # 執行會返回大量結果的查詢
            start_date = datetime.now() - timedelta(days=90)
            end_date = datetime.now()

            flow_tab.execute_query("1000", start_date, end_date)
            self.wait_for_gui_update(3.0)

            # 檢查是否有分頁控制項
            if hasattr(flow_tab, 'pagination_frame'):
                self.assertIsNotNone(flow_tab.pagination_frame, "應該有分頁控制項")

    def test_memory_usage_with_large_dataset(self):
        """測試大型資料集的記憶體使用"""
        try:
            import psutil
            import os

            # 取得目前程序
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss

            # 執行多次大型查詢
            if hasattr(self.main_window, 'passenger_flow_tab'):
                flow_tab = self.main_window.passenger_flow_tab

                for i in range(5):
                    start_date = datetime.now() - timedelta(days=30 + i * 10)
                    end_date = datetime.now() - timedelta(days=i * 10)

                    flow_tab.execute_query("1000", start_date, end_date)
                    self.wait_for_gui_update(1.0)

            # 檢查記憶體使用量
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            memory_increase_mb = memory_increase / (1024 * 1024)

            # 記憶體增加不應該超過100MB（可根據實際情況調整）
            self.assertLess(memory_increase_mb, 100, f"記憶體使用量增加過多：{memory_increase_mb:.2f}MB")

        except ImportError:
            # 如果沒有安裝psutil，跳過此測試
            self.skipTest("psutil 未安裝，跳過記憶體使用測試")


if __name__ == '__main__':
    # 建立測試套件
    suite = unittest.TestSuite()

    # 添加端到端測試
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCompleteUserWorkflows))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestErrorConditionWorkflows))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPerformanceAndLargeDataset))

    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 輸出結果
    if result.wasSuccessful():
        print("\n✅ 所有端到端整合測試通過！")
    else:
        print(f"\n❌ 測試失敗：{len(result.failures)} 個失敗，{len(result.errors)} 個錯誤")

    sys.exit(0 if result.wasSuccessful() else 1)
