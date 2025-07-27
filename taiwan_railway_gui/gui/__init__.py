"""
圖形使用者介面 (GUI) 模組

包含所有 tkinter 相關的 GUI 元件：
- MainWindow: 主應用程式視窗
- BaseTab: 基礎分頁類別
- StationSearchTab: 車站搜尋分頁
- PassengerFlowTab: 客流量查詢分頁
- ComparisonTab: 車站比較分頁
- ChartTab: 圖表視覺化分頁
- Styles: 樣式管理器
- Accessibility: 無障礙功能
- VisualFeedback: 視覺回饋系統
- PlatformConsistency: 跨平台一致性
"""

from .main_window import MainWindow, create_main_window
from .base_tab import BaseTab
from .station_search_tab import StationSearchTab, create_station_search_tab
from .passenger_flow_tab import PassengerFlowTab, create_passenger_flow_tab
from .comparison_tab import ComparisonTab, create_comparison_tab
from .chart_tab import ChartTab, create_chart_tab
from .styles import StyleManager, get_style_manager
from .accessibility import KeyboardNavigationManager, AccessibilityHelper, get_keyboard_navigation_manager, get_accessibility_helper
from .visual_feedback import (
    VisualFeedbackManager, StatusIndicator, LoadingSpinner, ProgressBar,
    NotificationBanner, AnimationHelper, IndicatorType, get_visual_feedback_manager
)
from .platform_consistency import PlatformManager, get_platform_manager, apply_platform_consistency

__all__ = [
    'MainWindow',
    'create_main_window',
    'BaseTab',
    'StationSearchTab',
    'create_station_search_tab',
    'PassengerFlowTab',
    'create_passenger_flow_tab',
    'ComparisonTab',
    'create_comparison_tab',
    'ChartTab',
    'create_chart_tab',
    'StyleManager',
    'get_style_manager',
    'KeyboardNavigationManager',
    'AccessibilityHelper',
    'get_keyboard_navigation_manager',
    'get_accessibility_helper',
    'VisualFeedbackManager',
    'StatusIndicator',
    'LoadingSpinner',
    'ProgressBar',
    'NotificationBanner',
    'AnimationHelper',
    'IndicatorType',
    'get_visual_feedback_manager',
    'PlatformManager',
    'get_platform_manager',
    'apply_platform_consistency'
]