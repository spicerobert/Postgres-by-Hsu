#!/usr/bin/env python3
"""
GUI 測試腳本

測試主視窗和基礎 GUI 元件功能。
"""

import sys
import os
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
import tkinter as tk
from taiwan_railway_gui.gui.main_window import create_main_window
from taiwan_railway_gui.config import get_config

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_gui_components():
    """測試 GUI 元件"""
    print("=== 測試 GUI 元件 ===")

    try:
        # 測試配置載入
        gui_config = get_config('gui')
        print(f"✅ GUI 配置載入成功: {gui_config['window_title']}")

        # 測試主視窗建立
        print("建立主視窗...")
        app = create_main_window()
        print("✅ 主視窗建立成功")

        # 測試分頁
        tabs = list(app.tabs.keys())
        print(f"✅ 分頁建立成功: {tabs}")

        # 測試資料庫連線狀態
        db_connected = app.db_manager.is_connected
        print(f"{'✅' if db_connected else '⚠️'} 資料庫連線狀態: {'已連線' if db_connected else '未連線'}")

        return app

    except Exception as e:
        print(f"❌ GUI 元件測試失敗: {e}")
        return None


def main():
    """主函數"""
    print("台鐵 GUI 應用程式 - GUI 測試")
    print("=" * 50)

    # 檢查 tkinter 可用性
    try:
        import tkinter as tk
        print("✅ tkinter 套件可用")
    except ImportError:
        print("❌ tkinter 套件不可用")
        return False

    # 測試 GUI 元件
    app = test_gui_components()

    if app:
        print("\n" + "=" * 50)
        print("✅ GUI 測試完成！")
        print("提示：")
        print("- 視窗已建立，包含4個分頁")
        print("- 選單列包含檔案、檢視、工具、說明選單")
        print("- 狀態列顯示載入指示器和資料庫狀態")
        print("- 可以測試選單功能和分頁切換")
        print("\n按 Ctrl+C 或關閉視窗結束測試")

        try:
            # 啟動 GUI
            app.run()
        except KeyboardInterrupt:
            print("\n測試已中斷")
        except Exception as e:
            print(f"\n執行錯誤: {e}")

        return True
    else:
        print("\n❌ GUI 測試失敗")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)