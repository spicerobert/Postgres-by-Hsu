#!/usr/bin/env python3
"""
客流量查詢 GUI 測試腳本

測試客流量查詢分頁的功能。
"""

import sys
import os
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
import tkinter as tk
from taiwan_railway_gui.gui.passenger_flow_tab import create_passenger_flow_tab
from taiwan_railway_gui.config import get_config

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_passenger_flow_tab():
    """測試客流量查詢分頁"""
    print("=== 測試客流量查詢分頁 ===")

    try:
        # 建立測試視窗
        root = tk.Tk()
        root.title("客流量查詢功能測試")
        root.geometry("1000x700")

        # 建立客流量查詢分頁
        print("建立客流量查詢分頁...")
        passenger_flow_tab = create_passenger_flow_tab(root)
        print("✅ 客流量查詢分頁建立成功")

        # 檢查基本元件
        components = [
            ('車站選擇下拉選單', 'station_combobox'),
            ('開始日期選擇器', 'start_date_picker'),
            ('結束日期選擇器', 'end_date_picker'),
            ('查詢按鈕', 'query_button'),
            ('清除按鈕', 'clear_button'),
            ('匯出按鈕', 'export_button'),
            ('結果樹狀檢視', 'results_tree'),
            ('統計變數', 'stats_vars')
        ]

        for name, attr in components:
            if hasattr(passenger_flow_tab, attr):
                print(f"✅ {name} 存在")
            else:
                print(f"❌ {name} 不存在")

        # 檢查 DAO 連線
        dao_components = [
            ('車站 DAO', 'station_dao'),
            ('客流量 DAO', 'passenger_flow_dao')
        ]

        for name, attr in dao_components:
            if hasattr(passenger_flow_tab, attr):
                print(f"✅ {name} 已初始化")
            else:
                print(f"❌ {name} 未初始化")

        # 檢查日期選擇器
        if hasattr(passenger_flow_tab, 'start_date_picker'):
            start_date = passenger_flow_tab.start_date_picker.get_date()
            print(f"✅ 開始日期: {start_date}")

        if hasattr(passenger_flow_tab, 'end_date_picker'):
            end_date = passenger_flow_tab.end_date_picker.get_date()
            print(f"✅ 結束日期: {end_date}")

        return root, passenger_flow_tab

    except Exception as e:
        print(f"❌ 客流量查詢分頁測試失敗: {e}")
        return None, None


def main():
    """主函數"""
    print("台鐵 GUI 應用程式 - 客流量查詢功能測試")
    print("=" * 50)

    # 檢查必要套件
    try:
        import tkinter as tk
        print("✅ tkinter 套件可用")
    except ImportError:
        print("❌ tkinter 套件不可用")
        return False

    # 測試客流量查詢分頁
    root, passenger_flow_tab = test_passenger_flow_tab()

    if root and passenger_flow_tab:
        print("\n" + "=" * 50)
        print("✅ 客流量查詢功能測試完成！")
        print("功能說明：")
        print("- 車站選擇：從下拉選單選擇要查詢的車站")
        print("- 日期範圍：設定查詢的開始和結束日期")
        print("- 查詢結果：以表格形式顯示每日客流量資料")
        print("- 統計摘要：顯示總計和平均值等統計資訊")
        print("- 排序功能：點選欄位標題可排序資料")
        print("- 匯出功能：將查詢結果匯出為 CSV 檔案")
        print("\n測試建議：")
        print("1. 選擇一個車站（如果有載入車站清單）")
        print("2. 設定適當的日期範圍")
        print("3. 點選查詢按鈕執行查詢")
        print("4. 測試排序和匯出功能")
        print("5. 嘗試清除結果功能")
        print("\n注意：需要有效的資料庫連線才能查詢到實際資料")
        print("\n按 Ctrl+C 或關閉視窗結束測試")

        try:
            # 啟動 GUI
            root.mainloop()
        except KeyboardInterrupt:
            print("\n測試已中斷")
        except Exception as e:
            print(f"\n執行錯誤: {e}")

        return True
    else:
        print("\n❌ 客流量查詢功能測試失敗")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)