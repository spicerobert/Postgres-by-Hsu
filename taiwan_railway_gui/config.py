"""
應用程式配置

包含應用程式的所有配置常數和設定。
"""

import os
from typing import Dict, Any

# 資料庫配置
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'taiwan_railway'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# GUI 配置
GUI_CONFIG = {
    'window_title': '台鐵車站資訊查詢系統',
    'window_size': '1200x800',
    'min_window_size': (800, 600),
    'theme': 'default',
}

# 色彩配置
COLORS = {
    'primary': '#2E86AB',      # 藍色 - 標題和活動元素
    'secondary': '#F5F5F5',    # 灰色 - 背景
    'accent': '#28A745',       # 綠色 - 成功狀態
    'warning': '#FFC107',      # 橙色 - 警告
    'error': '#DC3545',        # 紅色 - 錯誤
    'text': '#333333',         # 深灰色 - 文字
    'background': '#FFFFFF',   # 白色 - 主背景
}

# 字體配置
FONTS = {
    'header': ('Arial', 12, 'bold'),
    'body': ('Arial', 10, 'normal'),
    'monospace': ('Courier New', 9, 'normal'),
}

# 版面配置
LAYOUT = {
    'padding': 10,
    'button_width': 12,
    'entry_width': 30,
    'listbox_height': 10,
    'text_height': 5,
}

# 應用程式常數
APP_CONSTANTS = {
    'max_comparison_stations': 5,
    'default_date_format': '%Y-%m-%d',
    'export_formats': ['csv'],
    'chart_formats': ['png', 'jpg', 'svg'],
    'search_delay_ms': 300,  # 搜尋延遲毫秒
}

# 錯誤訊息
ERROR_MESSAGES = {
    'db_connection_failed': '資料庫連線失敗，請檢查網路連線和資料庫設定。',
    'invalid_date_range': '日期範圍無效，結束日期必須晚於開始日期。',
    'station_not_found': '找不到指定的車站，請檢查車站代碼或名稱。',
    'no_data_found': '查詢期間內沒有找到資料。',
    'export_failed': '資料匯出失敗，請檢查檔案路徑和權限。',
    'too_many_stations': f'最多只能選擇 {APP_CONSTANTS["max_comparison_stations"]} 個車站進行比較。',
    'invalid_search_query': '搜尋查詢格式不正確。',
}

# 成功訊息
SUCCESS_MESSAGES = {
    'data_exported': '資料已成功匯出到指定位置。',
    'chart_saved': '圖表已成功儲存。',
    'query_completed': '查詢已完成。',
}

def get_config(section: str) -> Dict[str, Any]:
    """取得指定區段的配置"""
    config_map = {
        'database': DATABASE_CONFIG,
        'gui': GUI_CONFIG,
        'colors': COLORS,
        'fonts': FONTS,
        'layout': LAYOUT,
        'constants': APP_CONSTANTS,
        'errors': ERROR_MESSAGES,
        'success': SUCCESS_MESSAGES,
    }
    return config_map.get(section, {})