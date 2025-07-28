"""
視覺回饋和狀態指示器

提供統一的視覺回饋系統，包括載入指示器、狀態指示器、動畫效果等。
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Callable, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
from taiwan_railway_gui.gui.styles import get_style_manager


class IndicatorType(Enum):
    """指示器類型"""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    LOADING = "loading"
    READY = "ready"


@dataclass
class VisualState:
    """視覺狀態配置"""
    color: str
    text: str
    icon: str = "●"
    animated: bool = False


class LoadingSpinner:
    """載入轉圈指示器"""

    def __init__(self, parent: tk.Widget, size: int = 16):
        """
        初始化載入轉圈指示器

        Args:
            parent: 父元件
            size: 指示器大小
        """
        self.parent = parent
        self.size = size
        self.is_spinning = False
        self.thread = None

        self.style_manager = get_style_manager()
        theme = self.style_manager.get_theme()
        colors = theme['colors']

        # 建立畫布
        self.canvas = tk.Canvas(parent, width=size, height=size,
                               background=colors['background'],
                               highlightthickness=0)

        self.spin_chars = ["◐", "◓", "◑", "◒"]
        self.current_char = 0

        # 建立文字元件顯示轉圈字符
        self.spin_label = tk.Label(parent,
                                  text=self.spin_chars[0],
                                  foreground=colors['primary'],
                                  background=colors['background'],
                                  font=('Arial', size))

    def start(self):
        """開始轉圈動畫"""
        if self.is_spinning:
            return

        self.is_spinning = True
        self.thread = threading.Thread(target=self._spin_animation, daemon=True)
        self.thread.start()

    def stop(self):
        """停止轉圈動畫"""
        self.is_spinning = False
        if self.thread:
            self.thread.join(timeout=0.1)

    def _spin_animation(self):
        """轉圈動畫邏輯"""
        while self.is_spinning:
            try:
                self.spin_label.configure(text=self.spin_chars[self.current_char])
                self.current_char = (self.current_char + 1) % len(self.spin_chars)
                time.sleep(0.2)
            except Exception:
                break

    def pack(self, **kwargs):
        """打包元件"""
        self.spin_label.pack(**kwargs)

    def grid(self, **kwargs):
        """網格佈局"""
        self.spin_label.grid(**kwargs)

    def place(self, **kwargs):
        """絕對定位"""
        self.spin_label.place(**kwargs)


class StatusIndicator:
    """狀態指示器"""

    def __init__(self, parent: tk.Widget):
        """
        初始化狀態指示器

        Args:
            parent: 父元件
        """
        self.parent = parent
        self.style_manager = get_style_manager()

        # 狀態配置
        self.states = self._create_state_configs()

        # 建立主要框架
        self.frame = ttk.Frame(parent)

        # 建立指示器元件
        self.icon_label = tk.Label(self.frame)
        self.text_label = tk.Label(self.frame)

        # 佈局
        self.icon_label.pack(side=tk.LEFT, padx=(0, 5))
        self.text_label.pack(side=tk.LEFT)

        # 設定初始狀態
        self.set_status(IndicatorType.READY)

    def _create_state_configs(self) -> Dict[IndicatorType, VisualState]:
        """建立狀態配置"""
        theme = self.style_manager.get_theme()
        colors = theme['colors']

        return {
            IndicatorType.SUCCESS: VisualState(
                color=colors['success'],
                text="就緒",
                icon="✓"
            ),
            IndicatorType.WARNING: VisualState(
                color=colors['warning'],
                text="警告",
                icon="⚠"
            ),
            IndicatorType.ERROR: VisualState(
                color=colors['error'],
                text="錯誤",
                icon="✗"
            ),
            IndicatorType.INFO: VisualState(
                color=colors['info'],
                text="資訊",
                icon="ℹ"
            ),
            IndicatorType.LOADING: VisualState(
                color=colors['primary'],
                text="載入中...",
                icon="●",
                animated=True
            ),
            IndicatorType.READY: VisualState(
                color=colors['success'],
                text="就緒",
                icon="●"
            )
        }

    def set_status(self, status: IndicatorType, custom_text: str = None):
        """
        設定狀態

        Args:
            status: 狀態類型
            custom_text: 自訂文字
        """
        if status not in self.states:
            return

        state = self.states[status]
        theme = self.style_manager.get_theme()
        fonts = theme['fonts']

        # 更新圖示
        self.icon_label.configure(
            text=state.icon,
            foreground=state.color,
            background=theme['colors']['background'],
            font=fonts['body']
        )

        # 更新文字
        display_text = custom_text if custom_text else state.text
        self.text_label.configure(
            text=display_text,
            foreground=state.color,
            background=theme['colors']['background'],
            font=fonts['small']
        )

        # 處理動畫
        if state.animated and status == IndicatorType.LOADING:
            self._start_loading_animation()
        else:
            self._stop_loading_animation()

    def _start_loading_animation(self):
        """開始載入動畫"""
        if hasattr(self, '_loading_animation') and self._loading_animation:
            return

        self._loading_animation = True
        self._animate_loading()

    def _stop_loading_animation(self):
        """停止載入動畫"""
        self._loading_animation = False

    def _animate_loading(self):
        """載入動畫邏輯"""
        if not hasattr(self, '_loading_animation') or not self._loading_animation:
            return

        # 載入點動畫
        current_text = self.text_label.cget('text')
        if current_text.endswith('...'):
            new_text = current_text[:-3]
        elif current_text.endswith('..'):
            new_text = current_text + '.'
        elif current_text.endswith('.'):
            new_text = current_text + '.'
        else:
            new_text = current_text + '.'

        self.text_label.configure(text=new_text)

        # 繼續動畫
        self.parent.after(500, self._animate_loading)

    def pack(self, **kwargs):
        """打包元件"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """網格佈局"""
        self.frame.grid(**kwargs)


class ProgressBar:
    """進度條元件"""

    def __init__(self, parent: tk.Widget, length: int = 200):
        """
        初始化進度條

        Args:
            parent: 父元件
            length: 進度條長度
        """
        self.parent = parent
        self.style_manager = get_style_manager()

        # 建立主要框架
        self.frame = ttk.Frame(parent)

        # 建立進度條
        self.progressbar = ttk.Progressbar(
            self.frame,
            length=length,
            mode='determinate',
            style='Custom.TProgressbar'
        )

        # 建立文字標籤
        self.label = tk.Label(self.frame, text="0%")

        # 佈局
        self.progressbar.pack(fill=tk.X, padx=(0, 10))
        self.label.pack(side=tk.RIGHT)

        # 設定樣式
        self._configure_style()

    def _configure_style(self):
        """配置進度條樣式"""
        theme = self.style_manager.get_theme()
        colors = theme['colors']
        fonts = theme['fonts']

        # 配置標籤樣式
        self.label.configure(
            foreground=colors['text'],
            background=colors['background'],
            font=fonts['small']
        )

    def set_progress(self, value: float, text: str = None):
        """
        設定進度

        Args:
            value: 進度值 (0-100)
            text: 顯示文字
        """
        self.progressbar['value'] = value

        if text:
            self.label.configure(text=text)
        else:
            self.label.configure(text=f"{value:.0f}%")

    def set_indeterminate(self, active: bool = True):
        """
        設定不定進度模式

        Args:
            active: 是否啟動
        """
        if active:
            self.progressbar.configure(mode='indeterminate')
            self.progressbar.start(10)
            self.label.configure(text="處理中...")
        else:
            self.progressbar.stop()
            self.progressbar.configure(mode='determinate')
            self.label.configure(text="完成")

    def pack(self, **kwargs):
        """打包元件"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """網格佈局"""
        self.frame.grid(**kwargs)


class NotificationBanner:
    """通知橫幅"""

    def __init__(self, parent: tk.Widget):
        """
        初始化通知橫幅

        Args:
            parent: 父元件
        """
        self.parent = parent
        self.style_manager = get_style_manager()

        # 建立主要框架
        self.frame = ttk.Frame(parent)

        # 建立通知標籤
        self.notification_label = tk.Label(self.frame)

        # 建立關閉按鈕
        self.close_button = tk.Button(self.frame, text="×",
                                     command=self.hide,
                                     borderwidth=0,
                                     relief=tk.FLAT)

        # 佈局
        self.notification_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        self.close_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # 預設隱藏
        self.frame.pack_forget()

    def show(self, message: str, notification_type: IndicatorType = IndicatorType.INFO,
             auto_hide: bool = True, duration: int = 3000):
        """
        顯示通知

        Args:
            message: 通知訊息
            notification_type: 通知類型
            auto_hide: 是否自動隱藏
            duration: 自動隱藏時間（毫秒）
        """
        theme = self.style_manager.get_theme()
        colors = theme['colors']
        fonts = theme['fonts']

        # 設定顏色配置
        color_map = {
            IndicatorType.SUCCESS: colors['success'],
            IndicatorType.WARNING: colors['warning'],
            IndicatorType.ERROR: colors['error'],
            IndicatorType.INFO: colors['info']
        }

        text_color = color_map.get(notification_type, colors['text'])

        # 配置標籤
        self.notification_label.configure(
            text=message,
            foreground=text_color,
            background=colors['background'],
            font=fonts['body']
        )

        # 配置關閉按鈕
        self.close_button.configure(
            foreground=text_color,
            background=colors['background'],
            font=fonts['body']
        )

        # 顯示橫幅
        self.frame.pack(fill=tk.X, pady=2)

        # 自動隱藏
        if auto_hide:
            self.parent.after(duration, self.hide)

    def hide(self):
        """隱藏通知"""
        self.frame.pack_forget()


class AnimationHelper:
    """動畫輔助工具"""

    @staticmethod
    def fade_in(widget: tk.Widget, duration: int = 300, steps: int = 10):
        """
        淡入動畫

        Args:
            widget: 目標元件
            duration: 動畫時間（毫秒）
            steps: 動畫步數
        """
        step_delay = duration // steps
        alpha_step = 1.0 / steps

        def animate_step(current_step):
            if current_step <= steps:
                alpha = current_step * alpha_step
                # 在 tkinter 中模擬透明度效果（使用顏色漸變）
                widget.after(step_delay, lambda: animate_step(current_step + 1))

        animate_step(1)

    @staticmethod
    def slide_in(widget: tk.Widget, direction: str = 'right',
                distance: int = 100, duration: int = 300):
        """
        滑入動畫

        Args:
            widget: 目標元件
            direction: 滑入方向 ('left', 'right', 'up', 'down')
            distance: 滑動距離
            duration: 動畫時間（毫秒）
        """
        steps = 20
        step_delay = duration // steps
        step_distance = distance // steps

        # 計算初始位置偏移
        if direction == 'right':
            start_x, start_y = -distance, 0
        elif direction == 'left':
            start_x, start_y = distance, 0
        elif direction == 'down':
            start_x, start_y = 0, -distance
        else:  # 'up'
            start_x, start_y = 0, distance

        # 設定初始位置
        widget.place(x=widget.winfo_x() + start_x, y=widget.winfo_y() + start_y)

        def animate_step(current_step):
            if current_step <= steps:
                progress = current_step / steps
                current_x = start_x * (1 - progress)
                current_y = start_y * (1 - progress)

                widget.place(x=widget.winfo_x() - current_x/steps,
                           y=widget.winfo_y() - current_y/steps)

                widget.after(step_delay, lambda: animate_step(current_step + 1))

        animate_step(1)


class VisualFeedbackManager:
    """視覺回饋管理器"""

    def __init__(self, parent: tk.Widget):
        """
        初始化視覺回饋管理器

        Args:
            parent: 父元件
        """
        self.parent = parent
        self.style_manager = get_style_manager()

        # 回饋元件
        self.status_indicator = None
        self.loading_spinner = None
        self.progress_bar = None
        self.notification_banner = None

        # 建立回饋容器
        self.feedback_frame = ttk.Frame(parent)
        self.feedback_frame.pack(fill=tk.X, side=tk.BOTTOM)

    def create_status_indicator(self) -> StatusIndicator:
        """建立狀態指示器"""
        if not self.status_indicator:
            self.status_indicator = StatusIndicator(self.feedback_frame)
            self.status_indicator.pack(side=tk.LEFT, padx=5)
        return self.status_indicator

    def create_loading_spinner(self, size: int = 16) -> LoadingSpinner:
        """建立載入轉圈指示器"""
        if not self.loading_spinner:
            self.loading_spinner = LoadingSpinner(self.feedback_frame, size)
            self.loading_spinner.pack(side=tk.LEFT, padx=5)
        return self.loading_spinner

    def create_progress_bar(self, length: int = 200) -> ProgressBar:
        """建立進度條"""
        if not self.progress_bar:
            self.progress_bar = ProgressBar(self.feedback_frame, length)
            self.progress_bar.pack(side=tk.RIGHT, padx=5)
        return self.progress_bar

    def create_notification_banner(self) -> NotificationBanner:
        """建立通知橫幅"""
        if not self.notification_banner:
            self.notification_banner = NotificationBanner(self.parent)
        return self.notification_banner

    def show_loading(self, message: str = "載入中..."):
        """顯示載入狀態"""
        status_indicator = self.create_status_indicator()
        status_indicator.set_status(IndicatorType.LOADING, message)

        spinner = self.create_loading_spinner()
        spinner.start()

    def hide_loading(self, success_message: str = "完成"):
        """隱藏載入狀態"""
        status_indicator = self.create_status_indicator()
        status_indicator.set_status(IndicatorType.SUCCESS, success_message)

        if self.loading_spinner:
            self.loading_spinner.stop()

    def show_error(self, message: str):
        """顯示錯誤狀態"""
        status_indicator = self.create_status_indicator()
        status_indicator.set_status(IndicatorType.ERROR, message)

        banner = self.create_notification_banner()
        banner.show(message, IndicatorType.ERROR)

    def show_success(self, message: str):
        """顯示成功狀態"""
        status_indicator = self.create_status_indicator()
        status_indicator.set_status(IndicatorType.SUCCESS, message)

        banner = self.create_notification_banner()
        banner.show(message, IndicatorType.SUCCESS)

    def show_warning(self, message: str):
        """顯示警告狀態"""
        status_indicator = self.create_status_indicator()
        status_indicator.set_status(IndicatorType.WARNING, message)

        banner = self.create_notification_banner()
        banner.show(message, IndicatorType.WARNING)


# 全域實例
_visual_feedback_manager = None


def get_visual_feedback_manager(parent: tk.Widget = None) -> VisualFeedbackManager:
    """取得全域視覺回饋管理器實例"""
    global _visual_feedback_manager
    if _visual_feedback_manager is None and parent:
        _visual_feedback_manager = VisualFeedbackManager(parent)
    return _visual_feedback_manager
