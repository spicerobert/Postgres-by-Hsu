"""
車站搜尋分頁

實作車站搜尋和詳細資訊顯示功能。
"""

import tkinter as tk
from tkinter import ttk
import logging
from datetime import date
from typing import List, Optional
from taiwan_railway_gui.gui.base_tab import BaseTab
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.dao.station_dao import create_station_dao
from taiwan_railway_gui.utils.gui_helpers import create_tooltip, format_number


class StationSearchTab(BaseTab):
    """
    車站搜尋分頁實作

    提供車站搜尋、結果顯示和詳細資訊查看功能。
    """

    def __init__(self, parent: tk.Widget, main_window=None):
        """
        初始化車站搜尋分頁

        Args:
            parent: 父元件
            main_window: 主視窗參考
        """
        # 初始化 DAO
        self.station_dao = create_station_dao()

        # 搜尋相關變數
        self.search_results = []
        self.selected_station = None
        self.search_delay_timer = None

        # 呼叫父類別初始化
        super().__init__(parent, main_window)

    def setup_ui(self):
        """設定使用者介面"""
        # 建立主要區域
        self.create_search_section()
        self.create_results_section()
        self.create_details_section()

        # 初始載入所有車站（限制數量）
        self.load_initial_stations()

    def create_search_section(self):
        """建立搜尋區域"""
        search_frame = self.create_section_frame(self.frame, "車站搜尋")
        search_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立輸入區域
        input_frame = self.create_input_frame(search_frame)

        # 搜尋標籤和輸入框
        self.search_label, self.search_entry = self.create_labeled_entry(
            input_frame, "搜尋車站（名稱或代碼）:", self.layout['entry_width']
        )

        self.search_label.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        # 綁定即時搜尋事件
        self.search_entry.bind('<KeyRelease>', self.on_search_changed)
        self.search_entry.bind('<Return>', self.perform_search)

        # 建立按鈕區域
        button_frame = self.create_button_frame(search_frame)

        # 搜尋按鈕
        self.search_button = ttk.Button(
            button_frame,
            text="搜尋",
            command=self.perform_search,
            width=self.layout['button_width']
        )
        self.search_button.pack(side=tk.LEFT, padx=(0, 10))

        # 清除按鈕
        self.clear_button = ttk.Button(
            button_frame,
            text="清除",
            command=self.clear_search,
            width=self.layout['button_width']
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))

        # 重新整理按鈕
        self.refresh_button = ttk.Button(
            button_frame,
            text="重新整理",
            command=self.refresh_data,
            width=self.layout['button_width']
        )
        self.refresh_button.pack(side=tk.LEFT)

        # 加入工具提示
        create_tooltip(self.search_entry, "輸入車站名稱或代碼進行搜尋")
        create_tooltip(self.search_button, "執行搜尋")
        create_tooltip(self.clear_button, "清除搜尋條件和結果")
        create_tooltip(self.refresh_button, "重新載入車站資料")

    def create_results_section(self):
        """建立搜尋結果區域"""
        results_frame = self.create_section_frame(self.frame, "搜尋結果")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立結果清單
        self.results_listbox, self.results_scrollbar = self.create_scrollable_listbox(
            results_frame, height=12
        )

        # 綁定選擇事件
        self.results_listbox.bind('<<ListboxSelect>>', self.on_station_selected)
        self.results_listbox.bind('<Double-Button-1>', self.on_station_double_click)

        # 建立結果統計標籤
        self.results_count_var = tk.StringVar(value="共 0 個結果")
        self.results_count_label = ttk.Label(
            results_frame,
            textvariable=self.results_count_var,
            font=self.fonts['body']
        )
        self.results_count_label.pack(anchor=tk.W, pady=(5, 0))

        # 加入工具提示
        create_tooltip(self.results_listbox, "點選車站查看詳細資訊，雙擊可快速查看")

    def create_details_section(self):
        """建立詳細資訊區域"""
        details_frame = self.create_section_frame(self.frame, "車站詳細資訊")
        details_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立詳細資訊顯示區域
        info_frame = ttk.Frame(details_frame)
        info_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立資訊標籤
        self.create_info_labels(info_frame)

        # 建立操作按鈕
        action_frame = ttk.Frame(details_frame)
        action_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=(0, self.layout['padding']))

        # 查看客流量按鈕
        self.view_flow_button = ttk.Button(
            action_frame,
            text="查看客流量",
            command=self.view_passenger_flow,
            width=self.layout['button_width'],
            state=tk.DISABLED
        )
        self.view_flow_button.pack(side=tk.LEFT, padx=(0, 10))

        # 複製資訊按鈕
        self.copy_info_button = ttk.Button(
            action_frame,
            text="複製資訊",
            command=self.copy_station_info,
            width=self.layout['button_width'],
            state=tk.DISABLED
        )
        self.copy_info_button.pack(side=tk.LEFT)

        # 加入工具提示
        create_tooltip(self.view_flow_button, "切換到客流量查詢分頁查看此車站資料")
        create_tooltip(self.copy_info_button, "複製車站資訊到剪貼簿")

    def create_info_labels(self, parent: tk.Widget):
        """建立資訊標籤"""
        # 使用網格佈局
        labels = [
            ("車站代碼:", "station_code"),
            ("車站名稱:", "station_name"),
            ("地址:", "address"),
            ("電話:", "phone"),
            ("GPS 座標:", "coordinates"),
            ("自行車租借:", "bike_rental")
        ]

        self.info_vars = {}
        self.info_labels = {}

        for i, (label_text, var_name) in enumerate(labels):
            # 標籤
            label = ttk.Label(parent, text=label_text, font=self.fonts['body'])
            label.grid(row=i, column=0, sticky=tk.W, padx=(0, 10), pady=2)

            # 值標籤
            var = tk.StringVar(value="")
            value_label = ttk.Label(parent, textvariable=var, font=self.fonts['body'])
            value_label.grid(row=i, column=1, sticky=tk.W, pady=2)

            self.info_vars[var_name] = var
            self.info_labels[var_name] = value_label

        # 設定欄位權重
        parent.columnconfigure(1, weight=1)

    def on_search_changed(self, event):
        """搜尋輸入變更事件"""
        # 取消之前的延遲搜尋
        if self.search_delay_timer:
            self.frame.after_cancel(self.search_delay_timer)

        # 設定新的延遲搜尋
        search_delay = self.main_window.gui_config.get('search_delay_ms', 300) if self.main_window else 300
        self.search_delay_timer = self.frame.after(search_delay, self.perform_search)

    def perform_search(self, event=None):
        """執行搜尋"""
        query = self.search_entry.get().strip()

        def search_task():
            try:
                if query:
                    # 執行搜尋
                    results = self.station_dao.search_stations(query)
                else:
                    # 空查詢顯示所有車站（限制數量）
                    results = self.station_dao.get_all_stations()[:50]

                return results
            except Exception as e:
                self.logger.error(f"搜尋失敗: {e}")
                raise

        def search_callback(results):
            self.search_results = results
            self.update_results_display()

            if results:
                self.show_info_message("搜尋完成", f"找到 {len(results)} 個車站")
            else:
                self.show_info_message("搜尋結果", "沒有找到匹配的車站")

        # 執行非同步搜尋
        loading_msg = f"搜尋 '{query}'" if query else "載入車站清單"
        self.run_async_task(search_task, search_callback, loading_msg)

    def update_results_display(self):
        """更新搜尋結果顯示"""
        # 清除現有結果
        self.results_listbox.delete(0, tk.END)

        # 加入新結果
        for station in self.search_results:
            display_text = f"{station.station_name} ({station.station_code})"
            self.results_listbox.insert(tk.END, display_text)

        # 更新結果統計
        count = len(self.search_results)
        self.results_count_var.set(f"共 {count} 個結果")

        # 清除詳細資訊
        self.clear_station_details()

    def on_station_selected(self, event):
        """車站選擇事件"""
        selection = self.results_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.search_results):
                self.selected_station = self.search_results[index]
                self.display_station_details(self.selected_station)

    def on_station_double_click(self, event):
        """車站雙擊事件"""
        self.on_station_selected(event)
        if self.selected_station:
            self.view_passenger_flow()

    def display_station_details(self, station: Station):
        """顯示車站詳細資訊"""
        # 更新資訊標籤
        self.info_vars['station_code'].set(station.station_code)
        self.info_vars['station_name'].set(station.station_name)
        self.info_vars['address'].set(station.address)
        self.info_vars['phone'].set(station.phone or "無")

        # 格式化座標
        coords_text = f"{station.gps_lat:.6f}, {station.gps_lng:.6f}"
        self.info_vars['coordinates'].set(coords_text)

        # 自行車租借狀態
        bike_text = "是" if station.has_bike_rental else "否"
        self.info_vars['bike_rental'].set(bike_text)

        # 啟用操作按鈕
        self.view_flow_button.config(state=tk.NORMAL)
        self.copy_info_button.config(state=tk.NORMAL)

        self.logger.info(f"顯示車站詳細資訊: {station.station_name}")

    def clear_station_details(self):
        """清除車站詳細資訊"""
        for var in self.info_vars.values():
            var.set("")

        # 停用操作按鈕
        self.view_flow_button.config(state=tk.DISABLED)
        self.copy_info_button.config(state=tk.DISABLED)

        self.selected_station = None

    def clear_search(self):
        """清除搜尋"""
        # 清除搜尋輸入
        self.search_entry.delete(0, tk.END)

        # 清除結果
        self.search_results = []
        self.update_results_display()

        # 重新載入初始車站
        self.load_initial_stations()

        self.logger.info("搜尋已清除")

    def load_initial_stations(self):
        """載入初始車站清單"""
        def load_task():
            try:
                # 載入前50個車站
                return self.station_dao.get_all_stations()[:50]
            except Exception as e:
                self.logger.error(f"載入初始車站失敗: {e}")
                raise

        def load_callback(results):
            self.search_results = results
            self.update_results_display()

        self.run_async_task(load_task, load_callback, "載入車站清單")

    def refresh_data(self):
        """重新整理資料"""
        # 清除快取
        self.station_dao.clear_cache()

        # 重新執行搜尋或載入
        query = self.search_entry.get().strip()
        if query:
            self.perform_search()
        else:
            self.load_initial_stations()

        self.logger.info("車站資料已重新整理")

    def view_passenger_flow(self):
        """查看客流量"""
        if not self.selected_station:
            self.show_warning_message("提示", "請先選擇一個車站")
            return

        if self.main_window:
            # 切換到客流量查詢分頁
            self.main_window.switch_to_tab('passenger_flow')

            # 設定選中的車站
            passenger_flow_tab = self.main_window.tabs.get('passenger_flow')
            if passenger_flow_tab and hasattr(passenger_flow_tab, 'set_selected_station'):
                passenger_flow_tab.set_selected_station(self.selected_station.station_code)

            self.show_info_message("切換分頁", f"已切換到客流量查詢，車站: {self.selected_station.station_name}")
        else:
            self.show_info_message("功能提示", "客流量查詢功能已實作")

    def copy_station_info(self):
        """複製車站資訊到剪貼簿"""
        if not self.selected_station:
            self.show_warning_message("提示", "請先選擇一個車站")
            return

        try:
            station = self.selected_station
            info_text = f"""車站資訊
車站代碼: {station.station_code}
車站名稱: {station.station_name}
地址: {station.address}
電話: {station.phone or '無'}
GPS 座標: {station.gps_lat:.6f}, {station.gps_lng:.6f}
自行車租借: {'是' if station.has_bike_rental else '否'}"""

            # 複製到剪貼簿
            self.frame.clipboard_clear()
            self.frame.clipboard_append(info_text)

            self.show_info_message("複製成功", "車站資訊已複製到剪貼簿")

        except Exception as e:
            self.logger.error(f"複製車站資訊失敗: {e}")
            self.show_error_message("複製失敗", f"無法複製車站資訊: {e}")

    def clear_results(self):
        """清除結果顯示"""
        self.search_results = []
        self.update_results_display()

    def export_data(self):
        """匯出車站資料"""
        if not self.search_results:
            self.show_warning_message("匯出", "沒有可匯出的資料")
            return

        try:
            from taiwan_railway_gui.services.export_manager import get_export_manager

            # 使用匯出管理器匯出資料
            export_manager = get_export_manager()
            success = export_manager.export_stations(
                parent=self.frame,
                stations=self.search_results,
                default_filename=f"車站搜尋結果_{date.today().strftime('%Y%m%d')}.csv"
            )

            if success:
                self.logger.info(f"成功匯出 {len(self.search_results)} 筆車站資料")

        except Exception as e:
            self.logger.error(f"匯出車站資料失敗: {e}")
            self.show_error_message("匯出失敗", f"無法匯出車站資料: {e}")


def create_station_search_tab(parent: tk.Widget, main_window=None) -> StationSearchTab:
    """建立車站搜尋分頁實例"""
    return StationSearchTab(parent, main_window)