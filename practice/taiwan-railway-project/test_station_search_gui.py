#!/usr/bin/env python3
"""
車站搜尋 GUI 測試腳本

測試車站搜尋分頁的功能。
"""

import sys
import os
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
import tkinter as tk
from taiwan_railway_gui.gui.station_search_tab import create_station_search_tab
from taiwan_railway_gui.config import get_config

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_station_search_tab():
    """測試車站搜尋分頁"""
    print("=== 測試車站搜尋分頁 ===")

    try:
        # 建立測試視窗
        root = tk.Tk()
        root.title("車站搜尋功能測試")
        root.geometry("800x600")

        # 建立車站搜尋分頁
        print("建立車站搜尋分頁...")
        station_search_tab = create_station_search_tab(root)
        print("✅ 車站搜尋分頁建立成功")

        # 檢查基本元件
        components = [
            ('搜尋輸入框', 'search_entry'),
            ('搜尋按鈕', 'search_button'),
            ('清除按鈕', 'clear_button'),
            ('結果清單', 'results_listbox'),
            ('詳細資訊區域', 'info_vars')
        ]

        for name, attr in components:
            if hasattr(station_search_tab, attr):
                print(f"✅ {name} 存在")
            else:
                print(f"❌ {name} 不存在")

        # 檢查 DAO 連線
        if hasattr(station_search_tab, 'station_dao'):
            print("✅ 車站 DAO 已初始化")
        else:
            print("❌ 車站 DAO 未初始化")

        return root, station_search_tab

    except Exception as e:
        print(f"❌ 車站搜尋分頁測試失敗: {e}")
        return None, None


def main():
    """主函數"""
    print("台鐵 GUI 應用程式 - 車站搜尋功能測試")
    print("=" * 50)

    # 檢查必要套件
    try:
        import tkinter as tk
        print("✅ tkinter 套件可用")
    except ImportError:
        print("❌ tkinter 套件不可用")
        return False

    # 測試車站搜尋分頁
    root, station_search_tab = test_station_search_tab()

    if root and station_search_tab:
        print("\n" + "=" * 50)
        print("✅ 車站搜尋功能測試完成！")
        print("功能說明：")
        print("- 搜尋框：輸入車站名稱或代碼進行搜尋")
        print("- 即時搜尋：輸入時自動搜尋（延遲300ms）")
        print("- 結果清單：顯示搜尋結果，點選查看詳細資訊")
        print("- 詳細資訊：顯示選中車站的完整資訊")
        print("- 操作按鈕：查看客流量、複製資訊、匯出資料")
        print("\n測試建議：")
        print("1. 嘗試搜尋 '台北' 或 '1000'")
        print("2. 點選搜尋結果查看詳細資訊")
        print("3. 測試清除和重新整理功能")
        print("4. 嘗試匯出功能")
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
        print("\n❌ 車站搜尋功能測試失敗")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)