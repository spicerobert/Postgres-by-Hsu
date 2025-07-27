"""
主應用程式視窗

實作應用程式的主視窗，包括選單列、分頁介面、狀態列和載入指示器。
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import threading
from typing import Optional, Callable, Any
from taiwan_railway_gui.config import get_config
from taiwan_railway_gui.dao import get_database_manager
from taiwan_railway_gui.services.error_handler import get_error_handler, ErrorCategory, ErrorSeverity
from taiwan_railway_gui.services.async_manager import get_async_manager
from taiwan_railway_gui.services.cache_manager import get_cache_manager
from taiwan_railway_gui.utils.memory_manager import get_memory_manager, start_memory_monitoring, stop_memory_monitoring
from taiwan_railway_gui.gui.user_feedback import create_user_feedback_manager


class LoadingIndicator:
    """載入指示器元件"""

    def __init__(self, parent: tk.Widget):
        """
        初始化載入指示器

        Args:
            parent: 父元件
        """
        self.parent = parent
        self.is_running = False

        # 建立進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            parent,
            mode='indeterminate',
            variable=self.progress_var
        )

        # 建立狀態標籤
        self.status_var = tk.StringVar(value="就緒")
        self.status_label = ttk.Label(
            parent,
            textvariable=self.status_var,
            font=get_config('fonts')['body']
        )

    def start(self, message: str = "載入中..."):
        """
        開始載入動畫

        Args:
            message: 載入訊息
        """
        if not self.is_running:
            self.is_running = True
            self.status_var.set(message)
            self.progress_bar.start(10)  # 每10ms更新一次

    def stop(self, message: str = "就緒"):
        """
        停止載入動畫

        Args:
            message: 完成訊息
        """
        if self.is_running:
            self.is_running = False
            self.progress_bar.stop()
            self.status_var.set(message)

    def pack(self, **kwargs):
        """打包元件"""
        # 分離 padx 參數避免衝突
        label_kwargs = kwargs.copy()
        progress_kwargs = kwargs.copy()
        progress_kwargs['padx'] = (10, 0)

        self.status_label.pack(side=tk.LEFT, **label_kwargs)
        self.progress_bar.pack(side=tk.RIGHT, **progress_kwargs)

    def grid(self, **kwargs):
        """網格佈局"""
        self.status_label.grid(**kwargs)
        self.progress_bar.grid(row=kwargs.get('row', 0), column=kwargs.get('column', 0) + 1, padx=(10, 0))


class StatusBar:
    """狀態列元件"""

    def __init__(self, parent: tk.Widget):
        """
        初始化狀態列

        Args:
            parent: 父元件
        """
        self.parent = parent

        # 建立狀態列框架
        self.frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)

        # 建立載入指示器
        self.loading_indicator = LoadingIndicator(self.frame)
        self.loading_indicator.pack(fill=tk.X, padx=5, pady=2)

        # 建立資料庫連線狀態
        self.db_status_var = tk.StringVar(value="資料庫: 未連線")
        self.db_status_label = ttk.Label(
            self.frame,
            textvariable=self.db_status_var,
            font=get_config('fonts')['body']
        )
        self.db_status_label.pack(side=tk.RIGHT, padx=5)

    def set_message(self, message: str):
        """設定狀態訊息"""
        self.loading_indicator.status_var.set(message)

    def set_database_status(self, connected: bool):
        """設定資料庫連線狀態"""
        if connected:
            self.db_status_var.set("資料庫: 已連線")
        else:
            self.db_status_var.set("資料庫: 未連線")

    def start_loading(self, message: str = "載入中..."):
        """開始載入"""
        self.loading_indicator.start(message)

    def stop_loading(self, message: str = "就緒"):
        """停止載入"""
        self.loading_indicator.stop(message)

    def pack(self, **kwargs):
        """打包狀態列"""
        self.frame.pack(**kwargs)


class MainWindow:
    """
    主應用程式視窗

    協調所有應用程式功能的中央樞紐，包括分頁介面、選單列和狀態列。
    """

    def __init__(self):
        """初始化主視窗"""
        self.logger = logging.getLogger(__name__)

        # 載入配置
        self.gui_config = get_config('gui')
        self.colors = get_config('colors')
        self.fonts = get_config('fonts')
        self.layout = get_config('layout')

        # 建立主視窗
        self.root = tk.Tk()
        self.setup_window()

        # 建立選單列
        self.setup_menu()

        # 建立主要內容區域
        self.setup_main_content()

        # 分頁字典（將在後續任務中填充）
        self.tabs = {}

        # 建立狀態列
        self.setup_status_bar()

        # 初始化服務
        self.db_manager = get_database_manager()
        self.error_handler = get_error_handler()
        self.feedback_manager = create_user_feedback_manager(self.root)

        # 初始化效能服務
        self.async_manager = get_async_manager()
        self.cache_manager = get_cache_manager()
        self.memory_manager = get_memory_manager()

        # 註冊錯誤回調
        self.setup_error_callbacks()

        # 設定效能監控
        self.setup_performance_monitoring()

        # 初始化資料庫連線
        self.check_database_connection()

        self.logger.info("主視窗初始化完成")

    def setup_error_callbacks(self):
        """設定錯誤回調"""
        def database_error_callback(error_info):
            """資料庫錯誤回調"""
            self.status_bar.set_database_status(False)
            if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                self.feedback_manager.show_error(
                    error_info.user_message,
                    "資料庫錯誤",
                    error_info.suggested_actions
                )

        def validation_error_callback(error_info):
            """驗證錯誤回調"""
            if error_info.severity == ErrorSeverity.LOW:
                self.feedback_manager.show_warning(error_info.user_message, "輸入驗證")
            else:
                self.feedback_manager.show_error(error_info.user_message, "驗證錯誤")

        def gui_error_callback(error_info):
            """GUI 錯誤回調"""
            self.feedback_manager.show_error(
                error_info.user_message,
                "介面錯誤",
                error_info.suggested_actions
            )

        # 註冊回調
        self.error_handler.register_error_callback(ErrorCategory.DATABASE, database_error_callback)
        self.error_handler.register_error_callback(ErrorCategory.VALIDATION, validation_error_callback)
        self.error_handler.register_error_callback(ErrorCategory.GUI, gui_error_callback)

    def setup_performance_monitoring(self):
        """設定效能監控"""
        try:
            # 設定記憶體警告回調
            def memory_alert_callback(alert):
                if alert.level == 'critical':
                    self.feedback_manager.show_warning(
                        f"記憶體使用量過高: {alert.memory_info.percent:.1f}%",
                        "效能警告",
                        ["建議清理快取", "關閉不必要的分頁"]
                    )
                    # 自動清理快取
                    self.clear_all_caches()

            self.memory_manager.register_alert_callback(memory_alert_callback)

            # 啟動記憶體監控
            start_memory_monitoring()

            # 設定記憶體清理回調
            def cleanup_gui_resources():
                # 清理 GUI 相關資源
                try:
                    # 清理圖表快取
                    if 'charts' in self.tabs:
                        chart_tab = self.tabs['charts']
                        if hasattr(chart_tab, 'chart_canvas') and chart_tab.chart_canvas:
                            chart_tab.chart_canvas.clear_chart()

                    # 強制垃圾回收
                    import gc
                    gc.collect()

                except Exception as e:
                    self.logger.error(f"GUI 資源清理失敗: {e}")

            self.memory_manager.register_cleanup_callback(cleanup_gui_resources)

            self.logger.info("效能監控已啟動")

        except Exception as e:
            self.logger.error(f"效能監控設定失敗: {e}")

    def setup_window(self):
        """設定主視窗屬性"""
        # 設定標題和圖示
        self.root.title(self.gui_config['window_title'])

        # 設定視窗大小
        self.root.geometry(self.gui_config['window_size'])
        self.root.minsize(*self.gui_config['min_window_size'])

        # 設定視窗關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 設定樣式
        self.style = ttk.Style()
        self.setup_styles()

    def setup_styles(self):
        """設定 ttk 樣式"""
        from taiwan_railway_gui.gui.styles import get_style_manager
        from taiwan_railway_gui.gui.accessibility import get_keyboard_navigation_manager, get_accessibility_helper

        # 初始化樣式管理器
        self.style_manager = get_style_manager()
        self.style_manager.configure_ttk_styles(self.style)

        # 初始化無障礙功能
        self.keyboard_nav = get_keyboard_navigation_manager(self.root)
        self.accessibility = get_accessibility_helper()

        # 設定視窗樣式
        theme = self.style_manager.get_theme()
        colors = theme['colors']

        self.root.configure(bg=colors['background'])

        # 註冊自訂快捷鍵
        self.setup_custom_shortcuts()

    def setup_custom_shortcuts(self):
        """設定自訂快捷鍵"""
        # 註冊應用程式特定的快捷鍵
        self.keyboard_nav.register_shortcut('<Control-q>', self.on_closing, "結束應用程式")
        self.keyboard_nav.register_shortcut('<Control-t>', self.test_database_connection, "測試資料庫連線")
        self.keyboard_nav.register_shortcut('<Control-l>', self.clear_all_caches, "清除所有快取")
        self.keyboard_nav.register_shortcut('<F1>', self.show_help, "顯示說明")
        self.keyboard_nav.register_shortcut('<F5>', self.refresh_data, "重新整理資料")

        # 分頁切換快捷鍵
        self.keyboard_nav.register_shortcut('<Control-1>', lambda: self.switch_to_tab(0), "切換到車站搜尋")
        self.keyboard_nav.register_shortcut('<Control-2>', lambda: self.switch_to_tab(1), "切換到客流量查詢")
        self.keyboard_nav.register_shortcut('<Control-3>', lambda: self.switch_to_tab(2), "切換到車站比較")
        self.keyboard_nav.register_shortcut('<Control-4>', lambda: self.switch_to_tab(3), "切換到圖表視覺化")

    def switch_to_tab(self, tab_index: int):
        """切換到指定分頁"""
        try:
            if 0 <= tab_index < len(self.notebook.tabs()):
                self.notebook.select(tab_index)
        except Exception as e:
            self.logger.error(f"切換分頁失敗: {e}")

    def setup_menu(self):
        """建立選單列"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # 檔案選單
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="檔案", menu=self.file_menu)
        self.file_menu.add_command(label="匯出資料...", command=self.export_data)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="結束", command=self.on_closing)

        # 檢視選單
        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="檢視", menu=self.view_menu)
        self.view_menu.add_command(label="重新整理", command=self.refresh_data)
        self.view_menu.add_command(label="清除快取", command=self.clear_cache)

        # 工具選單
        self.tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="工具", menu=self.tools_menu)
        self.tools_menu.add_command(label="資料庫連線測試", command=self.test_database_connection)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="錯誤歷史記錄", command=self.show_error_history)
        self.tools_menu.add_command(label="錯誤統計", command=self.show_error_statistics)
        self.tools_menu.add_command(label="清除錯誤記錄", command=self.clear_error_history)
        self.tools_menu.add_separator()

        # 效能選單
        self.performance_menu = tk.Menu(self.tools_menu, tearoff=0)
        self.tools_menu.add_cascade(label="效能管理", menu=self.performance_menu)
        self.performance_menu.add_command(label="記憶體使用狀況", command=self.show_memory_usage)
        self.performance_menu.add_command(label="快取統計", command=self.show_cache_statistics)
        self.performance_menu.add_command(label="清理記憶體", command=self.cleanup_memory)
        self.performance_menu.add_command(label="清除所有快取", command=self.clear_all_caches)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="設定...", command=self.show_settings)

        # 說明選單
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="說明", menu=self.help_menu)
        self.help_menu.add_command(label="使用說明", command=self.show_help)
        self.help_menu.add_command(label="關於", command=self.show_about)

    def setup_main_content(self):
        """建立主要內容區域"""
        # 建立主框架
        self.main_frame = ttk.Frame(self.root, style='Content.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立分頁控制項
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 建立預設分頁（將在後續任務中實作具體內容）
        self.create_placeholder_tabs()

        # 綁定分頁切換事件
        self.notebook.bind("<<NotebookChanged>>", self.on_tab_changed)

    def create_placeholder_tabs(self):
        """建立分頁"""
        # 建立車站搜尋分頁
        self.create_station_search_tab()

        # 建立客流量查詢分頁
        self.create_passenger_flow_tab()

        # 建立車站比較分頁
        self.create_comparison_tab()

        # 建立圖表視覺化分頁
        self.create_chart_tab()

    def create_station_search_tab(self):
        """建立車站搜尋分頁"""
        from taiwan_railway_gui.gui.station_search_tab import create_station_search_tab

        # 建立分頁框架
        tab_frame = ttk.Frame(self.notebook)

        # 建立車站搜尋元件
        station_search_tab = create_station_search_tab(tab_frame, self)

        # 加入分頁
        self.notebook.add(tab_frame, text="車站搜尋")
        self.tabs['station_search'] = station_search_tab

        # 添加到鍵盤導航
        self.keyboard_nav.add_to_focus_ring(tab_frame, priority=1)

    def create_passenger_flow_tab(self):
        """建立客流量查詢分頁"""
        from taiwan_railway_gui.gui.passenger_flow_tab import create_passenger_flow_tab

        # 建立分頁框架
        tab_frame = ttk.Frame(self.notebook)

        # 建立客流量查詢元件
        passenger_flow_tab = create_passenger_flow_tab(tab_frame, self)

        # 加入分頁
        self.notebook.add(tab_frame, text="客流量查詢")
        self.tabs['passenger_flow'] = passenger_flow_tab

        # 添加到鍵盤導航
        self.keyboard_nav.add_to_focus_ring(tab_frame, priority=2)

    def create_comparison_tab(self):
        """建立車站比較分頁"""
        from taiwan_railway_gui.gui.comparison_tab import create_comparison_tab

        # 建立分頁框架
        tab_frame = ttk.Frame(self.notebook)

        # 建立車站比較元件
        comparison_tab = create_comparison_tab(tab_frame, self)

        # 加入分頁
        self.notebook.add(tab_frame, text="車站比較")
        self.tabs['comparison'] = comparison_tab

        # 添加到鍵盤導航
        self.keyboard_nav.add_to_focus_ring(tab_frame, priority=3)

    def create_chart_tab(self):
        """建立圖表視覺化分頁"""
        from taiwan_railway_gui.gui.chart_tab import create_chart_tab

        # 建立分頁框架
        tab_frame = ttk.Frame(self.notebook)

        # 建立圖表視覺化元件
        chart_tab = create_chart_tab(tab_frame, self)

        # 加入分頁
        self.notebook.add(tab_frame, text="圖表視覺化")
        self.tabs['charts'] = chart_tab

        # 添加到鍵盤導航
        self.keyboard_nav.add_to_focus_ring(tab_frame, priority=4)

    def setup_status_bar(self):
        """建立狀態列"""
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def check_database_connection(self):
        """檢查資料庫連線"""
        def check_connection():
            try:
                connected = self.db_manager.test_connection()
                # 在主執行緒中更新 GUI
                self.root.after(0, lambda: self.status_bar.set_database_status(connected))
                if connected:
                    self.root.after(0, lambda: self.status_bar.set_message("資料庫連線正常"))
                else:
                    self.root.after(0, lambda: self.status_bar.set_message("資料庫連線失敗"))
            except Exception as e:
                self.logger.error(f"資料庫連線檢查失敗: {e}")
                self.root.after(0, lambda: self.status_bar.set_database_status(False))
                self.root.after(0, lambda: self.status_bar.set_message("資料庫連線錯誤"))

        # 在背景執行緒中檢查連線
        threading.Thread(target=check_connection, daemon=True).start()

    def on_tab_changed(self, event):
        """分頁切換事件處理"""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        self.status_bar.set_message(f"切換到 {tab_text}")
        self.logger.debug(f"切換到分頁: {tab_text}")

    def export_data(self):
        """匯出資料"""
        # 取得目前分頁
        current_tab = self.notebook.select()
        if current_tab:
            tab_text = self.notebook.tab(current_tab, "text")

            # 檢查分頁類型並呼叫對應的匯出功能
            if tab_text == "車站搜尋":
                station_search_tab = self.tabs.get('station_search')
                if station_search_tab and hasattr(station_search_tab, 'export_data'):
                    station_search_tab.export_data()
                else:
                    messagebox.showinfo("匯出資料", "車站搜尋分頁匯出功能不可用")
            elif tab_text == "客流量查詢":
                passenger_flow_tab = self.tabs.get('passenger_flow')
                if passenger_flow_tab and hasattr(passenger_flow_tab, 'export_data'):
                    passenger_flow_tab.export_data()
                else:
                    messagebox.showinfo("匯出資料", "客流量查詢分頁匯出功能不可用")
            elif tab_text == "車站比較":
                comparison_tab = self.tabs.get('comparison')
                if comparison_tab and hasattr(comparison_tab, 'export_data'):
                    comparison_tab.export_data()
                else:
                    messagebox.showinfo("匯出資料", "車站比較分頁匯出功能不可用")
            elif tab_text == "圖表視覺化":
                chart_tab = self.tabs.get('charts')
                if chart_tab and hasattr(chart_tab, 'export_data'):
                    chart_tab.export_data()
                else:
                    messagebox.showinfo("匯出資料", "圖表視覺化分頁匯出功能不可用")
            else:
                messagebox.showinfo("匯出資料", f"匯出 {tab_text} 的資料功能將在後續任務中實作")

    def refresh_data(self):
        """重新整理資料"""
        self.status_bar.start_loading("重新整理資料中...")

        def refresh():
            try:
                # 重新檢查資料庫連線
                self.check_database_connection()
                # 在主執行緒中停止載入
                self.root.after(1000, lambda: self.status_bar.stop_loading("資料已重新整理"))
            except Exception as e:
                self.logger.error(f"重新整理失敗: {e}")
                self.root.after(0, lambda: self.status_bar.stop_loading("重新整理失敗"))

        threading.Thread(target=refresh, daemon=True).start()

    def clear_cache(self):
        """清除快取"""
        try:
            # 清除車站搜尋分頁快取
            station_search_tab = self.tabs.get('station_search')
            if station_search_tab and hasattr(station_search_tab, 'station_dao'):
                station_search_tab.station_dao.clear_cache()

            messagebox.showinfo("清除快取", "車站資料快取已清除")
            self.status_bar.set_message("快取已清除")
        except Exception as e:
            self.logger.error(f"清除快取失敗: {e}")
            messagebox.showerror("錯誤", f"清除快取失敗: {e}")

    def clear_all_caches(self):
        """清除所有快取"""
        try:
            # 清除全域快取
            self.cache_manager.clear()

            # 清除各分頁的快取
            for tab_name, tab in self.tabs.items():
                if hasattr(tab, 'clear_cache'):
                    tab.clear_cache()
                elif hasattr(tab, 'station_dao') and hasattr(tab.station_dao, 'clear_cache'):
                    tab.station_dao.clear_cache()
                elif hasattr(tab, 'passenger_flow_dao') and hasattr(tab.passenger_flow_dao, 'clear_cache'):
                    tab.passenger_flow_dao.clear_cache()

            messagebox.showinfo("清除快取", "所有快取已清除")
            self.status_bar.set_message("所有快取已清除")
            self.logger.info("所有快取已清除")
        except Exception as e:
            self.logger.error(f"清除所有快取失敗: {e}")
            messagebox.showerror("錯誤", f"清除所有快取失敗: {e}")

    def cleanup_memory(self):
        """清理記憶體"""
        try:
            self.status_bar.start_loading("清理記憶體中...")

            def cleanup_task():
                try:
                    # 執行記憶體清理
                    self.memory_manager.force_cleanup()

                    # 取得清理後的記憶體資訊
                    memory_info = self.memory_manager.get_memory_info()

                    message = f"記憶體清理完成\n目前使用量: {memory_info.percent:.1f}%"
                    self.root.after(0, lambda: messagebox.showinfo("記憶體清理", message))
                    self.root.after(0, lambda: self.status_bar.stop_loading("記憶體清理完成"))

                except Exception as e:
                    error_msg = f"記憶體清理失敗: {e}"
                    self.root.after(0, lambda: messagebox.showerror("錯誤", error_msg))
                    self.root.after(0, lambda: self.status_bar.stop_loading("記憶體清理失敗"))

            threading.Thread(target=cleanup_task, daemon=True).start()

        except Exception as e:
            self.logger.error(f"記憶體清理失敗: {e}")
            messagebox.showerror("錯誤", f"記憶體清理失敗: {e}")

    def show_memory_usage(self):
        """顯示記憶體使用狀況"""
        try:
            memory_usage = self.memory_manager.get_detailed_memory_usage()

            # 建立記憶體使用資訊視窗
            info_window = tk.Toplevel(self.root)
            info_window.title("記憶體使用狀況")
            info_window.geometry("500x400")
            info_window.resizable(True, True)

            # 建立文字區域
            text_frame = ttk.Frame(info_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 10))
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)

            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # 格式化記憶體資訊
            info_text = "記憶體使用狀況報告\n"
            info_text += "=" * 50 + "\n\n"

            # 系統記憶體
            system = memory_usage['system']
            info_text += f"系統記憶體:\n"
            info_text += f"  總計: {system['total_mb']:.1f} MB\n"
            info_text += f"  可用: {system['available_mb']:.1f} MB\n"
            info_text += f"  已用: {system['used_mb']:.1f} MB ({system['percent']:.1f}%)\n\n"

            # 程序記憶體
            process = memory_usage['process']
            info_text += f"程序記憶體:\n"
            info_text += f"  使用量: {process['memory_mb']:.1f} MB\n"
            info_text += f"  佔系統比例: {process['percent_of_system']:.2f}%\n\n"

            # 快取記憶體
            cache = memory_usage['cache']
            info_text += f"快取記憶體:\n"
            info_text += f"  使用量: {cache['memory_mb']:.1f} MB\n"
            info_text += f"  項目數: {cache['items']}\n"
            info_text += f"  命中率: {cache['hit_rate']:.1%}\n\n"

            # 分頁快取
            pagination = memory_usage['pagination']
            info_text += f"分頁快取:\n"
            info_text += f"  快取頁面數: {pagination['cached_pages']}\n"
            info_text += f"  命中率: {pagination['hit_rate']:.1%}\n\n"

            # 閾值設定
            thresholds = memory_usage['thresholds']
            info_text += f"警告閾值:\n"
            info_text += f"  警告: {thresholds['warning']:.1f}%\n"
            info_text += f"  嚴重: {thresholds['critical']:.1f}%\n\n"

            # 建議
            recommendations = self.memory_manager.get_memory_recommendations()
            if recommendations:
                info_text += "最佳化建議:\n"
                for i, rec in enumerate(recommendations, 1):
                    info_text += f"  {i}. {rec}\n"

            text_widget.insert(tk.END, info_text)
            text_widget.config(state=tk.DISABLED)

            # 建立按鈕框架
            button_frame = ttk.Frame(info_window)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

            ttk.Button(button_frame, text="重新整理",
                      command=lambda: self.refresh_memory_info(text_widget)).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="清理記憶體",
                      command=self.cleanup_memory).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="關閉",
                      command=info_window.destroy).pack(side=tk.RIGHT)

        except Exception as e:
            self.logger.error(f"顯示記憶體使用狀況失敗: {e}")
            messagebox.showerror("錯誤", f"無法顯示記憶體使用狀況: {e}")

    def refresh_memory_info(self, text_widget):
        """重新整理記憶體資訊"""
        try:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)

            memory_usage = self.memory_manager.get_detailed_memory_usage()

            # 重新格式化並插入資訊（簡化版本）
            info_text = f"記憶體使用量: {memory_usage['system']['percent']:.1f}%\n"
            info_text += f"程序記憶體: {memory_usage['process']['memory_mb']:.1f} MB\n"
            info_text += f"快取記憶體: {memory_usage['cache']['memory_mb']:.1f} MB\n"

            text_widget.insert(tk.END, info_text)
            text_widget.config(state=tk.DISABLED)

        except Exception as e:
            self.logger.error(f"重新整理記憶體資訊失敗: {e}")

    def show_cache_statistics(self):
        """顯示快取統計"""
        try:
            cache_stats = self.cache_manager.get_stats()

            # 建立統計資訊視窗
            stats_window = tk.Toplevel(self.root)
            stats_window.title("快取統計")
            stats_window.geometry("400x300")
            stats_window.resizable(False, False)

            # 建立統計標籤
            main_frame = ttk.Frame(stats_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(main_frame, text="快取統計資訊",
                     font=self.fonts['header']).pack(pady=(0, 20))

            stats_frame = ttk.Frame(main_frame)
            stats_frame.pack(fill=tk.BOTH, expand=True)

            # 統計項目
            stats_items = [
                ("快取項目數", f"{cache_stats['size']}/{cache_stats['max_size']}"),
                ("記憶體使用量", f"{cache_stats['memory_usage_mb']:.1f}/{cache_stats['max_memory_mb']:.1f} MB"),
                ("命中次數", str(cache_stats['hits'])),
                ("未命中次數", str(cache_stats['misses'])),
                ("命中率", f"{cache_stats['hit_rate']:.1%}"),
                ("淘汰次數", str(cache_stats['evictions'])),
                ("過期清理次數", str(cache_stats['expired_removals']))
            ]

            for i, (label, value) in enumerate(stats_items):
                row_frame = ttk.Frame(stats_frame)
                row_frame.pack(fill=tk.X, pady=2)

                ttk.Label(row_frame, text=f"{label}:", width=15, anchor=tk.W).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=value, anchor=tk.W).pack(side=tk.LEFT, padx=(10, 0))

            # 按鈕框架
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(20, 0))

            ttk.Button(button_frame, text="清除快取",
                      command=lambda: [self.clear_all_caches(), stats_window.destroy()]).pack(side=tk.LEFT)
            ttk.Button(button_frame, text="關閉",
                      command=stats_window.destroy).pack(side=tk.RIGHT)

        except Exception as e:
            self.logger.error(f"顯示快取統計失敗: {e}")
            messagebox.showerror("錯誤", f"無法顯示快取統計: {e}")

    def test_database_connection(self):
        """測試資料庫連線"""
        self.status_bar.start_loading("測試資料庫連線...")

        def test_connection():
            try:
                connected = self.db_manager.test_connection()
                if connected:
                    message = "資料庫連線測試成功！"
                    self.root.after(0, lambda: messagebox.showinfo("連線測試", message))
                    self.root.after(0, lambda: self.status_bar.stop_loading("連線測試成功"))
                else:
                    message = "資料庫連線測試失敗，請檢查設定。"
                    self.root.after(0, lambda: messagebox.showerror("連線測試", message))
                    self.root.after(0, lambda: self.status_bar.stop_loading("連線測試失敗"))
            except Exception as e:
                error_msg = f"連線測試錯誤: {e}"
                self.root.after(0, lambda: messagebox.showerror("錯誤", error_msg))
                self.root.after(0, lambda: self.status_bar.stop_loading("連線測試錯誤"))

        threading.Thread(target=test_connection, daemon=True).start()

    def show_settings(self):
        """顯示設定對話框"""
        messagebox.showinfo("設定", "設定功能將在後續版本中實作")

    def show_help(self):
        """顯示使用說明"""
        help_text = """台鐵車站資訊查詢系統使用說明

主要功能：
1. 車站搜尋 - 搜尋和查看車站基本資訊
2. 客流量查詢 - 查詢特定車站的進出站人數統計
3. 車站比較 - 比較多個車站的客流量
4. 圖表視覺化 - 客流量資料的圖形化表示

操作說明：
- 使用上方分頁切換不同功能
- 查看下方狀態列了解系統狀態
- 使用選單列存取進階功能

注意事項：
- 確保資料庫連線正常
- 大量資料查詢可能需要較長時間"""

        messagebox.showinfo("使用說明", help_text)

    def show_about(self):
        """顯示關於對話框"""
        about_text = """台鐵車站資訊查詢系統 v1.0.0

這是一個基於 Python tkinter 的桌面應用程式，
用於查詢和分析台鐵車站資訊及進出站人數資料。

開發目的：
- 提供直觀的車站資訊查詢介面
- 展示 GUI 開發和資料庫整合技術
- 作為 Python 程式設計教學範例

技術架構：
- 前端：Python tkinter + ttk
- 後端：PostgreSQL + psycopg2
- 視覺化：matplotlib

© 2024 台鐵 GUI 開發團隊"""

        messagebox.showinfo("關於", about_text)

    def run_async_task(self, task: Callable, callback: Optional[Callable] = None,
                      loading_message: str = "處理中..."):
        """
        執行非同步任務（增強版錯誤處理）

        Args:
            task: 要執行的任務函數
            callback: 任務完成後的回調函數
            loading_message: 載入訊息
        """
        self.status_bar.start_loading(loading_message)

        def run_task():
            try:
                result = task()
                if callback:
                    self.root.after(0, lambda: callback(result))
                self.root.after(0, lambda: self.status_bar.stop_loading("完成"))
                self.root.after(0, lambda: self.feedback_manager.show_success("操作完成"))
            except Exception as e:
                # 使用錯誤處理器處理錯誤
                error_info = self.error_handler.handle_error(
                    e,
                    context={
                        "task": task.__name__ if hasattr(task, '__name__') else str(task),
                        "loading_message": loading_message,
                        "component": "MainWindow"
                    }
                )

                # 在主執行緒中顯示錯誤
                self.root.after(0, lambda: self.status_bar.stop_loading("操作失敗"))

                # 根據錯誤嚴重程度決定顯示方式
                if error_info.severity == ErrorSeverity.CRITICAL:
                    self.root.after(0, lambda: self.handle_critical_error(error_info))
                else:
                    self.root.after(0, lambda: self.feedback_manager.show_error(
                        error_info.user_message,
                        "操作失敗",
                        error_info.suggested_actions
                    ))

        threading.Thread(target=run_task, daemon=True).start()

    def handle_critical_error(self, error_info):
        """處理致命錯誤"""
        # 顯示詳細錯誤資訊
        self.feedback_manager.show_error_details_dialog({
            'error_id': error_info.error_id,
            'category': error_info.category.value,
            'severity': error_info.severity.value,
            'user_message': error_info.user_message,
            'technical_message': error_info.technical_message,
            'suggested_actions': error_info.suggested_actions,
            'timestamp': error_info.timestamp.isoformat(),
            'stack_trace': error_info.stack_trace
        })

        # 詢問是否重新啟動應用程式
        if self.feedback_manager.show_confirmation_dialog(
            "系統發生嚴重錯誤，建議重新啟動應用程式。\n\n是否立即重新啟動？",
            "嚴重錯誤"
        ):
            self.restart_application()

    def restart_application(self):
        """重新啟動應用程式"""
        try:
            import sys
            import os

            # 關閉當前應用程式
            self.on_closing()

            # 重新啟動
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            self.logger.error(f"重新啟動失敗: {e}")
            messagebox.showerror("重新啟動失敗", "無法自動重新啟動，請手動重新啟動應用程式")

    def get_tab_frame(self, tab_id: str) -> Optional[ttk.Frame]:
        """
        取得指定分頁的框架

        Args:
            tab_id: 分頁 ID

        Returns:
            分頁框架或 None
        """
        return self.tabs.get(tab_id)

    def switch_to_tab(self, tab_id: str):
        """
        切換到指定分頁

        Args:
            tab_id: 分頁 ID
        """
        if tab_id in self.tabs:
            tab_frame = self.tabs[tab_id]
            # 找到分頁索引
            for i in range(self.notebook.index("end")):
                if self.notebook.nametowidget(self.notebook.tabs()[i]) == tab_frame:
                    self.notebook.select(i)
                    break

    def show_error_history(self):
        """顯示錯誤歷史記錄"""
        try:
            history = self.error_handler.get_error_history(limit=50)

            if not history:
                self.feedback_manager.show_info("沒有錯誤記錄")
                return

            # 建立錯誤歷史對話框
            dialog = tk.Toplevel(self.root)
            dialog.title("錯誤歷史記錄")
            dialog.geometry("800x600")
            dialog.transient(self.root)

            # 建立樹狀檢視
            columns = ('time', 'category', 'severity', 'message')
            tree = ttk.Treeview(dialog, columns=columns, show='headings')

            # 設定標題
            tree.heading('time', text='時間')
            tree.heading('category', text='類別')
            tree.heading('severity', text='嚴重程度')
            tree.heading('message', text='訊息')

            # 設定欄位寬度
            tree.column('time', width=150)
            tree.column('category', width=100)
            tree.column('severity', width=100)
            tree.column('message', width=400)

            # 加入資料
            for error in history:
                tree.insert('', tk.END, values=(
                    error.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    error.category.value,
                    error.severity.value,
                    error.user_message[:100] + ('...' if len(error.user_message) > 100 else '')
                ))

            # 加入捲軸
            scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=tree.yview)
            tree.config(yscrollcommand=scrollbar.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # 雙擊查看詳細資訊
            def on_double_click(event):
                selection = tree.selection()
                if selection:
                    item = tree.item(selection[0])
                    index = tree.index(selection[0])
                    if index < len(history):
                        error_info = history[index]
                        self.feedback_manager.show_error_details_dialog({
                            'error_id': error_info.error_id,
                            'category': error_info.category.value,
                            'severity': error_info.severity.value,
                            'user_message': error_info.user_message,
                            'technical_message': error_info.technical_message,
                            'suggested_actions': error_info.suggested_actions,
                            'timestamp': error_info.timestamp.isoformat(),
                            'stack_trace': error_info.stack_trace
                        })

            tree.bind('<Double-1>', on_double_click)

        except Exception as e:
            self.logger.error(f"顯示錯誤歷史失敗: {e}")
            messagebox.showerror("錯誤", f"無法顯示錯誤歷史: {e}")

    def show_error_statistics(self):
        """顯示錯誤統計"""
        try:
            stats = self.error_handler.get_error_statistics()

            stats_text = f"""錯誤統計資訊

總錯誤數: {stats['total']}

按類別統計:
• 資料庫錯誤: {stats['by_category'].get('database', 0)}
• 驗證錯誤: {stats['by_category'].get('validation', 0)}
• 檔案 I/O 錯誤: {stats['by_category'].get('file_io', 0)}
• GUI 錯誤: {stats['by_category'].get('gui', 0)}
• 網路錯誤: {stats['by_category'].get('network', 0)}
• 系統錯誤: {stats['by_category'].get('system', 0)}
• 未知錯誤: {stats['by_category'].get('unknown', 0)}

按嚴重程度統計:
• 輕微: {stats['by_severity'].get('low', 0)}
• 中等: {stats['by_severity'].get('medium', 0)}
• 嚴重: {stats['by_severity'].get('high', 0)}
• 致命: {stats['by_severity'].get('critical', 0)}"""

            messagebox.showinfo("錯誤統計", stats_text)

        except Exception as e:
            self.logger.error(f"顯示錯誤統計失敗: {e}")
            messagebox.showerror("錯誤", f"無法顯示錯誤統計: {e}")

    def clear_error_history(self):
        """清除錯誤歷史記錄"""
        try:
            if self.feedback_manager.show_confirmation_dialog(
                "確定要清除所有錯誤歷史記錄嗎？",
                "確認清除"
            ):
                self.error_handler.clear_error_history()
                self.feedback_manager.show_success("錯誤歷史記錄已清除")

        except Exception as e:
            self.logger.error(f"清除錯誤歷史失敗: {e}")
            messagebox.showerror("錯誤", f"無法清除錯誤歷史: {e}")

    def on_closing(self):
        """視窗關閉事件處理"""
        try:
            # 停止效能監控
            if hasattr(self, 'memory_manager'):
                stop_memory_monitoring()

            # 關閉非同步管理器
            if hasattr(self, 'async_manager'):
                self.async_manager.shutdown(wait=False)

            # 清除快取
            if hasattr(self, 'cache_manager'):
                self.cache_manager.clear()

            # 清除所有通知和對話框
            if hasattr(self, 'feedback_manager'):
                self.feedback_manager.clear_all_notifications()
                self.feedback_manager.close_all_dialogs()

            # 關閉資料庫連線
            if hasattr(self, 'db_manager'):
                self.db_manager.close_connection()

            self.logger.info("應用程式正常關閉")
            self.root.destroy()

        except Exception as e:
            self.logger.error(f"關閉應用程式時發生錯誤: {e}")
            # 使用錯誤處理器處理關閉錯誤
            if hasattr(self, 'error_handler'):
                self.error_handler.handle_error(
                    e,
                    context={"action": "application_closing"},
                    category=ErrorCategory.SYSTEM
                )
            self.root.destroy()

    def run(self):
        """執行應用程式主迴圈"""
        try:
            self.logger.info("啟動應用程式主迴圈")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"應用程式執行錯誤: {e}")
            raise


def create_main_window() -> MainWindow:
    """建立主視窗實例"""
    return MainWindow()