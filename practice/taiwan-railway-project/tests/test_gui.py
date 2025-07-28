"""
GUI 元件單元測試

測試主視窗和基礎 GUI 元件的功能。
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from taiwan_railway_gui.gui.main_window import MainWindow, LoadingIndicator, StatusBar
from taiwan_railway_gui.gui.base_tab import BaseTab


class TestLoadingIndicator(unittest.TestCase):
    """測試載入指示器"""

    def setUp(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏視窗
        self.indicator = LoadingIndicator(self.root)

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    def test_start_loading(self):
        """測試開始載入"""
        self.indicator.start("測試載入")

        self.assertTrue(self.indicator.is_running)
        self.assertEqual(self.indicator.status_var.get(), "測試載入")

    def test_stop_loading(self):
        """測試停止載入"""
        self.indicator.start("測試載入")
        self.indicator.stop("完成")

        self.assertFalse(self.indicator.is_running)
        self.assertEqual(self.indicator.status_var.get(), "完成")


class TestStatusBar(unittest.TestCase):
    """測試狀態列"""

    def setUp(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏視窗
        self.status_bar = StatusBar(self.root)

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    def test_set_message(self):
        """測試設定訊息"""
        self.status_bar.set_message("測試訊息")
        self.assertEqual(self.status_bar.loading_indicator.status_var.get(), "測試訊息")

    def test_set_database_status(self):
        """測試設定資料庫狀態"""
        # 測試連線狀態
        self.status_bar.set_database_status(True)
        self.assertEqual(self.status_bar.db_status_var.get(), "資料庫: 已連線")

        # 測試未連線狀態
        self.status_bar.set_database_status(False)
        self.assertEqual(self.status_bar.db_status_var.get(), "資料庫: 未連線")

    def test_loading_operations(self):
        """測試載入操作"""
        self.status_bar.start_loading("載入中")
        self.assertTrue(self.status_bar.loading_indicator.is_running)

        self.status_bar.stop_loading("完成")
        self.assertFalse(self.status_bar.loading_indicator.is_running)


class TestMainWindow(unittest.TestCase):
    """測試主視窗"""

    def setUp(self):
        """設定測試環境"""
        # 模擬資料庫管理器
        self.mock_db_manager = Mock()
        self.mock_db_manager.test_connection.return_value = True
        self.mock_db_manager.is_connected = True

    @patch('taiwan_railway_gui.gui.main_window.get_database_manager')
    def test_main_window_creation(self, mock_get_db_manager):
        """測試主視窗建立"""
        mock_get_db_manager.return_value = self.mock_db_manager

        # 建立主視窗但不顯示
        main_window = MainWindow()
        main_window.root.withdraw()

        # 檢查基本屬性
        self.assertIsNotNone(main_window.root)
        self.assertIsNotNone(main_window.notebook)
        self.assertIsNotNone(main_window.status_bar)
        self.assertIsNotNone(main_window.menubar)

        # 檢查分頁
        self.assertEqual(len(main_window.tabs), 4)
        expected_tabs = ['station_search', 'passenger_flow', 'comparison', 'charts']
        for tab_id in expected_tabs:
            self.assertIn(tab_id, main_window.tabs)

        # 清理
        main_window.root.destroy()

    @patch('taiwan_railway_gui.gui.main_window.get_database_manager')
    def test_tab_switching(self, mock_get_db_manager):
        """測試分頁切換"""
        mock_get_db_manager.return_value = self.mock_db_manager

        main_window = MainWindow()
        main_window.root.withdraw()

        # 測試切換到不同分頁
        main_window.switch_to_tab('passenger_flow')
        # 由於是模擬環境，主要檢查方法不會拋出異常

        # 測試取得分頁框架
        frame = main_window.get_tab_frame('station_search')
        self.assertIsNotNone(frame)

        # 測試不存在的分頁
        frame = main_window.get_tab_frame('nonexistent')
        self.assertIsNone(frame)

        # 清理
        main_window.root.destroy()

    @patch('taiwan_railway_gui.gui.main_window.get_database_manager')
    def test_menu_creation(self, mock_get_db_manager):
        """測試選單建立"""
        mock_get_db_manager.return_value = self.mock_db_manager

        main_window = MainWindow()
        main_window.root.withdraw()

        # 檢查選單列存在
        self.assertIsNotNone(main_window.menubar)
        self.assertIsNotNone(main_window.file_menu)
        self.assertIsNotNone(main_window.view_menu)
        self.assertIsNotNone(main_window.tools_menu)
        self.assertIsNotNone(main_window.help_menu)

        # 清理
        main_window.root.destroy()


class TestBaseTab(unittest.TestCase):
    """測試基礎分頁"""

    def setUp(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.root.withdraw()

        # 建立測試用的基礎分頁子類別
        class TestTab(BaseTab):
            def setup_ui(self):
                self.test_label = tk.Label(self.frame, text="測試分頁")
                self.test_label.pack()

        self.TestTab = TestTab

    def tearDown(self):
        """清理測試環境"""
        self.root.destroy()

    @patch('taiwan_railway_gui.gui.base_tab.get_database_manager')
    @patch('taiwan_railway_gui.gui.base_tab.create_validation_service')
    def test_base_tab_creation(self, mock_validation_service, mock_db_manager):
        """測試基礎分頁建立"""
        # 模擬服務
        mock_db_manager.return_value = Mock()
        mock_validation_service.return_value = Mock()

        # 建立測試分頁
        tab = self.TestTab(self.root)

        # 檢查基本屬性
        self.assertIsNotNone(tab.frame)
        self.assertIsNotNone(tab.db_manager)
        self.assertIsNotNone(tab.validation_service)
        self.assertIsNotNone(tab.colors)
        self.assertIsNotNone(tab.fonts)
        self.assertIsNotNone(tab.layout)

    @patch('taiwan_railway_gui.gui.base_tab.get_database_manager')
    @patch('taiwan_railway_gui.gui.base_tab.create_validation_service')
    def test_create_ui_components(self, mock_validation_service, mock_db_manager):
        """測試 UI 元件建立"""
        # 模擬服務
        mock_db_manager.return_value = Mock()
        mock_validation_service.return_value = Mock()

        tab = self.TestTab(self.root)

        # 測試建立區段框架
        section_frame = tab.create_section_frame(tab.frame, "測試區段")
        self.assertIsInstance(section_frame, tk.LabelFrame)

        # 測試建立輸入框架
        input_frame = tab.create_input_frame(tab.frame)
        self.assertIsInstance(input_frame, tk.Frame)

        # 測試建立帶標籤的輸入框
        label, entry = tab.create_labeled_entry(tab.frame, "測試標籤")
        self.assertIsInstance(label, tk.Label)
        self.assertIsInstance(entry, tk.Entry)

        # 測試建立帶標籤的下拉選單
        label, combobox = tab.create_labeled_combobox(tab.frame, "測試選單", ["選項1", "選項2"])
        self.assertIsInstance(label, tk.Label)
        self.assertIsInstance(combobox, tk.Combobox)

    @patch('taiwan_railway_gui.gui.base_tab.get_database_manager')
    @patch('taiwan_railway_gui.gui.base_tab.create_validation_service')
    def test_validation_methods(self, mock_validation_service, mock_db_manager):
        """測試驗證方法"""
        # 模擬服務
        mock_db_manager.return_value = Mock()
        mock_validator = Mock()
        mock_validator.validate_station_code.return_value = (True, "")
        mock_validation_service.return_value = mock_validator

        tab = self.TestTab(self.root)

        # 測試驗證輸入
        is_valid, error_msg = tab.validate_input("1000", "validate_station_code")
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")

        # 驗證方法被呼叫
        mock_validator.validate_station_code.assert_called_once_with("1000")


if __name__ == '__main__':
    # 設定測試環境
    import os
    os.environ['DISPLAY'] = ':0'  # 設定顯示環境（Linux）

    unittest.main()