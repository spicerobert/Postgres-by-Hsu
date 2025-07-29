#!/usr/bin/env python3
"""
台鐵車站資訊查詢 GUI 應用程式啟動器

此腳本提供安全的應用程式啟動方式，包含錯誤處理和環境檢查。
"""

import sys
import os
import logging
from pathlib import Path

# 設定專案路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """設定日誌記錄"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('taiwan_railway_gui.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_environment():
    """檢查執行環境"""
    try:
        import tkinter
        import psycopg2
        import matplotlib
        return True
    except ImportError as e:
        print(f"缺少必要的套件: {e}")
        print("請安裝必要套件: pip install psycopg2-binary matplotlib")
        return False

def main():
    """主函數"""
    print("=" * 60)
    print("🚀 台鐵車站資訊查詢 GUI 應用程式")
    print("=" * 60)

    # 設定日誌
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # 檢查環境
        if not check_environment():
            sys.exit(1)

        # 匯入並啟動應用程式
        from taiwan_railway_gui.gui.main_window import create_main_window

        logger.info("正在啟動應用程式...")
        app = create_main_window()

        logger.info("應用程式啟動成功")
        app.run()

    except Exception as e:
        logger.error(f"應用程式啟動失敗: {e}")
        print(f"錯誤: {e}")
        print("請檢查日誌檔案 'taiwan_railway_gui.log' 以獲取詳細資訊")
        sys.exit(1)

if __name__ == "__main__":
    main()
