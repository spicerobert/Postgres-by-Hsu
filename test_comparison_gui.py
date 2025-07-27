#!/usr/bin/env python3
"""
車站比較 GUI 測試腳本

測試車站比較分頁的功能。
"""

import sys
import os
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
import tkinter as tk
from taiwan_railway_gui.gui.comparison_tab import create_comparison_tab
from taiwan_railway_gui.config import get_config

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_comparison_tab():
    """測試車站比較分頁"""
    print("=== 測試車站比較分頁 ===")

    try:
        # 建立測試視窗
        root = tk.Tk()
        root.title("車站比較功能測試")
        root.geometry("1200x800")

        # 建立車站比較分頁
        print("建立車站比較分頁...")
        comparison_tab = create_comparison_tab(root)
        print("✅ 車站比較分頁建立成功")

        # 檢查基本元件
        components = [
            ('車站選擇器', 'station_selector'),
            ('開始日期選擇器', 'start_date_picker'),
            ('結束日期選擇器', 'end_date_picker'),
            ('比較按鈕', 'compare_button'),
            ('清除按鈕', 'clear_button'),
            ('匯出按鈕', 'export_button'),
            ('結果樹狀檢視', 'results_tree'),
            ('排名資訊變數', 'ranking_info_var')
        ]

        for name, attr in components:
            if hasattr(comparison_tab, attr):
                print(f"✅ {name} 存在")
            else:
                print(f"❌ {name} 不存在")

        # 檢查 DAO 連線
        dao_components = [
            ('車站 DAO', 'station_dao'),
            ('客流量 DAO', 'passenger_flow_dao')
        ]

        for name, attr in dao_components:
            if hasattr(comparison_tab, attr):
                print(f"✅ {name} 已初始化")
            else:
                print(f"❌ {name} 未初始化")

        # 檢查車站選擇器
        if hasattr(comparison_tab, 'station_selector') and comparison_tab.station_selector:
            max_stations = comparison_tab.max_stations
            print(f"✅ 車站選擇器已建立，最大選擇數量: {max_stations}")
        else:
            print("⚠️  車站選擇器尚未建立（可能正在載入車站清單）")

        # 檢查日期選擇器
        if hasattr(comparison_tab, 'start_date_picker'):
            start_date = comparison_tab.start_date_picker.get_date()
            print(f"✅ 開始日期: {start_date}")

        if hasattr(comparison_tab, 'end_date_picker'):
            end_date = comparison_tab.end_date_picker.get_date()
            print(f"✅ 結束日期: {end_date}")

        return root, comparison_tab

    except Exception as e:
        print(f"❌ 車站比較分頁測試失敗: {e}")
        return None, None


def main():
    """主函數"""
    print("台鐵 GUI 應用程式 - 車站比較功能測試")
    print("=" * 50)

    # 檢查必要套件
    try:
        import tkinter as tk
        print("✅ tkinter 套件可用")
    except ImportError:
        print("❌ tkinter 套件不可用")
        return False

    # 測試車站比較分頁
    root, comparison_tab = test_comparison_tab()

    if root and comparison_tab:
        print("\n" + "=" * 50)
        print("✅ 車站比較功能測試完成！")
        print("功能說明：")
        print("- 車站選擇：從左側清單選擇車站，點選「加入」按鈕或雙擊加入比較")
        print("- 已選車站：右側顯示已選擇的車站，最多可選擇 5 個")
        print("- 日期範圍：設定比較的時間範圍")
        print("- 比較結果：以表格形式顯示各車站的排名和統計資料")
        print("- 排名顯示：前三名會有不同的背景顏色（金、銀、銅）")
        print("- 排序功能：點選欄位標題可重新排序")
        print("- 匯出功能：將比較結果匯出為 CSV 檔案")
        print("\n測試建議：")
        print("1. 等待車站清單載入完成")
        print("2. 從左側清單選擇至少 2 個車站加入比較")
        print("3. 設定適當的日期範圍")
        print("4. 點選「開始比較」按鈕")
        print("5. 查看排名結果和統計資料")
        print("6. 測試排序和匯出功能")
        print("7. 嘗試移除車站和清除結果")
        print("\n注意：")
        print("- 需要有效的資料庫連線才能查詢到實際資料")
        print("- 最多只能選擇 5 個車站進行比較")
        print("- 排名按總客流量降序排列")
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
        print("\n❌ 車站比較功能測試失敗")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)