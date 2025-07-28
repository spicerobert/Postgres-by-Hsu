"""
應用程式配置模組

此模組包含台鐵車站資訊查詢 GUI 應用程式的所有配置常數和設定。
配置採用分類組織，便於維護和擴展。

配置類別：
- 資料庫連線設定
- GUI 介面配置
- 色彩主題設定
- 字體樣式配置
- 版面配置參數
- 應用程式常數
- 使用者訊息文字

環境變數支援：
資料庫配置支援透過環境變數覆蓋預設值，提供部署彈性。

使用範例：
    from taiwan_railway_gui.config import get_config

    # 取得資料庫配置
    db_config = get_config('database')

    # 取得 GUI 配置
    gui_config = get_config('gui')

作者: Taiwan Railway GUI Team
版本: 1.0.0
"""

import os
from typing import Dict, Any, Optional

# =============================================================================
# 資料庫配置
# =============================================================================

DATABASE_CONFIG = {
    # 資料庫主機位址，支援環境變數覆蓋
    'host': os.getenv('DB_HOST', 'localhost'),

    # 資料庫連接埠，預設為 PostgreSQL 標準埠
    'port': os.getenv('DB_PORT', '5432'),

    # 資料庫名稱
    'database': os.getenv('DB_NAME', 'postgres'),

    # 資料庫使用者名稱
    'user': os.getenv('DB_USER', 'postgres'),

    # 資料庫密碼，建議透過環境變數設定
    'password': os.getenv('DB_PASSWORD', 'raspberry'),

    # 連線逾時設定（秒）
    'connect_timeout': int(os.getenv('DB_CONNECT_TIMEOUT', '30')),

    # 查詢逾時設定（秒）
    'query_timeout': int(os.getenv('DB_QUERY_TIMEOUT', '60')),

    # 連線池大小
    'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),

    # 最大連線數
    'max_connections': int(os.getenv('DB_MAX_CONNECTIONS', '20')),
}

# =============================================================================
# GUI 介面配置
# =============================================================================

GUI_CONFIG = {
    # 應用程式視窗標題
    'window_title': '台鐵車站資訊查詢系統',

    # 預設視窗大小（寬x高）
    'window_size': '1200x800',

    # 最小視窗大小，確保介面元素可見
    'min_window_size': (800, 600),

    # 最大視窗大小（可選）
    'max_window_size': (1920, 1080),

    # 視覺主題
    'theme': 'default',

    # 是否允許調整視窗大小
    'resizable': True,

    # 是否在啟動時置中顯示
    'center_on_startup': True,

    # 分頁切換動畫
    'tab_animation': False,

    # 工具提示延遲（毫秒）
    'tooltip_delay': 500,
}

# =============================================================================
# 色彩主題配置
# =============================================================================

COLORS = {
    # 主要色彩 - 用於標題、按鈕和重要元素
    'primary': '#2E86AB',

    # 次要色彩 - 用於背景和次要元素
    'secondary': '#F5F5F5',

    # 強調色彩 - 用於成功狀態和確認動作
    'accent': '#28A745',

    # 警告色彩 - 用於警告訊息和注意事項
    'warning': '#FFC107',

    # 錯誤色彩 - 用於錯誤訊息和危險動作
    'error': '#DC3545',

    # 資訊色彩 - 用於一般資訊提示
    'info': '#17A2B8',

    # 文字色彩
    'text': '#333333',           # 主要文字
    'text_muted': '#6C757D',     # 次要文字
    'text_light': '#FFFFFF',     # 淺色背景上的文字

    # 背景色彩
    'background': '#FFFFFF',      # 主背景
    'background_alt': '#F8F9FA',  # 替代背景
    'background_dark': '#343A40', # 深色背景

    # 邊框色彩
    'border': '#DEE2E6',         # 一般邊框
    'border_focus': '#80BDFF',   # 焦點邊框

    # 狀態指示色彩
    'success': '#28A745',        # 成功狀態
    'danger': '#DC3545',         # 危險狀態
    'warning': '#FFC107',        # 警告狀態
    'info': '#17A2B8',          # 資訊狀態
}

# =============================================================================
# 字體配置
# =============================================================================

