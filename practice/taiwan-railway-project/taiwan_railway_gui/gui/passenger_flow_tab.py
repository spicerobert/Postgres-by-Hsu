"""
客流量查詢分頁

實作客流量資料查詢和統計顯示功能。
"""

import tkinter as tk
from tkinter import ttk
import logging
from datetime import date, datetime, timedelta
from typing import List, Optional
from taiwan_railway_gui.gui.base_tab import BaseTab
from taiwan_railway_gui.models.passenger_flow import PassengerFlow, StationStatistics
from taiwan_railway_gui.dao.station_dao import create_station_dao
from taiwan_railway_gui.dao.passenger_flow_dao import create_passenger_flow_dao
from taiwan_railway_gui.utils.gui_helpers import create_tooltip, format_number


class DatePicker:
    """日期選擇器元件"""

    def __init__(self, parent: tk.Widget, label_text: str, initial_date: date = None):
        """
        初始化日期選擇器

        Args:
            parent: 父元件
            label_text: 標籤文字
            initial_date: 初始日期
        """
        self.parent = parent
        self.date_value = initial_date or date.today()

        # 建立框架
        self.frame = ttk.Frame(parent)

        # 建立標籤
        self.label = ttk.Label(self.frame, text=label_text)
        self.label.pack(side=tk.LEFT, padx=(0, 5))

        # 建立日期輸入框
        self.date_var = tk.StringVar(value=self.date_value.strftime('%Y-%m-%d'))
        self.date_entry = ttk.Entry(self.frame, textvariable=self.date_var, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=(0, 5))

        # 建立日期選擇按鈕
        self.date_button = ttk.Button(self.frame, text="選擇", command=self.show_calendar, width=6)
        self.date_button.pack(side=tk.LEFT)

        # 綁定驗證事件
        self.date_entry.bind('<FocusOut>', self.validate_date)
        self.date_entry.bind('<Return>', self.validate_date)

        # 加入工具提示
        create_tooltip(self.date_entry, "格式: YYYY-MM-DD")
        create_tooltip(self.date_button, "開啟日期選擇器")

    def show_calendar(self):
        """顯示日期選擇器（簡化版）"""
        # 這裡實作一個簡單的日期輸入對話框
        from tkinter import simpledialog

        date_str = simpledialog.askstring(
            "選擇日期",
            "請輸入日期 (YYYY-MM-DD):",
itialvalue=self.date_var.get()
        )

        if date_str:
            try:
                new_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                self.set_date(new_date)
            except ValueError:
                tk.messagebox.showerror("錯誤", "日期格式不正確，請使用 YYYY-MM-DD 格式")

    def validate_date(self, event=None):
        """驗證日期格式"""
        try:
            date_str = self.date_var.get()
            new_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            self.date_value = new_date
            return True
        except ValueError:
            # 恢復到之前的有效日期
            self.date_var.set(self.date_value.strftime('%Y-%m-%d'))
            return False

    def get_date(self) -> date:
        """取得選擇的日期"""
        self.validate_date()
        return self.date_value

    def set_date(self, new_date: date):
        """設定日期"""
        self.date_value = new_date
        self.date_var.set(new_date.strftime('%Y-%m-%d'))

    def pack(self, **kwargs):
        """打包元件"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """網格佈局"""
        self.frame.grid(**kwargs)


class PassengerFlowTab(BaseTab):
    """
    客流量查詢分頁實作

    提供客流量資料查詢、統計顯示和分析功能。
    """

    def __init__(self, parent: tk.Widget, main_window=None):
        """
        初始化客流量查詢分頁

        Args:
            parent: 父元件
            main_window: 主視窗參考
        """
        # 初始化 DAO
        self.station_dao = create_station_dao()
        self.passenger_flow_dao = create_passenger_flow_dao()

        # 查詢相關變數
        self.stations_list = []
        self.current_flows = []
        self.current_statistics = None
        self.current_page = 1
        self.page_size = 50
        self.total_pages = 1
        self.use_pagination = False

        # 呼叫父類別初始化
        super().__init__(parent, main_window)

    def setup_ui(self):
        """設定使用者介面"""
        # 建立主要區域
        self.create_query_section()
        self.create_results_section()
        self.create_statistics_section()

        # 載入車站清單
        self.load_stations()

    def create_query_section(self):
        """建立查詢區域"""
        query_frame = self.create_section_frame(self.frame, "客流量查詢")
        query_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立輸入區域
        input_frame = self.create_input_frame(query_frame)

        # 車站選擇
        station_frame = ttk.Frame(input_frame)
        station_frame.pack(fill=tk.X, pady=(0, 10))

        self.station_label, self.station_combobox = self.create_labeled_combobox(
            station_frame, "選擇車站:", [], width=30
        )
        self.station_label.pack(side=tk.LEFT, padx=(0, 10))
        self.station_combobox.pack(side=tk.LEFT, padx=(0, 10))

        # 重新載入車站按鈕
        self.reload_stations_button = ttk.Button(
            station_frame,
            text="重新載入",
            command=self.load_stations,
            width=10
        )
        self.reload_stations_button.pack(side=tk.LEFT)

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

        # 查詢按鈕
        self.query_button = ttk.Button(
            button_frame,
            text="查詢",
            command=self.perform_query,
            width=self.layout['button_width']
        )
        self.query_button.pack(side=tk.LEFT, padx=(0, 10))

        # 清除按鈕
        self.clear_button = ttk.Button(
            button_frame,
            text="清除",
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
        create_tooltip(self.station_combobox, "選擇要查詢的車站")
        create_tooltip(self.query_button, "執行客流量查詢")
        create_tooltip(self.clear_button, "清除查詢結果")
        create_tooltip(self.export_button, "匯出查詢結果到 CSV 檔案")

    def create_results_section(self):
        """建立結果顯示區域"""
        results_frame = self.create_section_frame(self.frame, "查詢結果")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立結果表格
        columns = ('date', 'in_passengers', 'out_passengers', 'total_passengers', 'net_flow')
        headings = ['日期', '進站人數', '出站人數', '總人數', '淨流量']

        self.results_tree, self.results_scrollbar = self.create_treeview_with_scrollbar(
            results_frame, columns, headings
        )

        # 設定欄位寬度
        self.results_tree.column('date', width=100, anchor=tk.CENTER)
        self.results_tree.column('in_passengers', width=100, anchor=tk.E)
        self.results_tree.column('out_passengers', width=100, anchor=tk.E)
        self.results_tree.column('total_passengers', width=100, anchor=tk.E)
        self.results_tree.column('net_flow', width=100, anchor=tk.E)

        # 綁定排序事件
        for col in columns:
            self.results_tree.heading(col, command=lambda c=col: self.sort_results(c))

        # 建立結果統計和分頁控制
        control_frame = ttk.Frame(results_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))

        # 結果統計標籤
        self.results_count_var = tk.StringVar(value="共 0 筆記錄")
        self.results_count_label = ttk.Label(
            control_frame,
            textvariable=self.results_count_var,
            font=self.fonts['body']
        )
        self.results_count_label.pack(side=tk.LEFT)

        # 分頁控制
        self.pagination_frame = ttk.Frame(control_frame)
        self.pagination_frame.pack(side=tk.RIGHT)

        self.prev_button = ttk.Button(
            self.pagination_frame,
            text="上一頁",
            command=self.previous_page,
            state=tk.DISABLED,
            width=8
        )
        self.prev_button.pack(side=tk.LEFT, padx=(0, 5))

        self.page_info_var = tk.StringVar(value="")
        self.page_info_label = ttk.Label(
            self.pagination_frame,
            textvariable=self.page_info_var,
            font=self.fonts['body']
        )
        self.page_info_label.pack(side=tk.LEFT, padx=(0, 5))

        self.next_button = ttk.Button(
            self.pagination_frame,
            text="下一頁",
            command=self.next_page,
            state=tk.DISABLED,
            width=8
        )
        self.next_button.pack(side=tk.LEFT)

        # 預設隱藏分頁控制
        self.pagination_frame.pack_forget()

        # 加入工具提示
        create_tooltip(self.results_tree, "點選欄位標題可排序資料")
        create_tooltip(self.prev_button, "顯示上一頁結果")
        create_tooltip(self.next_button, "顯示下一頁結果")

    def create_statistics_section(self):
        """建立統計資訊區域"""
        stats_frame = self.create_section_frame(self.frame, "統計摘要")
        stats_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立統計資訊顯示區域
        info_frame = ttk.Frame(stats_frame)
        info_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立統計標籤
        self.create_statistics_labels(info_frame)

    def create_statistics_labels(self, parent: tk.Widget):
        """建立統計標籤"""
        # 使用網格佈局
        stats_labels = [
            ("查詢期間:", "date_range"),
            ("總進站人數:", "total_in"),
            ("總出站人數:", "total_out"),
            ("總客流量:", "total_passengers"),
            ("平均每日客流量:", "average_daily"),
            ("淨流量:", "net_flow")
        ]

        self.stats_vars = {}
        self.stats_labels = {}

        # 分兩欄顯示
        for i, (label_text, var_name) in enumerate(stats_labels):
            row = i % 3
            col = (i // 3) * 2

            # 標籤
            label = ttk.Label(parent, text=label_text, font=self.fonts['body'])
            label.grid(row=row, column=col, sticky=tk.W, padx=(0, 10), pady=2)

            # 值標籤
            var = tk.StringVar(value="")
            value_label = ttk.Label(parent, textvariable=var, font=self.fonts['body'])
            value_label.grid(row=row, column=col+1, sticky=tk.W, padx=(0, 20), pady=2)

            self.stats_vars[var_name] = var
            self.stats_labels[var_name] = value_label

        # 設定欄位權重
        for i in range(4):
            parent.columnconfigure(i, weight=1)

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

            # 更新下拉選單
            station_names = [f"{station.station_name} ({station.station_code})"
                           for station in stations]
            self.station_combobox['values'] = station_names

            if stations:
                self.station_combobox.set(station_names[0])  # 預設選擇第一個

            self.show_info_message("載入完成", f"已載入 {len(stations)} 個車站")

        self.run_async_task(load_task, load_callback, "載入車站清單")

    def get_selected_station_code(self) -> Optional[str]:
        """取得選中的車站代碼"""
        selection = self.station_combobox.get()
        if not selection:
            return None

        # 從 "車站名稱 (代碼)" 格式中提取代碼
        try:
            start = selection.rfind('(') + 1
            end = selection.rfind(')')
            if start > 0 and end > start:
                return selection[start:end]
        except:
            pass

        return None

    def set_selected_station(self, station_code: str):
        """設定選中的車站（供其他分頁呼叫）"""
        for i, station in enumerate(self.stations_list):
            if station.station_code == station_code:
                station_name = f"{station.station_name} ({station.station_code})"
                self.station_combobox.set(station_name)
                break

    def perform_query(self):
        """執行查詢"""
        # 驗證輸入
        station_code = self.get_selected_station_code()
        if not station_code:
            self.show_warning_message("輸入錯誤", "請選擇一個車站")
            return

        start_date = self.start_date_picker.get_date()
        end_date = self.end_date_picker.get_date()

        # 驗證日期範圍
        is_valid, error_msg = self.validate_input(
            (start_date, end_date), 'validate_date_range'
        )
        if not is_valid:
            self.show_error_message("日期錯誤", error_msg)
            return

        def query_task():
            try:
                # 檢查資料量大小來決定使用哪種查詢方式
                days_diff = (end_date - start_date).days + 1

                if days_diff > 365:  # 超過一年的資料使用漸進式載入
                    def progress_update(progress, message):
                        # 這裡可以更新進度條（如果有的話）
                        pass

                    flows = self.passenger_flow_dao.get_large_dataset_progressive(
                        station_code, start_date, end_date,
                        chunk_size=500, progress_callback=progress_update
                    )
                elif days_diff > 90:  # 超過三個月使用快取版本
                    flows = self.passenger_flow_dao.get_passenger_flow_cached(
                        station_code, start_date, end_date
                    )
                else:  # 小資料量使用一般查詢
                    flows = self.passenger_flow_dao.get_passenger_flow(
                        station_code, start_date, end_date
                    )

                # 查詢統計資料
                statistics = self.passenger_flow_dao.get_station_statistics(
                    station_code, start_date, end_date
                )

                return flows, statistics
            except Exception as e:
                self.logger.error(f"查詢客流量失敗: {e}")
                raise

        def query_callback(result):
            flows, statistics = result
            self.current_statistics = statistics

            # 判斷是否使用分頁
            self.use_pagination = self.should_use_pagination(start_date, end_date)

            if self.use_pagination and len(flows) > self.page_size:
                # 使用分頁模式
                self.current_page = 1

                # 重新查詢第一頁
                def first_page_task():
                    return self.passenger_flow_dao.get_passenger_flow_paginated(
                        station_code, start_date, end_date, 1, self.page_size
                    )

                def first_page_callback(page_result):
                    self.current_flows = page_result.items
                    self.total_pages = page_result.page_info.total_pages

                    self.update_results_display()
                    self.update_statistics_display()
                    self.update_pagination_controls(page_result.page_info)

                    # 顯示分頁控制
                    self.pagination_frame.pack(side=tk.RIGHT)

                    self.export_button.config(state=tk.NORMAL)
                    self.show_info_message("查詢完成", f"找到 {page_result.page_info.total_items} 筆記錄（分頁顯示）")

                self.run_async_task(first_page_task, first_page_callback, "載入第一頁")
            else:
                # 一般模式
                self.current_flows = flows
                self.current_page = 1
                self.total_pages = 1

                # 隱藏分頁控制
                self.pagination_frame.pack_forget()

                self.update_results_display()
                self.update_statistics_display()

                if flows:
                    self.export_button.config(state=tk.NORMAL)
                    self.show_info_message("查詢完成", f"找到 {len(flows)} 筆記錄")
                else:
                    self.export_button.config(state=tk.DISABLED)
                    self.show_info_message("查詢結果", "查詢期間內沒有資料")

        # 執行非同步查詢
        station_name = self.station_combobox.get().split(' (')[0]
        loading_msg = f"查詢 {station_name} 客流量資料"
        self.run_async_task(query_task, query_callback, loading_msg)

    def update_results_display(self):
        """更新結果顯示"""
        # 清除現有結果
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # 加入新結果
        for flow in self.current_flows:
            values = (
                flow.date_str,
                format_number(flow.in_passengers),
                format_number(flow.out_passengers),
                format_number(flow.total_passengers),
                format_number(flow.net_flow)
            )
            self.results_tree.insert('', tk.END, values=values)

        # 更新結果統計
        count = len(self.current_flows)
        self.results_count_var.set(f"共 {count} 筆記錄")

    def update_statistics_display(self):
        """更新統計顯示"""
        if self.current_statistics:
            stats = self.current_statistics

            # 更新統計標籤
            self.stats_vars['date_range'].set(stats.date_range_str)
            self.stats_vars['total_in'].set(format_number(stats.total_in))
            self.stats_vars['total_out'].set(format_number(stats.total_out))
            self.stats_vars['total_passengers'].set(format_number(stats.total_passengers))
            self.stats_vars['average_daily'].set(f"{stats.average_daily:,.1f}")
            self.stats_vars['net_flow'].set(format_number(stats.net_flow))
        else:
            # 清除統計資訊
            for var in self.stats_vars.values():
                var.set("")

    def sort_results(self, column: str):
        """排序結果"""
        if not self.current_flows:
            return

        # 根據欄位排序
        reverse = getattr(self, f'_sort_{column}_reverse', False)

        if column == 'date':
            self.current_flows.sort(key=lambda x: x.date, reverse=reverse)
        elif column == 'in_passengers':
            self.current_flows.sort(key=lambda x: x.in_passengers, reverse=reverse)
        elif column == 'out_passengers':
            self.current_flows.sort(key=lambda x: x.out_passengers, reverse=reverse)
        elif column == 'total_passengers':
            self.current_flows.sort(key=lambda x: x.total_passengers, reverse=reverse)
        elif column == 'net_flow':
            self.current_flows.sort(key=lambda x: x.net_flow, reverse=reverse)

        # 切換排序方向
        setattr(self, f'_sort_{column}_reverse', not reverse)

        # 更新顯示
        self.update_results_display()

        self.logger.info(f"結果已按 {column} {'降序' if reverse else '升序'} 排序")

    def clear_results(self):
        """清除結果"""
        # 清除資料
        self.current_flows = []
        self.current_statistics = None

        # 更新顯示
        self.update_results_display()
        self.update_statistics_display()

        # 停用匯出按鈕
        self.export_button.config(state=tk.DISABLED)

        self.logger.info("查詢結果已清除")

    def export_data(self):
        """匯出資料"""
        if not self.current_flows:
            self.show_warning_message("匯出", "沒有可匯出的資料")
            return

        try:
            from taiwan_railway_gui.services.export_manager import get_export_manager

            # 使用匯出管理器匯出客流量資料
            export_manager = get_export_manager()
            station_name = self.station_combobox.get().split(' (')[0]
            default_filename = f"{station_name}_客流量_{date.today().strftime('%Y%m%d')}.csv"

            success = export_manager.export_passenger_flows(
                parent=self.frame,
                flows=self.current_flows,
                default_filename=default_filename
            )

            if success:
                self.logger.info(f"成功匯出 {len(self.current_flows)} 筆客流量資料")

        except Exception as e:
            self.logger.error(f"匯出客流量資料失敗: {e}")
            self.show_error_message("匯出失敗", f"無法匯出客流量資料: {e}")

    def previous_page(self):
        """上一頁"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_current_page()

    def next_page(self):
        """下一頁"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_current_page()

    def load_current_page(self):
        """載入當前頁面"""
        if not self.use_pagination:
            return

        station_code = self.get_selected_station_code()
        if not station_code:
            return

        start_date = self.start_date_picker.get_date()
        end_date = self.end_date_picker.get_date()

        def page_query_task():
            try:
                page_result = self.passenger_flow_dao.get_passenger_flow_paginated(
                    station_code, start_date, end_date, self.current_page, self.page_size
                )
                return page_result
            except Exception as e:
                self.logger.error(f"載入頁面失敗: {e}")
                raise

        def page_query_callback(page_result):
            self.current_flows = page_result.items
            self.total_pages = page_result.page_info.total_pages

            self.update_results_display()
            self.update_pagination_controls(page_result.page_info)

        self.run_async_task(page_query_task, page_query_callback, f"載入第 {self.current_page} 頁")

    def update_pagination_controls(self, page_info):
        """更新分頁控制"""
        # 更新按鈕狀態
        self.prev_button.config(state=tk.NORMAL if page_info.has_previous else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if page_info.has_next else tk.DISABLED)

        # 更新頁面資訊
        self.page_info_var.set(f"第 {page_info.current_page}/{page_info.total_pages} 頁")

        # 更新結果統計
        start_idx = page_info.start_index + 1
        end_idx = page_info.end_index
        total = page_info.total_items
        self.results_count_var.set(f"顯示 {start_idx}-{end_idx} / 共 {total} 筆記錄")

    def should_use_pagination(self, start_date, end_date) -> bool:
        """判斷是否應該使用分頁"""
        days_diff = (end_date - start_date).days + 1
        return days_diff > 31  # 超過一個月的資料使用分頁

    def refresh_data(self):
        """重新整理資料"""
        # 清除快取
        self.passenger_flow_dao.clear_cache()

        # 重新載入車站清單
        self.load_stations()

        # 如果有查詢結果，重新執行查詢
        if self.current_flows:
            self.perform_query()


def create_passenger_flow_tab(parent: tk.Widget, main_window=None) -> PassengerFlowTab:
    """建立客流量查詢分頁實例"""
    return PassengerFlowTab(parent, main_window)