#!/usr/bin/env python3
"""
客流量查詢 GUI 測試腳本

專門測試客流量查詢分頁的功能
"""

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from datetime import datetime, date, timedelta

# 設定專案路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from taiwan_railway_gui.dao.station_dao import create_station_dao
from taiwan_railway_gui.dao.passenger_flow_dao import create_passenger_flow_dao
from taiwan_railway_gui.utils.gui_helpers import format_number


class SimplePassengerFlowTest:
    """簡化的客流量查詢測試"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("客流量查詢測試")
        self.root.geometry("800x600")

        # 初始化 DAO
        self.station_dao = create_station_dao()
        self.passenger_flow_dao = create_passenger_flow_dao()

        # 載入車站資料
        self.stations = []
        self.load_stations()

        self.setup_ui()

    def load_stations(self):
        """載入車站資料"""
        try:
            self.stations = self.station_dao.get_all_stations()
            print(f"載入了 {len(self.stations)} 個車站")
        except Exception as e:
            print(f"載入車站失敗: {e}")

    def setup_ui(self):
        """設定使用者介面"""
        # 車站選擇
        station_frame = ttk.Frame(self.root)
        station_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(station_frame, text="選擇車站:").pack(side=tk.LEFT)

        self.station_var = tk.StringVar()
        self.station_combo = ttk.Combobox(station_frame, textvariable=self.station_var, width=30)
        self.station_combo.pack(side=tk.LEFT, padx=10)

        # 填充車站選項
        if self.stations:
            station_options = [f"{s.station_name} ({s.station_code})" for s in self.stations]
            self.station_combo['values'] = station_options
            self.station_combo.set(station_options[0])  # 預設選擇第一個

        # 日期選擇
        date_frame = ttk.Frame(self.root)
        date_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(date_frame, text="開始日期:").pack(side=tk.LEFT)
        self.start_date_var = tk.StringVar(value="2025-07-21")
        ttk.Entry(date_frame, textvariable=self.start_date_var, width=12).pack(side=tk.LEFT, padx=5)

        ttk.Label(date_frame, text="結束日期:").pack(side=tk.LEFT, padx=(20, 0))
        self.end_date_var = tk.StringVar(value="2025-07-27")
        ttk.Entry(date_frame, textvariable=self.end_date_var, width=12).pack(side=tk.LEFT, padx=5)

        # 查詢按鈕
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="查詢", command=self.perform_query).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="清除", command=self.clear_results).pack(side=tk.LEFT, padx=10)

        # 結果顯示
        result_frame = ttk.Frame(self.root)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 建立表格
        columns = ('date', 'in_passengers', 'out_passengers', 'total_passengers')
        self.tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=15)

        # 設定標題
        self.tree.heading('date', text='日期')
        self.tree.heading('in_passengers', text='進站人數')
        self.tree.heading('out_passengers', text='出站人數')
        self.tree.heading('total_passengers', text='總人數')

        # 設定欄位寬度
        self.tree.column('date', width=100, anchor=tk.CENTER)
        self.tree.column('in_passengers', width=120, anchor=tk.E)
        self.tree.column('out_passengers', width=120, anchor=tk.E)
        self.tree.column('total_passengers', width=120, anchor=tk.E)

        # 捲軸
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 狀態列
        self.status_var = tk.StringVar(value="就緒")
        status_label = ttk.Label(self.root, textvariable=self.status_var)
        status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def get_selected_station_code(self):
        """取得選中的車站代碼"""
        selection = self.station_var.get()
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

    def perform_query(self):
        """執行查詢"""
        try:
            # 取得選中的車站
            station_code = self.get_selected_station_code()
            if not station_code:
                self.status_var.set("錯誤: 請選擇車站")
                return

            # 取得日期範圍
            try:
                start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d").date()
                end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d").date()
            except ValueError:
                self.status_var.set("錯誤: 日期格式不正確 (應為 YYYY-MM-DD)")
                return

            if start_date > end_date:
                self.status_var.set("錯誤: 開始日期不能晚於結束日期")
                return

            self.status_var.set("查詢中...")
            self.root.update()

            # 執行查詢
            flows = self.passenger_flow_dao.get_passenger_flow(station_code, start_date, end_date)

            # 清除現有結果
            for item in self.tree.get_children():
                self.tree.delete(item)

            # 顯示結果
            if flows:
                for flow in flows:
                    values = (
                        flow.date_str if hasattr(flow, 'date_str') else str(flow.date),
                        format_number(flow.in_passengers),
                        format_number(flow.out_passengers),
                        format_number(flow.total_passengers)
                    )
                    self.tree.insert('', tk.END, values=values)

                self.status_var.set(f"查詢完成，找到 {len(flows)} 筆記錄")
            else:
                self.status_var.set("查詢完成，沒有找到資料")

            # 取得統計資料
            stats = self.passenger_flow_dao.get_station_statistics(station_code, start_date, end_date)
            if stats:
                print(f"統計資料: 總人數 {stats.total_passengers:,}, 平均每日 {stats.average_daily:.1f}")

        except Exception as e:
            self.status_var.set(f"查詢失敗: {e}")
            print(f"查詢錯誤: {e}")
            import traceback
            traceback.print_exc()

    def clear_results(self):
        """清除結果"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_var.set("已清除結果")

    def run(self):
        """執行應用程式"""
        self.root.mainloop()


def main():
    """主函數"""
    print("🚀 啟動客流量查詢 GUI 測試")

    try:
        app = SimplePassengerFlowTest()
        app.run()
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()