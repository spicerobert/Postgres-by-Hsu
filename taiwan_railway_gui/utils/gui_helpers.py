"""
GUI 輔助工具函數

提供 GUI 開發中常用的工具函數和輔助類別。
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any, Dict, List
import threading
import time


class ThreadSafeVar:
    """執行緒安全的變數包裝器"""

    def __init__(self, initial_value: Any = None):
        """
        初始化執行緒安全變數

        Args:
            initial_value: 初始值
        """
        self._value = initial_value
        self._lock = threading.Lock()

    def get(self) -> Any:
        """取得值"""
        with self._lock:
            return self._value

    def set(self, value: Any):
        """設定值"""
        with self._lock:
            self._value = value

    def update(self, func: Callable[[Any], Any]):
        """使用函數更新值"""
        with self._lock:
            self._value = func(self._value)


class WidgetState:
    """元件狀態管理器"""

    def __init__(self):
        """初始化狀態管理器"""
        self._states = {}

    def save_state(self, widget: tk.Widget, state_name: str):
        """
        儲存元件狀態

        Args:
            widget: 要儲存狀態的元件
            state_name: 狀態名稱
        """
        try:
            if isinstance(widget, (ttk.Entry, tk.Entry)):
                self._states[state_name] = widget.get()
            elif isinstance(widget, (ttk.Combobox,)):
                self._states[state_name] = widget.get()
            elif isinstance(widget, (tk.Listbox,)):
                self._states[state_name] = widget.curselection()
            elif isinstance(widget, (ttk.Treeview,)):
                self._states[state_name] = widget.selection()
            else:
                # 嘗試取得通用狀態
                if hasattr(widget, 'get'):
                    self._states[state_name] = widget.get()
        except Exception:
            pass  # 忽略無法儲存的狀態

    def restore_state(self, widget: tk.Widget, state_name: str):
        """
        恢復元件狀態

        Args:
            widget: 要恢復狀態的元件
            state_name: 狀態名稱
        """
        if state_name not in self._states:
            return

        try:
            state_value = self._states[state_name]

            if isinstance(widget, (ttk.Entry, tk.Entry)):
                widget.delete(0, tk.END)
                widget.insert(0, state_value)
            elif isinstance(widget, (ttk.Combobox,)):
                widget.set(state_value)
            elif isinstance(widget, (tk.Listbox,)):
                widget.selection_clear(0, tk.END)
                for index in state_value:
                    widget.selection_set(index)
            elif isinstance(widget, (ttk.Treeview,)):
                widget.selection_set(state_value)
            else:
                # 嘗試設定通用狀態
                if hasattr(widget, 'set'):
                    widget.set(state_value)
        except Exception:
            pass  # 忽略無法恢復的狀態

    def clear_state(self, state_name: str):
        """清除指定狀態"""
        self._states.pop(state_name, None)

    def clear_all_states(self):
        """清除所有狀態"""
        self._states.clear()


def center_window(window: tk.Toplevel, width: int, height: int):
    """
    將視窗置中顯示

    Args:
        window: 要置中的視窗
        width: 視窗寬度
        height: 視窗高度
    """
    # 取得螢幕尺寸
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 計算置中位置
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # 設定視窗位置和大小
    window.geometry(f"{width}x{height}+{x}+{y}")


def create_tooltip(widget: tk.Widget, text: str, delay: int = 500):
    """
    為元件建立工具提示

    Args:
        widget: 要加入工具提示的元件
        text: 提示文字
        delay: 顯示延遲（毫秒）
    """
    class ToolTip:
        def __init__(self, widget, text, delay):
            self.widget = widget
            self.text = text
            self.delay = delay
            self.tooltip_window = None
            self.timer = None

            # 綁定事件
            self.widget.bind("<Enter>", self.on_enter)
            self.widget.bind("<Leave>", self.on_leave)
            self.widget.bind("<Motion>", self.on_motion)

        def on_enter(self, event):
            """滑鼠進入事件"""
            self.schedule_tooltip()

        def on_leave(self, event):
            """滑鼠離開事件"""
            self.cancel_tooltip()
            self.hide_tooltip()

        def on_motion(self, event):
            """滑鼠移動事件"""
            self.cancel_tooltip()
            self.schedule_tooltip()

        def schedule_tooltip(self):
            """排程顯示工具提示"""
            self.cancel_tooltip()
            self.timer = self.widget.after(self.delay, self.show_tooltip)

        def cancel_tooltip(self):
            """取消工具提示"""
            if self.timer:
                self.widget.after_cancel(self.timer)
                self.timer = None

        def show_tooltip(self):
            """顯示工具提示"""
            if self.tooltip_window:
                return

            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

            self.tooltip_window = tk.Toplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{x}+{y}")

            label = tk.Label(
                self.tooltip_window,
                text=self.text,
                background="lightyellow",
                relief=tk.SOLID,
                borderwidth=1,
                font=("Arial", 9)
            )
            label.pack()

        def hide_tooltip(self):
            """隱藏工具提示"""
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None

    return ToolTip(widget, text, delay)


def bind_mousewheel(widget: tk.Widget, canvas: Optional[tk.Canvas] = None):
    """
    為元件綁定滑鼠滾輪事件

    Args:
        widget: 要綁定的元件
        canvas: 可選的畫布元件
    """
    def on_mousewheel(event):
        if canvas:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif hasattr(widget, 'yview_scroll'):
            widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # 綁定不同平台的滾輪事件
    widget.bind("<MouseWheel>", on_mousewheel)  # Windows
    widget.bind("<Button-4>", lambda e: on_mousewheel(type('Event', (), {'delta': 120})()))  # Linux
    widget.bind("<Button-5>", lambda e: on_mousewheel(type('Event', (), {'delta': -120})()))  # Linux


def create_progress_dialog(parent: tk.Widget, title: str = "處理中",
                         message: str = "請稍候...") -> tuple[tk.Toplevel, ttk.Progressbar, tk.StringVar]:
    """
    建立進度對話框

    Args:
        parent: 父元件
        title: 對話框標題
        message: 顯示訊息

    Returns:
        (對話框, 進度條, 訊息變數) 元組
    """
    # 建立對話框
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    # 置中顯示
    center_window(dialog, 300, 100)

    # 建立訊息標籤
    message_var = tk.StringVar(value=message)
    message_label = ttk.Label(dialog, textvariable=message_var)
    message_label.pack(pady=10)

    # 建立進度條
    progress = ttk.Progressbar(dialog, mode='indeterminate', length=250)
    progress.pack(pady=10)
    progress.start()

    return dialog, progress, message_var


def format_number(number: int, use_comma: bool = True) -> str:
    """
    格式化數字顯示

    Args:
        number: 要格式化的數字
        use_comma: 是否使用千分位逗號

    Returns:
        格式化後的字串
    """
    if use_comma:
        return f"{number:,}"
    else:
        return str(number)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截斷過長的文字

    Args:
        text: 原始文字
        max_length: 最大長度
        suffix: 截斷後的後綴

    Returns:
        截斷後的文字
    """
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length - len(suffix)] + suffix


