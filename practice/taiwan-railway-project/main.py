#!/usr/bin/env python3
"""
台鐵車站資訊查詢 GUI 應用程式主程式

這是應用程式的主要入口點，負責初始化系統環境、檢查相依性、設定日誌記錄，
並啟動主應用程式視窗。

主要功能：
- 檢查 Python 版本相容性
- 驗證必要套件是否已安裝
- 設定日誌記錄系統
- 載入應用程式配置
- 初始化並啟動主視窗

使用方式：
    python main.py

環境需求：
    - Python 3.8 或更高版本
    - tkinter（GUI 框架）
    - psycopg2（PostgreSQL 連接器）
    - matplotlib（圖表繪製）

作者: Taiwan Railway GUI Team
版本: 1.0.0
"""

import sys
import os
import logging
from pathlib import Path

# 將專案根目錄加入 Python 路徑
# 這確保了模組可以正確匯入，無論從哪個目錄執行程式
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from taiwan_railway_gui.config import get_config


def setup_logging():
    """
    設定應用程式的日誌記錄系統

    配置日誌記錄器以同時輸出到檔案和控制台，使用統一的格式。
    日誌檔案將儲存在應用程式根目錄下的 'taiwan_railway_gui.log'。

    日誌格式包含：
    - 時間戳記
    - 記錄器名稱
    - 日誌等級
    - 訊息內容

    Raises:
        OSError: 當無法建立日誌檔案時
    """
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                # 輸出到檔案，用於持久化記錄
                logging.FileHandler('taiwan_railway_gui.log', encoding='utf-8'),
                # 輸出到控制台，用於即時監控
                logging.StreamHandler(sys.stdout)
            ]
        )

        # 設定第三方套件的日誌等級，避免過多的除錯訊息
        logging.getLogger('matplotlib').setLevel(logging.WARNING)
        logging.getLogger('PIL').setLevel(logging.WARNING)

    except OSError as e:
        print(f"警告：無法建立日誌檔案: {e}")
        # 如果無法建立檔案，至少保持控制台輸出
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )


def check_python_version():
    """
    檢查 Python 版本是否符合最低需求

    應用程式需要 Python 3.8 或更高版本，因為使用了以下功能：
    - 海象運算子 (:=)
    - 位置參數專用語法 (/)
    - 型別提示的改進

    Raises:
        SystemExit: 當 Python 版本不符合需求時
    """
    required_version = (3, 8)
    current_version = sys.version_info[:2]

    if current_version < required_version:
        error_msg = (
            f"此應用程式需要 Python {required_version[0]}.{required_version[1]} 或更高版本，"
            f"目前版本為 {current_version[0]}.{current_version[1]}"
        )
        logging.error(error_msg)
        print(error_msg)
        sys.exit(1)


def check_dependencies():
    """
    檢查必要的第三方套件是否已安裝

    檢查以下套件：
    - tkinter: GUI 框架（通常隨 Python 安裝）
    - psycopg2: PostgreSQL 資料庫連接器
    - matplotlib: 圖表繪製套件

    Raises:
        SystemExit: 當缺少必要套件時
    """
    required_packages = {
        'tkinter': 'GUI 框架',
        'psycopg2': 'PostgreSQL 連接器',
        'matplotlib': '圖表繪製套件'
    }

    missing_packages = []

    for package, description in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(f"{package} ({description})")

    if missing_packages:
        error_msg = f"缺少必要的套件: {', '.join(missing_packages)}"
        logging.error(error_msg)
        print(error_msg)
        print("請安裝必要的套件:")
        print("pip install psycopg2-binary matplotlib")
        print("注意：tkinter 通常隨 Python 一起安裝")
        sys.exit(1)


def main():
    """
    應用程式主函數

    執行應用程式的初始化流程：
    1. 設定日誌記錄
    2. 檢查 Python 版本
    3. 檢查套件相依性
    4. 載入應用程式配置
    5. 建立並啟動主視窗

    此函數包含完整的錯誤處理，確保任何初始化失敗都會被適當記錄。

    Raises:
        SystemExit: 當初始化失敗時
    """
    try:
        # 第一步：設定日誌記錄
        # 必須最先執行，以便後續步驟的錯誤能被記錄
        setup_logging()
        logger = logging.getLogger(__name__)

        logger.info("=" * 50)
        logger.info("啟動台鐵車站資訊查詢 GUI 應用程式")
        logger.info("=" * 50)

        # 第二步：檢查系統環境
        logger.info("檢查 Python 版本...")
        check_python_version()
        logger.info(f"Python 版本檢查通過: {sys.version}")

        # 第三步：檢查套件相依性
        logger.info("檢查必要套件...")
        check_dependencies()
        logger.info("套件相依性檢查通過")

        # 第四步：載入應用程式配置
        logger.info("載入應用程式配置...")
        gui_config = get_config('gui')
        logger.info(f"GUI 配置載入完成: {gui_config}")

        # 第五步：建立並啟動主應用程式
        logger.info("匯入主視窗模組...")
        from taiwan_railway_gui.gui.main_window import create_main_window

        logger.info("建立主視窗實例...")
        app = create_main_window()

        logger.info("應用程式初始化完成，啟動主視窗...")
        logger.info("=" * 50)

        # 啟動 GUI 主迴圈
        app.run()

    except KeyboardInterrupt:
        # 處理使用者中斷（Ctrl+C）
        logger.info("使用者中斷應用程式")
        sys.exit(0)

    except Exception as e:
        # 處理所有其他未預期的錯誤
        error_msg = f"應用程式啟動失敗: {e}"
        logger.error(error_msg, exc_info=True)  # 包含完整的錯誤堆疊
        print(f"錯誤: {error_msg}")
        print("請檢查日誌檔案 'taiwan_railway_gui.log' 以獲取詳細資訊")
        sys.exit(1)

    finally:
        # 清理資源（如果需要）
        logger.info("應用程式結束")


if __name__ == "__main__":
    # 當直接執行此檔案時啟動應用程式
    # 這是 Python 的標準做法，確保模組可以被匯入而不會自動執行
    main()