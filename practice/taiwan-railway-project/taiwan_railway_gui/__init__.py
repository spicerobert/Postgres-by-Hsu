"""
台鐵車站資訊查詢 GUI 應用程式

這是一個基於 Python tkinter 的桌面應用程式，專為查詢和分析台鐵車站資訊及進出站人數資料而設計。
此應用程式不僅是實用的資料查詢工具，同時也是 Python GUI 開發和 PostgreSQL 資料庫操作的優秀教學範例。

主要特色：
- 直觀的圖形化使用者介面
- 即時車站資訊搜尋
- 客流量統計分析
- 多車站比較功能
- 資料視覺化圖表
- 資料匯出功能
- 完整的錯誤處理機制
- 效能最佳化設計

技術架構：
- 前端：Python tkinter + ttk
- 後端：Python 3.8+
- 資料庫：PostgreSQL
- 視覺化：matplotlib
- 測試：pytest

模組結構：
- dao/: 資料存取層，處理資料庫操作
- models/: 資料模型，定義資料結構
- services/: 服務層，提供業務邏輯
- gui/: 使用者介面層，實作 GUI 元件
- utils/: 工具模組，提供輔助功能

設計原則：
- 分層架構：清楚分離各層職責
- 模組化設計：便於維護和擴展
- 介面導向：使用抽象介面定義系統邊界
- 錯誤處理：統一的錯誤處理機制
- 效能最佳化：非同步處理、快取機制

使用範例：
    # 啟動應用程式
    python main.py

    # 或者以模組方式匯入
    from taiwan_railway_gui.gui.main_window import create_main_window
    app = create_main_window()
    app.run()

系統需求：
- Python 3.8 或更高版本
- tkinter（通常隨 Python 安裝）
- psycopg2-binary（PostgreSQL 連接器）
- matplotlib（圖表繪製）

作者: Taiwan Railway GUI Team
授權: MIT License
版本: 1.0.0
"""

# 版本資訊
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

# 作者資訊
__author__ = "Taiwan Railway GUI Team"
__email__ = "contact@taiwan-railway-gui.com"

# 專案資訊
__title__ = "Taiwan Railway GUI"
__description__ = "台鐵車站資訊查詢 GUI 應用程式"
__url__ = "https://github.com/taiwan-railway-gui/taiwan-railway-gui"

# 授權資訊
__license__ = "MIT"
__copyright__ = "Copyright 2024 Taiwan Railway GUI Team"

# 支援的 Python 版本
__python_requires__ = ">=3.8"

# 套件分類
__classifiers__ = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Database :: Front-Ends",
    "Topic :: Education",
    "Topic :: Scientific/Engineering :: Visualization",
]

# 關鍵字
__keywords__ = [
    "taiwan", "railway", "gui", "tkinter", "postgresql",
    "data-analysis", "visualization", "education"
]

# 相依套件
__dependencies__ = [
    "psycopg2-binary>=2.8.0",
    "matplotlib>=3.3.0",
]

# 可選相依套件
__extras_require__ = {
    "dev": [
        "pytest>=6.0.0",
        "pytest-cov>=2.10.0",
        "black>=21.0.0",
        "flake8>=3.8.0",
        "mypy>=0.800",
    ],
    "docs": [
        "sphinx>=3.0.0",
        "sphinx-rtd-theme>=0.5.0",
    ],
}

# 匯出的公開 API
__all__ = [
    # 版本資訊
    "__version__",
    "__version_info__",
    "__author__",
    "__description__",

    # 主要入口點
    "create_main_window",

    # 核心模組
    "config",
    "models",
    "dao",
    "services",
    "gui",
    "utils",
]


def get_version() -> str:
    """
    取得應用程式版本號

    Returns:
        str: 版本號字串

    Example:
        >>> from taiwan_railway_gui import get_version
        >>> print(get_version())
        '1.0.0'
    """
    return __version__


def get_version_info() -> tuple:
    """
    取得詳細版本資訊

    Returns:
        tuple: 版本資訊元組 (major, minor, patch)

    Example:
        >>> from taiwan_railway_gui import get_version_info
        >>> print(get_version_info())
        (1, 0, 0)
    """
    return __version_info__


def get_package_info() -> dict:
    """
    取得完整的套件資訊

    Returns:
        dict: 包含所有套件資訊的字典

    Example:
        >>> from taiwan_railway_gui import get_package_info
        >>> info = get_package_info()
        >>> print(info['title'])
        'Taiwan Railway GUI'
    """
    return {
        'title': __title__,
        'version': __version__,
        'version_info': __version_info__,
        'author': __author__,
        'email': __email__,
        'description': __description__,
        'url': __url__,
        'license': __license__,
        'copyright': __copyright__,
        'python_requires': __python_requires__,
        'dependencies': __dependencies__,
        'keywords': __keywords__,
    }


# 延遲匯入主要元件，避免循環匯入
def create_main_window():
    """
    建立主應用程式視窗

    這是應用程式的主要入口點，建立並回傳主視窗實例。
    使用延遲匯入避免模組載入時的循環相依問題。

    Returns:
        MainWindow: 主視窗實例

    Example:
        >>> from taiwan_railway_gui import create_main_window
        >>> app = create_main_window()
        >>> app.run()
    """
    from taiwan_railway_gui.gui.main_window import create_main_window as _create_main_window
    return _create_main_window()


# 模組初始化檢查
def _check_dependencies():
    """檢查必要相依套件是否可用"""
    import sys

    # 檢查 Python 版本
    if sys.version_info < (3, 8):
        raise ImportError(
            f"Taiwan Railway GUI requires Python 3.8 or higher. "
            f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
        )

    # 檢查必要套件
    missing_packages = []

    try:
        import tkinter
    except ImportError:
        missing_packages.append("tkinter")

    try:
        import psycopg2
    except ImportError:
        missing_packages.append("psycopg2-binary")

    try:
        import matplotlib
    except ImportError:
        missing_packages.append("matplotlib")

    if missing_packages:
        raise ImportError(
            f"Missing required packages: {', '.join(missing_packages)}. "
            f"Please install them using: pip install {' '.join(missing_packages)}"
        )


# 執行初始化檢查
try:
    _check_dependencies()
except ImportError as e:
    import warnings
    warnings.warn(f"Dependency check failed: {e}", ImportWarning)


# 設定日誌記錄器
import logging

# 建立套件層級的日誌記錄器
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # 避免沒有處理器時的警告

# 設定日誌格式
_log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logging(level=logging.INFO, format_string=None):
    """
    設定套件的日誌記錄

    Args:
        level: 日誌等級，預設為 INFO
        format_string: 日誌格式字串，預設使用標準格式

    Example:
        >>> from taiwan_railway_gui import setup_logging
        >>> setup_logging(logging.DEBUG)
    """
    if format_string is None:
        format_string = _log_format

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('taiwan_railway_gui.log', encoding='utf-8')
        ]
    )