FONTS = {
    # 標題字體 - 用於主標題和重要標籤
    'header': ('Arial', 12, 'bold'),

    # 子標題字體 - 用於次要標題
    'subheader': ('Arial', 11, 'bold'),

    # 內文字體 - 用於一般文字內容
    'body': ('Arial', 10, 'normal'),

    # 小字體 - 用於說明文字和狀態列
    'small': ('Arial', 9, 'normal'),

    # 等寬字體 - 用於程式碼和資料顯示
    'monospace': ('Courier New', 9, 'normal'),

    # 按鈕字體 - 用於按鈕文字
    'button': ('Arial', 10, 'normal'),

    # 輸入框字體 - 用於文字輸入
    'input': ('Arial', 10, 'normal'),
}

# =============================================================================
# 版面配置參數
# =============================================================================

LAYOUT = {
    # 一般內距
    'padding': 10,

    # 小內距
    'padding_small': 5,

    # 大內距
    'padding_large': 20,

    # 元件間距
    'spacing': 5,

    # 按鈕寬度
    'button_width': 12,

    # 輸入框寬度
    'entry_width': 30,

    # 清單框高度（行數）
    'listbox_height': 10,

    # 文字區域高度（行數）
    'text_height': 5,

    # 分頁內距
    'tab_padding': 15,

    # 框架邊框寬度
    'frame_border_width': 1,

    # 捲軸寬度
    'scrollbar_width': 16,
}

# =============================================================================
# 應用程式常數
# =============================================================================

APP_CONSTANTS = {
    # 車站比較功能的最大車站數量
    'max_comparison_stations': 5,

    # 預設日期格式
    'default_date_format': '%Y-%m-%d',

    # 支援的匯出格式
    'export_formats': ['csv', 'xlsx', 'json'],

    # 支援的圖表格式
    'chart_formats': ['png', 'jpg', 'svg', 'pdf'],

    # 搜尋延遲時間（毫秒），避免過於頻繁的查詢
    'search_delay_ms': 300,

    # 自動儲存間隔（秒）
    'autosave_interval': 300,

    # 快取過期時間（秒）
    'cache_expiry': 3600,

    # 最大搜尋結果數量
    'max_search_results': 100,

    # 分頁大小
    'page_size': 50,

    # 圖表預設寬度和高度（像素）
    'chart_width': 800,
    'chart_height': 600,

    # 匯出檔案的預設編碼
    'export_encoding': 'utf-8-sig',  # 包含 BOM 以支援 Excel
}

# =============================================================================
# 錯誤訊息
# =============================================================================

ERROR_MESSAGES = {
    # 資料庫相關錯誤
    'db_connection_failed': '資料庫連線失敗，請檢查網路連線和資料庫設定。',
    'db_query_timeout': '資料庫查詢逾時，請稍後再試或縮小查詢範圍。',
    'db_query_failed': '資料庫查詢失敗，請檢查查詢條件。',

    # 資料驗證錯誤
    'invalid_date_range': '日期範圍無效，結束日期必須晚於開始日期。',
    'invalid_date_format': '日期格式不正確，請使用 YYYY-MM-DD 格式。',
    'future_date_not_allowed': '不允許選擇未來日期。',
    'date_range_too_large': '日期範圍過大，請選擇較小的時間區間。',

    # 車站相關錯誤
    'station_not_found': '找不到指定的車站，請檢查車站代碼或名稱。',
    'invalid_station_code': '車站代碼格式不正確。',
    'too_many_stations': f'最多只能選擇 {APP_CONSTANTS["max_comparison_stations"]} 個車站進行比較。',
    'no_stations_selected': '請至少選擇一個車站。',

    # 資料相關錯誤
    'no_data_found': '查詢期間內沒有找到資料。',
    'data_processing_failed': '資料處理失敗，請稍後再試。',
    'invalid_data_format': '資料格式不正確。',

    # 檔案操作錯誤
    'export_failed': '資料匯出失敗，請檢查檔案路徑和權限。',
    'file_not_found': '找不到指定的檔案。',
    'file_permission_denied': '檔案權限不足，無法執行操作。',
    'invalid_file_format': '不支援的檔案格式。',

    # 搜尋相關錯誤
    'invalid_search_query': '搜尋查詢格式不正確。',
    'search_query_too_short': '搜尋查詢至少需要 2 個字元。',
    'search_failed': '搜尋失敗，請稍後再試。',

    # 系統錯誤
    'memory_insufficient': '記憶體不足，請關閉其他應用程式。',
    'network_error': '網路連線錯誤。',
    'system_error': '系統錯誤，請重新啟動應用程式。',
}

