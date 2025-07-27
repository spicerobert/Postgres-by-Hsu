#!/usr/bin/env python3
"""
圖表視覺化 GUI 測試腳本

測試圖表視覺化分頁的功能。
"""

import sys
import os
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
import tkinter as tk
from taiwan_railway_gui.gui.chart_tab import create_chart_tab
from taiwan_railway_gui.config import get_config

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_chart_tab():
    """測試圖表視覺化分頁"""
    print("=== 測試圖表視覺化分頁 ===")

    try:
        # 建立測試視窗
        root = tk.Tk()
        root.title("圖表視覺化功能測試")
        root.geometry("1400x900")

        # 建立圖表視覺化分頁
        print("建立圖表視覺化分頁...")
        chart_tab = create_chart_tab(root)
        print("✅ 圖表視覺化分頁建立成功")

        # 檢查基本元件
        components = [
            ('車站選擇下拉選單', 'station_combobox'),
            ('圖表類型選擇', 'chart_type_var'),
            ('開始日期選擇器', 'start_date_picker'),
            ('結束日期選擇器', 'end_date_picker'),
            ('生成圖表按鈕', 'generate_button'),
            ('重新整理按鈕', 'refresh_button'),
            ('清除圖表按鈕', 'clear_button'),
            ('儲存圖表按鈕', 'save_button'),
            ('圖表畫布', 'chart_canvas'),
            ('圖表資訊變數', 'chart_info_var')
        ]

        for name, attr in components:
            if hasattr(chart_tab, attr):
                print(f"✅ {name} 存在")
            else:
                print(f"❌ {name} 不存在")

        # 檢查 DAO 連線
        dao_components = [
            ('車站 DAO', 'station_dao'),
            ('客流量 DAO', 'passenger_flow_dao')
        ]

        for name, attr in dao_components:
            if hasattr(chart_tab, attr):
                print(f"✅ {name} 已初始化")
            else:
                print(f"❌ {name} 未初始化")

        # 檢查圖表畫布
        if hasattr(chart_tab, 'chart_canvas'):
            canvas = chart_tab.chart_canvas
            if hasattr(canvas, 'figure') and hasattr(canvas, 'canvas') and hasattr(canvas, 'toolbar'):
                print("✅ matplotlib 圖表畫布已建立")
                print(f"  - 圖形大小: {canvas.figure.get_size_inches()}")
                print(f"  - DPI: {canvas.figure.dpi}")
            else:
                print("❌ matplotlib 圖表畫布建立不完整")

        # 檢查圖表類型選項
        if hasattr(chart_tab, 'chart_type_var'):
            chart_types = chart_tab.chart_type_combobox['values']
            print(f"✅ 圖表類型選項: {chart_types}")

        # 檢查日期選擇器
        if hasattr(chart_tab, 'start_date_picker'):
            start_date = chart_tab.start_date_picker.get_date()
            print(f"✅ 開始日期: {start_date}")

        if hasattr(chart_tab, 'end_date_picker'):
            end_date = chart_tab.end_date_picker.get_date()
            print(f"✅ 結束日期: {end_date}")

        return root, chart_tab

    except Exception as e:
        print(f"❌ 圖表視覺化分頁測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def main():
    """主函數"""
    print("台鐵 GUI 應用程式 - 圖表視覺化功能測試")
    print("=" * 50)

    # 檢查必要套件
    try:
        import tkinter as tk
        print("✅ tkinter 套件可用")
    except ImportError:
        print("❌ tkinter 套件不可用")
        return False

    try:
        import matplotlib
        print(f"✅ matplotlib 套件可用 (版本: {matplotlib.__version__})")
    except ImportError:
        print("❌ matplotlib 套件不可用，請安裝: pip install matplotlib")
        return False

    # 測試圖表視覺化分頁
    root, chart_tab = test_chart_tab()

    if root and chart_tab:
        print("\n" + "=" * 50)
        print("✅ 圖表視覺化功能測試完成！")
        print("功能說明：")
        print("- 車站選擇：從下拉選單選擇要繪製圖表的車站")
        print("- 圖表類型：選擇線圖或長條圖")
        print("- 日期範圍：設定圖表的時間範圍")
        print("- 圖表顯示：使用 matplotlib 繪製互動式圖表")
        print("- 圖表工具：縮放、平移、重置等操作")
        print("- 儲存功能：將圖表儲存為多種格式的圖片檔案")
        print("\n測試建議：")
        print("1. 等待車站清單載入完成")
        print("2. 選擇一個車站")
        print("3. 選擇圖表類型（線圖或長條圖）")
        print("4. 設定適當的日期範圍")
        print("5. 點選「生成圖表」按鈕")
        print("6. 使用圖表工具列進行縮放、平移等操作")
        print("7. 測試重新整理和清除功能")
        print("8. 嘗試儲存圖表為不同格式")
        print("\n圖表功能：")
        print("- 線圖：顯示進站和出站人數的趨勢變化")
        print("- 長條圖：以長條形式比較每日的進出站人數")
        print("- 互動工具：縮放、平移、重置、儲存等")
        print("- 自動調整：根據資料量自動調整顯示密度")
        print("\n注意：")
        print("- 需要有效的資料庫連線才能查詢到實際資料")
        print("- 圖表支援中文顯示")
        print("- 可儲存為 PNG、JPG、SVG、PDF 等格式")
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
        print("\n❌ 圖表視覺化功能測試失敗")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)