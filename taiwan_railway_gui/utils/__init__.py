"""
工具函數模組

包含應用程式使用的工具函數和常數：
- 常數定義
- 工具函數
- 配置管理
- GUI 輔助工具
"""

from .gui_helpers import (
    ThreadSafeVar,
    WidgetState,
    center_window,
    create_tooltip,
    bind_mousewheel,
    create_progress_dialog,
    format_number,
    truncate_text,
    validate_numeric_input,
    create_numeric_entry,
    AutoCompleteCombobox
)

__all__ = [
    'ThreadSafeVar',
    'WidgetState',
    'center_window',
    'create_tooltip',
    'bind_mousewheel',
    'create_progress_dialog',
    'format_number',
    'truncate_text',
    'validate_numeric_input',
    'create_numeric_entry',
    'AutoCompleteCombobox'
]