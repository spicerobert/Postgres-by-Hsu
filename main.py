#!/usr/bin/env python3
"""
台鐵車站資訊查詢 GUI 應用程式主程式

這是應用程式的主要入口點。
"""

import sys
import os
import logging
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from taiwan_railway_gui.config import get_config


def setup_logging():
    """設定日誌記錄"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('taiwan_railway_gui.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """主函數"""
    try:
        # 設定日誌
        setup_logging()
        logger = logging.getLogger(__name__)

        logger.info("啟動台鐵車站資訊查詢 GUI 應用程式")

        # 檢查 Python 版本
        if sys.version_info < (3, 8):
            logger.error("此應用程式需要 Python 3.8 或更高版本")
            sys.exit(1)

        # 檢查必要的套件
        try:
            import tkinter as tk
            import psycopg2
            import matplotlib
        except ImportError as e:
            logger.error(f"缺少必要的套件: {e}")
            logger.error("請安裝必要的套件: pip install psycopg2-binary matplotlib")
            sys.exit(1)

        # 載入配置
        gui_config = get_config('gui')
        logger.info(f"載入配置: {gui_config}")

        # 啟動主應用程式
        from taiwan_railway_gui.gui.main_window import create_main_window

        logger.info("建立主視窗...")
        app = create_main_window()

        logger.info("啟動應用程式...")
        app.run()

    except Exception as e:
        logger.error(f"應用程式啟動失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()