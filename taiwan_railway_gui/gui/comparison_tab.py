"""
車站比較分頁

實作多個車站的客流量比較和排名功能。
"""

import tkinter as tk
from tkinter import ttk
import logging
from datetime import date, timedelta
from typing import List, Optional
from taiwan_railway_gui.gui.base_tab import BaseTab
from taiwan_railway_gui.gui.passenger_flow_tab import DatePicker
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import StationStatistics, ComparisonResult
from taiwan_railway_gui.dao.station_dao import create_station_dao
from taiwan_railway_gui.dao.passenger_flow_dao import create_passenger_flow_dao
from taiwan_railway_gui.utils.gui_helpers import create_tooltip, format_number
from taiwan_railway_gui.config import get_config


class StationSelector:
    """車站選擇器元件"""

    def __init__(self, parent: tk.Widget, stations: List[Station], max_selections: int = 5):
        """
        初始化車站選擇器

        Args:
            parent: 父元件
            stations: 可選車站列表
            max_selections: 最大選擇數量
        """
        self.parent = parent
        self.stations = stations
        self.max_selections = max_selections
        self.selected_stations = []

        # 建立主框架
        self.frame = ttk.Frame(parent)

        # 建立選擇區域
        self.create_selection_area()

        # 建立已選車站區域
        self.create_selected_area()

    def create_selection_area(self):
        """建立車站選擇區域"""
        # 選擇標籤
        select_label = ttk.Label(self.frame, text="選擇車站:")
        select_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))

        # 車站清單框
        list_frame = ttk.Frame(self.frame)
        list_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=(0, 10))

        self.station_listbox = tk.Listbox(list_frame, height=8, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.station_listbox.yview)
        self.station_listbox.config(yscrollcommand=scrollbar.set)

        self.station_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 載入車站清單
        self.load_stations()

        # 操作按鈕
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=2, column=0, pady=(5, 0))

        self.add_button = ttk.Button(
            button_frame,
            text="加入 →",
            command=self.add_station,
            width=10
        )
        self.add_button.pack(side=tk.LEFT, padx=(0, 5))

        self.remove_button = ttk.Button(
            button_frame,
            text="← 移除",
            command=self.remove_station,
            width=10
        )
        self.remove_button.pack(side=tk.LEFT)

        # 綁定雙擊事件
        self.station_listbox.bind('<Double-Button-1>', lambda e: self.add_station())

        # 加入工具提示
        create_tooltip(self.station_listbox, "雙擊或點選「加入」按鈕選擇車站")
        create_tooltip(self.add_button, "將選中的車站加入比較清單")
        create_tooltip(self.remove_button, "從比較清單中移除選中的車站")

    def create_selected_area(self):
        """建立已選車站區域"""
        # 已選標籤
        selected_label = ttk.Label(self.frame, text="已選車站:")
        selected_label.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))

        # 已選車站清單框
        selected_frame = ttk.Frame(self.frame)
        selected_frame.grid(row=1, column=1, sticky=tk.NSEW)

        self.selected_listbox = tk.Listbox(selected_frame, height=8, selectmode=tk.SINGLE)
        selected_scrollbar = ttk.Scrollbar(selected_frame, orient=tk.VERTICAL, command=self.selected_listbox.yview)
        self.selected_listbox.config(yscrollcommand=selected_scrollbar.set)

        self.selected_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        selected_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 狀態標籤
        self.status_var = tk.StringVar(value="已選 0/5 個車站")
        self.status_label = ttk.Label(self.frame, textvariable=self.status_var)
        self.status_label.grid(row=2, column=1, pady=(5, 0))

        # 綁定雙擊事件
        self.selected_listbox.bind('<Double-Button-1>', lambda e: self.remove_station())

        # 加入工具提示
        create_tooltip(self.selected_listbox, "雙擊或點選「移除」按鈕移除車站")

        # 設定網格權重
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)

    def load_stations(self):
        """載入車站清單"""
        self.station_listbox.delete(0, tk.END)
        for station in self.stations:
            display_text = f"{station.station_name} ({station.station_code})"
            self.station_listbox.insert(tk.END, display_text)

    def add_station(self):
        """加入車站到比較清單"""
        selection = self.station_listbox.curselection()
        if not selection:
            return

        # 檢查是否已達最大選擇數量
        if len(self.selected_stations) >= self.max_selections:
            tk.messagebox.showwarning("選擇限制", f"最多只能選擇 {self.max_selections} 個車站進行比較")
            return

        index = selection[0]
        if 0 <= index < len(self.stations):
            station = self.stations[index]

            # 檢查是否已選擇
            if station.station_code not in [s.station_code for s in self.selected_stations]:
                self.selected_stations.append(station)
                self.update_selected_display()

    def remove_station(self):
        """從比較清單移除車站"""
        selection = self.selected_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if 0 <= index < len(self.selected_stations):
            self.selected_stations.pop(index)
            self.update_selected_display()

    def update_selected_display(self):
        """更新已選車站顯示"""
        self.selected_listbox.delete(0, tk.END)
        for station in self.selected_stations:
            display_text = f"{station.station_name} ({station.station_code})"
            self.selected_listbox.insert(tk.END, display_text)
        # 更新狀態
        count = len(self.selected_stations)
        self.status_var.set(f"已選 {count}/{self.max_selections} 個車站")

        # 更新按鈕狀態
        self.add_button.config(state=tk.NORMAL if count < self.max_selections else tk.DISABLED)

    def get_selected_stations(self) -> List[Station]:
        """取得已選車站列表"""
        return self.selected_stations.copy()

    def clear_selection(self):
        """清除所有選擇"""
        self.selected_stations.clear()
        self.update_selected_display()

    def pack(self, **kwargs):
        """打包元件"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """網格佈局"""
        self.frame.grid(**kwargs)


class ComparisonTab(BaseTab):
    """
    車站比較分頁實作

    提供多個車站的客流量比較和排名功能。
    """

    def __init__(self, parent: tk.Widget, main_window=None):
        """
        初始化車站比較分頁

        Args:
            parent: 父元件
            main_window: 主視窗參考
        """
        # 初始化 DAO
        self.station_dao = create_station_dao()
        self.passenger_flow_dao = create_passenger_flow_dao()

        # 比較相關變數
        self.stations_list = []
        self.comparison_result = None
        self.max_stations = get_config('constants')['max_comparison_stations']

        # 呼叫父類別初始化
        super().__init__(parent, main_window)

    def setup_ui(self):
        """設定使用者介面"""
        # 建立主要區域
        self.create_selection_section()
        self.create_query_section()
        self.create_results_section()

        # 載入車站清單
        self.load_stations()

    def create_selection_section(self):
        """建立車站選擇區域"""
        selection_frame = self.create_section_frame(self.frame, "車站選擇")
        selection_frame.pack(fill=tk.BOTH, expand=True, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立車站選擇器（稍後初始化）
        self.station_selector = None

    def create_query_section(self):
        """建立查詢區域"""
        query_frame = self.create_section_frame(self.frame, "比較設定")
        query_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立輸入區域
        input_frame = self.create_input_frame(query_frame)

        # 日期範圍選擇
        date_frame = ttk.Frame(input_frame)
        date_frame.pack(fill=tk.X, pady=(0, 10))

        # 開始日期
        self.start_date_picker = DatePicker(
            date_frame,
            "開始日期:",
            date.today() - timedelta(days=30)
        )
        self.start_date_picker.pack(side=tk.LEFT, padx=(0, 20))

        # 結束日期
        self.end_date_picker = DatePicker(
            date_frame,
            "結束日期:",
            date.today()
        )
        self.end_date_picker.pack(side=tk.LEFT)

        # 建立按鈕區域
        button_frame = self.create_button_frame(query_frame)

        # 比較按鈕
        self.compare_button = ttk.Button(
            button_frame,
            text="開始比較",
            command=self.perform_comparison,
            width=self.layout['button_width']
        )
        self.compare_button.pack(side=tk.LEFT, padx=(0, 10))

        # 清除按鈕
        self.clear_button = ttk.Button(
            button_frame,
            text="清除結果",
            command=self.clear_results,
            width=self.layout['button_width']
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))

        # 匯出按鈕
        self.export_button = ttk.Button(
            button_frame,
            text="匯出",
            command=self.export_data,
            width=self.layout['button_width'],
            state=tk.DISABLED
        )
        self.export_button.pack(side=tk.LEFT)

        # 加入工具提示
        create_tooltip(self.compare_button, "比較選中車站的客流量資料")
        create_tooltip(self.clear_button, "清除比較結果")
        create_tooltip(self.export_button, "匯出比較結果到 CSV 檔案")

    def create_results_section(self):
        """建立結果顯示區域"""
        results_frame = self.create_section_frame(self.frame, "比較結果")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立結果表格
        columns = ('rank', 'station_name', 'total_in', 'total_out', 'total_passengers', 'average_daily', 'net_flow')
        headings = ['排名', '車站名稱', '總進站', '總出站', '總客流量', '平均每日', '淨流量']

        self.results_tree, self.results_scrollbar = self.create_treeview_with_scrollbar(
            results_frame, columns, headings
        )

        # 設定欄位寬度
        self.results_tree.column('rank', width=60, anchor=tk.CENTER)
        self.results_tree.column('station_name', width=120, anchor=tk.W)
        self.results_tree.column('total_in', width=100, anchor=tk.E)
        self.results_tree.column('total_out', width=100, anchor=tk.E)
        self.results_tree.column('total_passengers', width=100, anchor=tk.E)
        self.results_tree.column('average_daily', width=100, anchor=tk.E)
        self.results_tree.column('net_flow', width=100, anchor=tk.E)

        # 綁定排序事件
        for col in columns:
            self.results_tree.heading(col, command=lambda c=col: self.sort_results(c))

        # 建立排名說明
        ranking_frame = ttk.Frame(results_frame)
        ranking_frame.pack(fill=tk.X, pady=(5, 0))

        self.ranking_info_var = tk.StringVar(value="")
        self.ranking_info_label = ttk.Label(
            ranking_frame,
            textvariable=self.ranking_info_var,
            font=self.fonts['body']
        )
        self.ranking_info_label.pack(anchor=tk.W)

        # 加入工具提示
        create_tooltip(self.results_tree, "點選欄位標題可排序資料")

    def load_stations(self):
        """載入車站清單"""
        def load_task():
            try:
                return self.station_dao.get_all_stations()
            except Exception as e:
                self.logger.error(f"載入車站清單失敗: {e}")
                raise

        def load_callback(stations):
            self.stations_list = stations

            # 建立車站選擇器
            if hasattr(self, 'station_selector') and self.station_selector:
                # 更新現有選擇器
                self.station_selector.stations = stations
                self.station_selector.load_stations()
            else:
                # 建立新的選擇器
                selection_frame = self.frame.winfo_children()[0]  # 第一個子元件是選擇區域
                self.station_selector = StationSelector(
                    selection_frame,
                    stations,
                    self.max_stations
                )
                self.station_selector.pack(fill=tk.BOTH, expand=True, padx=self.layout['padding'], pady=self.layout['padding'])

            self.show_info_message("載入完成", f"已載入 {len(stations)} 個車站")

        self.run_async_task(load_task, load_callback, "載入車站清單")

    def perform_comparison(self):
        """執行比較"""
        # 驗證選擇的車站
        selected_stations = self.station_selector.get_selected_stations()
        if len(selected_stations) < 2:
            self.show_warning_message("選擇錯誤", "請至少選擇 2 個車站進行比較")
            return

        # 驗證日期範圍
        start_date = self.start_date_picker.get_date()
        end_date = self.end_date_picker.get_date()

        is_valid, error_msg = self.validate_input(
            (start_date, end_date), 'validate_date_range'
        )
        if not is_valid:
            self.show_error_message("日期錯誤", error_msg)
            return

        def comparison_task():
            try:
                # 取得車站代碼列表
                station_codes = [station.station_code for station in selected_stations]

                # 查詢多個車站的統計資料
                statistics_list = self.passenger_flow_dao.get_multiple_station_statistics(
                    station_codes, start_date, end_date
                )

                # 建立比較結果
                if statistics_list:
                    comparison_result = ComparisonResult(statistics_list, [])
                    return comparison_result
                else:
                    return None

            except Exception as e:
                self.logger.error(f"比較車站失敗: {e}")
                raise

        def comparison_callback(result):
            self.comparison_result = result

            if result and result.stations:
                self.update_results_display()
                self.export_button.config(state=tk.NORMAL)

                station_count = len(result.stations)
                self.show_info_message("比較完成", f"已比較 {station_count} 個車站")
            else:
                self.clear_results()
                self.show_info_message("比較結果", "查詢期間內沒有找到資料")

        # 執行非同步比較
        station_names = [s.station_name for s in selected_stations]
        loading_msg = f"比較 {len(selected_stations)} 個車站"
        self.run_async_task(comparison_task, comparison_callback, loading_msg)

    def update_results_display(self):
        """更新結果顯示"""
        # 清除現有結果
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        if not self.comparison_result or not self.comparison_result.stations:
            return

        # 加入比較結果
        for rank, (station_name, total_passengers) in enumerate(self.comparison_result.ranking, 1):
            # 找到對應的統計資料
            station_stats = None
            for stats in self.comparison_result.stations:
                if stats.station_name == station_name:
                    station_stats = stats
                    break

            if station_stats:
                values = (
                    rank,
                    station_name,
                    format_number(station_stats.total_in),
                    format_number(station_stats.total_out),
                    format_number(station_stats.total_passengers),
                    f"{station_stats.average_daily:,.1f}",
                    format_number(station_stats.net_flow)
                )

                # 根據排名設定標籤
                tags = []
                if rank == 1:
                    tags = ['rank1']
                elif rank == 2:
                    tags = ['rank2']
                elif rank == 3:
                    tags = ['rank3']

                self.results_tree.insert('', tk.END, values=values, tags=tags)

        # 設定排名顏色
        self.results_tree.tag_configure('rank1', background='#FFD700')  # 金色
        self.results_tree.tag_configure('rank2', background='#C0C0C0')  # 銀色
        self.results_tree.tag_configure('rank3', background='#CD7F32')  # 銅色

        # 更新排名資訊
        if self.comparison_result.ranking:
            top_station = self.comparison_result.ranking[0]
            total_all = self.comparison_result.total_passengers_all
            info_text = f"排名第一: {top_station[0]} ({format_number(top_station[1])} 人次)，總計: {format_number(total_all)} 人次"
            self.ranking_info_var.set(info_text)

    def sort_results(self, column: str):
        """排序結果"""
        if not self.comparison_result or not self.comparison_result.stations:
            return

        # 根據欄位排序
        reverse = getattr(self, f'_sort_{column}_reverse', False)

        if column == 'rank':
            # 按排名排序（實際上是按總客流量）
            self.comparison_result.stations.sort(key=lambda x: x.total_passengers, reverse=not reverse)
        elif column == 'station_name':
            self.comparison_result.stations.sort(key=lambda x: x.station_name, reverse=reverse)
        elif column == 'total_in':
            self.comparison_result.stations.sort(key=lambda x: x.total_in, reverse=reverse)
        elif column == 'total_out':
            self.comparison_result.stations.sort(key=lambda x: x.total_out, reverse=reverse)
        elif column == 'total_passengers':
            self.comparison_result.stations.sort(key=lambda x: x.total_passengers, reverse=reverse)
        elif column == 'average_daily':
            self.comparison_result.stations.sort(key=lambda x: x.average_daily, reverse=reverse)
        elif column == 'net_flow':
            self.comparison_result.stations.sort(key=lambda x: x.net_flow, reverse=reverse)

        # 更新排名
        self.comparison_result._update_ranking()

        # 切換排序方向
        setattr(self, f'_sort_{column}_reverse', not reverse)

        # 更新顯示
        self.update_results_display()

        self.logger.info(f"結果已按 {column} {'降序' if reverse else '升序'} 排序")

    def clear_results(self):
        """清除結果"""
        # 清除資料
        self.comparison_result = None

        # 清除顯示
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        self.ranking_info_var.set("")

        # 停用匯出按鈕
        self.export_button.config(state=tk.DISABLED)

        self.logger.info("比較結果已清除")

    def export_data(self):
        """匯出資料"""
        if not self.comparison_result or not self.comparison_result.stations:
            self.show_warning_message("匯出", "沒有可匯出的資料")
            return

        try:
            from taiwan_railway_gui.services.export_manager import get_export_manager

            # 使用匯出管理器匯出比較結果
            export_manager = get_export_manager()
            default_filename = f"車站比較_{date.today().strftime('%Y%m%d')}.csv"

            success = export_manager.export_comparison_result(
                parent=self.frame,
                comparison_result=self.comparison_result,
                default_filename=default_filename
            )

            if success:
                self.logger.info(f"成功匯出 {len(self.comparison_result.stations)} 個車站的比較資料")

        except Exception as e:
            self.logger.error(f"匯出比較資料失敗: {e}")
            self.show_error_message("匯出失敗", f"無法匯出比較資料: {e}")

    def refresh_data(self):
        """重新整理資料"""
        # 重新載入車站清單
        self.load_stations()

        # 如果有比較結果，重新執行比較
        if self.comparison_result:
            self.perform_comparison()


def create_comparison_tab(parent: tk.Widget, main_window=None) -> ComparisonTab:
    """建立車站比較分頁實例"""
    return ComparisonTab(parent, main_window)