def validate_numeric_input(char: str) -> bool:
    """
    驗證數字輸入

    Args:
        char: 輸入的字元

    Returns:
        是否為有效的數字字元
    """
    return char.isdigit() or char in ".-"


def create_numeric_entry(parent: tk.Widget, **kwargs) -> ttk.Entry:
    """
    建立只能輸入數字的輸入框

    Args:
        parent: 父元件
        **kwargs: 其他參數

    Returns:
        數字輸入框
    """
    # 註冊驗證函數
    vcmd = (parent.register(validate_numeric_input), '%S')

    entry = ttk.Entry(parent, validate='key', validatecommand=vcmd, **kwargs)
    return entry


class AutoCompleteCombobox(ttk.Combobox):
    """自動完成下拉選單"""

    def __init__(self, parent, completevalues: List[str], **kwargs):
        """
        初始化自動完成下拉選單

        Args:
            parent: 父元件
            completevalues: 自動完成的值列表
            **kwargs: 其他參數
        """
        super().__init__(parent, **kwargs)
        self.completevalues = completevalues
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = tk.StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Return>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)

    def changed(self, name, index, mode):
        """文字變更事件"""
        if self.var.get() == '':
            self['values'] = self.completevalues
        else:
            words = []
            for element in self.completevalues:
                if element.lower().startswith(self.var.get().lower()):
                    words.append(element)
            self['values'] = words

    def selection(self, event):
        """選擇事件"""
        self.icursor(tk.END)

    def up(self, event):
        """向上鍵事件"""
        if self.current() > 0:
            self.current(self.current() - 1)

    def down(self, event):
        """向下鍵事件"""
        if self.current() < len(self['values']) - 1:
            self.current(self.current() + 1)