# =============================================================================
# 成功訊息
# =============================================================================

SUCCESS_MESSAGES = {
    # 資料操作成功
    'data_exported': '資料已成功匯出到指定位置。',
    'data_imported': '資料已成功匯入。',
    'data_updated': '資料已成功更新。',

    # 檔案操作成功
    'chart_saved': '圖表已成功儲存。',
    'file_saved': '檔案已成功儲存。',
    'settings_saved': '設定已成功儲存。',

    # 查詢操作成功
    'query_completed': '查詢已完成。',
    'search_completed': '搜尋已完成。',

    # 系統操作成功
    'cache_cleared': '快取已清除。',
    'connection_established': '資料庫連線已建立。',
    'backup_completed': '備份已完成。',
}

# =============================================================================
# 資訊訊息
# =============================================================================

INFO_MESSAGES = {
    'loading': '載入中，請稍候...',
    'processing': '處理中，請稍候...',
    'connecting': '連線中...',
    'searching': '搜尋中...',
    'exporting': '匯出中...',
    'saving': '儲存中...',
}


def get_config(section: str) -> Dict[str, Any]:
    """
    取得指定區段的配置

    此函數提供統一的配置存取介面，支援所有配置區段的查詢。

    Args:
        section (str): 配置區段名稱，支援的值包括：
            - 'database': 資料庫配置
            - 'gui': GUI 介面配置
            - 'colors': 色彩主題配置
            - 'fonts': 字體配置
            - 'layout': 版面配置
            - 'constants': 應用程式常數
            - 'errors': 錯誤訊息
            - 'success': 成功訊息
            - 'info': 資訊訊息

    Returns:
        Dict[str, Any]: 指定區段的配置字典，如果區段不存在則回傳空字典

    Example:
        >>> db_config = get_config('database')
        >>> print(db_config['host'])
        'localhost'

        >>> colors = get_config('colors')
        >>> print(colors['primary'])
        '#2E86AB'

    Note:
        - 回傳的字典是原始配置的副本，修改不會影響原始配置
        - 不存在的區段會回傳空字典而不會拋出異常
    """
    # 配置區段映射表
    config_map = {
        'database': DATABASE_CONFIG,
        'gui': GUI_CONFIG,
        'colors': COLORS,
        'fonts': FONTS,
        'layout': LAYOUT,
        'constants': APP_CONSTANTS,
        'errors': ERROR_MESSAGES,
        'success': SUCCESS_MESSAGES,
        'info': INFO_MESSAGES,
    }

    # 回傳指定區段的配置，如果不存在則回傳空字典
    return config_map.get(section, {}).copy()


def get_database_url() -> str:
    """
    建構資料庫連線 URL

    根據資料庫配置建構標準的 PostgreSQL 連線 URL。

    Returns:
        str: PostgreSQL 連線 URL

    Example:
        >>> url = get_database_url()
        >>> print(url)
        'postgresql://postgres:password@localhost:5432/taiwan_railway'
    """
    db_config = get_config('database')

    # 建構連線 URL
    url = (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )

    return url


def validate_config() -> bool:
    """
    驗證配置的完整性和正確性

    檢查所有必要的配置項目是否存在且格式正確。

    Returns:
        bool: 配置是否有效

    Raises:
        ValueError: 當發現無效配置時
    """
    # 檢查資料庫配置
    db_config = get_config('database')
    required_db_keys = ['host', 'port', 'database', 'user']

    for key in required_db_keys:
        if not db_config.get(key):
            raise ValueError(f"資料庫配置缺少必要項目: {key}")

    # 檢查埠號格式
    try:
        port = int(db_config['port'])
        if not (1 <= port <= 65535):
            raise ValueError(f"資料庫埠號無效: {port}")
    except ValueError:
        raise ValueError(f"資料庫埠號格式不正確: {db_config['port']}")

    # 檢查 GUI 配置
    gui_config = get_config('gui')
    if not gui_config.get('window_title'):
        raise ValueError("GUI 配置缺少視窗標題")

    # 檢查視窗大小格式
    window_size = gui_config.get('window_size', '')
    if 'x' not in window_size:
        raise ValueError(f"視窗大小格式不正確: {window_size}")

    return True


# 在模組載入時驗證配置（可選）
if __name__ == "__main__":
    try:
        validate_config()
        print("配置驗證通過")
    except ValueError as e:
        print(f"配置驗證失敗: {e}")