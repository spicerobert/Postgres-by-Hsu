"""
使用者回饋系統

提供統一的使用者回饋介面，包括錯誤顯示、進度指示、
狀態通知和互動式回饋元件。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Optional, Callable, List, Dict, Any
from enum import Enum
from dataclasses import dataclass
from taiwan_railway_gui.config import get_config


class FeedbackType(Enum):
    """回饋類型"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"


class NotificationPosition(Enum):
    """通知位置"""
    TOP_RIGHT = "top_right"
    TOP_LEFT = "top_left"
    BOTTOM_RIGHT = "bottom_right"
    BOTTOM_LEFT = "bottom_left"
    CENTER = "center"


@dataclass
class FeedbackMessage:
    """回饋訊息"""
    message: str
    feedback_type: FeedbackType
    title: str = ""
    duration: int = 3000  # 毫秒
    actions: List[Dict[str, Any]] = None
    auto_dismiss: bool = True


class ToastNotification:
    """吐司通知元件"""

    def __init__(self, parent: tk.Widget, message: FeedbackMessage,
                 position: NotificationPosition = NotificationPosition.TOP_RIGHT):
        """
        初始化吐司通知

        Args:
            parent: 父元件
            message: 回饋訊息
            position: 顯示位置
        """
        self.parent = parent
        self.message = message
        self.position = position
        self.colors = get_config('colors')

        # 建立通知視窗
        self.toast_window = tk.Toplevel(parent)
        self.toast_window.withdraw()  # 先隱藏
        self.setup_window()
        self.create_content()
        self.position_window()

        # 顯示動畫
        self.show_animation()

        # 自動消失
        if message.auto_dismiss:
            self.parent.after(message.duration, self.hide_animation)

    def setup_window(self):
        """設定視窗屬性"""
        self.toast_window.overrideredirect(True)  # 無邊框
        self.toast_window.attributes('-topmost', True)  # 置頂

        # 設定背景色
        bg_colors = {
            FeedbackType.INFO: self.colors.get('info', '#2196F3'),
            FeedbackType.SUCCESS: self.colors.get('success', '#4CAF50'),
            FeedbackType.WARNING: self.colors.get('warning', '#FF9800'),
            FeedbackType.ERROR: self.colors.get('error', '#F44336'),
            FeedbackType.QUESTION: self.colors.get('question', '#9C27B0')
        }

        self.bg_color = bg_colors.get(self.message.feedback_type, '#2196F3')
        self.toast_window.configure(bg=self.bg_color)

    def create_content(self):
        """建立內容"""
        # 主框架
        main_frame = tk.Frame(self.toast_window, bg=self.bg_color, padx=15, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 圖示（可選）
        icon_text = self.get_icon_text()
        if icon_text:
            icon_label = tk.Label(
                main_frame,
                text=icon_text,
                bg=self.bg_color,
                fg='white',
                font=('Arial', 12, 'bold')
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 10))

        # 訊息內容
        content_frame = tk.Frame(main_frame, bg=self.bg_color)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 標題
        if self.message.title:
            title_label = tk.Label(
                content_frame,
                text=self.message.title,
                bg=self.bg_color,
                fg='white',
                font=('Arial', 10, 'bold')
            )
            title_label.pack(anchor=tk.W)

        # 訊息
        message_label = tk.Label(
            content_frame,
            text=self.message.message,
            bg=self.bg_color,
            fg='white',
            font=('Arial', 9),
            wraplength=300,
            justify=tk.LEFT
        )
        message_label.pack(anchor=tk.W)

        # 動作按鈕
        if self.message.actions:
            button_frame = tk.Frame(content_frame, bg=self.bg_color)
            button_frame.pack(anchor=tk.W, pady=(5, 0))

            for action in self.message.actions:
                btn = tk.Button(
                    button_frame,
                    text=action.get('text', '確定'),
                    command=lambda a=action: self.handle_action(a),
                    bg='white',
                    fg=self.bg_color,
                    font=('Arial', 8),
                    relief=tk.FLAT,
                    padx=10,
                    pady=2
                )
                btn.pack(side=tk.LEFT, padx=(0, 5))

        # 關閉按鈕
        close_btn = tk.Button(
            main_frame,
            text='×',
            command=self.hide_animation,
            bg=self.bg_color,
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            width=2,
            height=1
        )
        close_btn.pack(side=tk.RIGHT, anchor=tk.NE)

    def get_icon_text(self) -> str:
        """取得圖示文字"""
        icons = {
            FeedbackType.INFO: 'ℹ',
            FeedbackType.SUCCESS: '✓',
            FeedbackType.WARNING: '⚠',
            FeedbackType.ERROR: '✗',
            FeedbackType.QUESTION: '?'
        }
        return icons.get(self.message.feedback_type, '')

    def position_window(self):
        """定位視窗"""
        self.toast_window.update_idletasks()

        # 取得視窗大小
        width = self.toast_window.winfo_reqwidth()
        height = self.toast_window.winfo_reqheight()

        # 取得父視窗位置和大小
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        # 計算位置
        positions = {
            NotificationPosition.TOP_RIGHT: (
                parent_x + parent_width - width - 20,
                parent_y + 20
            ),
            NotificationPosition.TOP_LEFT: (
                parent_x + 20,
                parent_y + 20
            ),
            NotificationPosition.BOTTOM_RIGHT: (
                parent_x + parent_width - width - 20,
                parent_y + parent_height - height - 20
            ),
            NotificationPosition.BOTTOM_LEFT: (
                parent_x + 20,
                parent_y + parent_height - height - 20
            ),
            NotificationPosition.CENTER: (
                parent_x + (parent_width - width) // 2,
                parent_y + (parent_height - height) // 2
            )
        }

        x, y = positions.get(self.position, positions[NotificationPosition.TOP_RIGHT])
        self.toast_window.geometry(f"{width}x{height}+{x}+{y}")

    def show_animation(self):
        """顯示動畫"""
        self.toast_window.deiconify()
        self.toast_window.attributes('-alpha', 0.0)

        # 淡入動畫
        def fade_in(alpha=0.0):
            if alpha < 1.0:
                alpha += 0.1
                self.toast_window.attributes('-alpha', alpha)
                self.parent.after(20, lambda: fade_in(alpha))

        fade_in()

    def hide_animation(self):
        """隱藏動畫"""
        def fade_out(alpha=1.0):
            if alpha > 0.0:
                alpha -= 0.1
                self.toast_window.attributes('-alpha', alpha)
                self.parent.after(20, lambda: fade_out(alpha))
            else:
                self.toast_window.destroy()

        fade_out()

    def handle_action(self, action: Dict[str, Any]):
        """處理動作"""
        callback = action.get('callback')
        if callback:
            try:
                callback()
            except Exception as e:
                print(f"動作回調執行失敗: {e}")

        # 關閉通知
        self.hide_animation()


class ProgressDialog:
    """進度對話框"""

    def __init__(self, parent: tk.Widget, title: str = "處理中...",
                 message: str = "請稍候...", cancelable: bool = False):
        """
        初始化進度對話框

        Args:
            parent: 父元件
            title: 對話框標題
            message: 顯示訊息
            cancelable: 是否可取消
        """
        self.parent = parent
        self.title = title
        self.message = message
        self.cancelable = cancelable
        self.cancelled = False
        self.cancel_callback = None

        # 建立對話框
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_content()

    def setup_dialog(self):
        """設定對話框"""
        self.dialog.title(self.title)
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 置中顯示
        self.dialog.update_idletasks()
        width = 300
        height = 120
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

        # 禁用關閉按鈕（除非可取消）
        if not self.cancelable:
            self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)

    def create_content(self):
        """建立內容"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 訊息標籤
        self.message_var = tk.StringVar(value=self.message)
        message_label = ttk.Label(
            main_frame,
            textvariable=self.message_var,
            font=('Arial', 10)
        )
        message_label.pack(pady=(0, 10))

        # 進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        self.progress_bar.start(10)

        # 取消按鈕
        if self.cancelable:
            cancel_btn = ttk.Button(
                main_frame,
                text="取消",
                command=self.cancel
            )
            cancel_btn.pack()

    def update_message(self, message: str):
        """更新訊息"""
        self.message_var.set(message)
        self.dialog.update()

    def update_progress(self, value: float):
        """更新進度（0-100）"""
        self.progress_bar.config(mode='determinate')
        self.progress_var.set(value)
        self.dialog.update()

    def set_cancel_callback(self, callback: Callable):
        """設定取消回調"""
        self.cancel_callback = callback

    def cancel(self):
        """取消操作"""
        self.cancelled = True
        if self.cancel_callback:
            self.cancel_callback()
        self.close()

    def close(self):
        """關閉對話框"""
        self.progress_bar.stop()
        self.dialog.destroy()

    def is_cancelled(self) -> bool:
        """檢查是否已取消"""
        return self.cancelled


class UserFeedbackManager:
    """使用者回饋管理器"""

    def __init__(self, parent: tk.Widget):
        """
        初始化回饋管理器

        Args:
            parent: 父元件
        """
        self.parent = parent
        self.active_notifications = []
        self.active_dialogs = []

    def show_toast(self, message: str, feedback_type: FeedbackType = FeedbackType.INFO,
                   title: str = "", duration: int = 3000,
                   position: NotificationPosition = NotificationPosition.TOP_RIGHT,
                   actions: List[Dict[str, Any]] = None):
        """
        顯示吐司通知

        Args:
            message: 訊息內容
            feedback_type: 回饋類型
            title: 標題
            duration: 顯示時間（毫秒）
            position: 顯示位置
            actions: 動作按鈕
        """
        feedback_message = FeedbackMessage(
            message=message,
            feedback_type=feedback_type,
            title=title,
            duration=duration,
            actions=actions or []
        )

        toast = ToastNotification(self.parent, feedback_message, position)
        self.active_notifications.append(toast)

    def show_success(self, message: str, title: str = "成功"):
        """顯示成功訊息"""
        self.show_toast(message, FeedbackType.SUCCESS, title)

    def show_error(self, message: str, title: str = "錯誤",
                   suggestions: List[str] = None):
        """顯示錯誤訊息"""
        actions = []
        if suggestions:
            actions.append({
                'text': '查看建議',
                'callback': lambda: self.show_suggestions_dialog(suggestions)
            })

        self.show_toast(message, FeedbackType.ERROR, title, duration=5000, actions=actions)

    def show_warning(self, message: str, title: str = "警告"):
        """顯示警告訊息"""
        self.show_toast(message, FeedbackType.WARNING, title, duration=4000)

    def show_info(self, message: str, title: str = "資訊"):
        """顯示資訊訊息"""
        self.show_toast(message, FeedbackType.INFO, title)

    def show_progress_dialog(self, title: str = "處理中...",
                           message: str = "請稍候...",
                           cancelable: bool = False) -> ProgressDialog:
        """
        顯示進度對話框

        Args:
            title: 對話框標題
            message: 顯示訊息
            cancelable: 是否可取消

        Returns:
            ProgressDialog: 進度對話框實例
        """
        dialog = ProgressDialog(self.parent, title, message, cancelable)
        self.active_dialogs.append(dialog)
        return dialog

    def show_confirmation_dialog(self, message: str, title: str = "確認",
                                callback: Callable[[bool], None] = None) -> bool:
        """
        顯示確認對話框

        Args:
            message: 確認訊息
            title: 對話框標題
            callback: 結果回調函數

        Returns:
            bool: 使用者選擇結果
        """
        result = messagebox.askyesno(title, message)
        if callback:
            callback(result)
        return result

    def show_input_dialog(self, message: str, title: str = "輸入",
                         default_value: str = "") -> Optional[str]:
        """
        顯示輸入對話框

        Args:
            message: 提示訊息
            title: 對話框標題
            default_value: 預設值

        Returns:
            Optional[str]: 使用者輸入的值
        """
        from tkinter import simpledialog
        return simpledialog.askstring(title, message, initialvalue=default_value)

    def show_suggestions_dialog(self, suggestions: List[str]):
        """
        顯示建議對話框

        Args:
            suggestions: 建議列表
        """
        suggestions_text = "\n".join([f"• {suggestion}" for suggestion in suggestions])
        messagebox.showinfo("建議解決方案", f"您可以嘗試以下方法：\n\n{suggestions_text}")

    def show_error_details_dialog(self, error_info: Dict[str, Any]):
        """
        顯示錯誤詳細資訊對話框

        Args:
            error_info: 錯誤資訊
        """
        # 建立詳細錯誤對話框
        dialog = tk.Toplevel(self.parent)
        dialog.title("錯誤詳細資訊")
        dialog.geometry("500x400")
        dialog.transient(self.parent)

        # 建立內容
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 錯誤資訊
        info_text = tk.Text(main_frame, wrap=tk.WORD, height=15)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=info_text.yview)
        info_text.config(yscrollcommand=scrollbar.set)

        # 填入錯誤資訊
        error_details = f"""錯誤 ID: {error_info.get('error_id', 'N/A')}
類別: {error_info.get('category', 'N/A')}
嚴重程度: {error_info.get('severity', 'N/A')}
時間: {error_info.get('timestamp', 'N/A')}

使用者訊息:
{error_info.get('user_message', 'N/A')}

技術訊息:
{error_info.get('technical_message', 'N/A')}

建議動作:
{chr(10).join(['• ' + action for action in error_info.get('suggested_actions', [])])}

堆疊追蹤:
{error_info.get('stack_trace', 'N/A')}"""

        info_text.insert(tk.END, error_details)
        info_text.config(state=tk.DISABLED)

        info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按鈕框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 複製按鈕
        def copy_to_clipboard():
            dialog.clipboard_clear()
            dialog.clipboard_append(error_details)
            self.show_info("錯誤資訊已複製到剪貼簿")

        copy_btn = ttk.Button(button_frame, text="複製", command=copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 關閉按鈕
        close_btn = ttk.Button(button_frame, text="關閉", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT)

    def clear_all_notifications(self):
        """清除所有通知"""
        for notification in self.active_notifications:
            try:
                notification.hide_animation()
            except:
                pass
        self.active_notifications.clear()

    def close_all_dialogs(self):
        """關閉所有對話框"""
        for dialog in self.active_dialogs:
            try:
                dialog.close()
            except:
                pass
        self.active_dialogs.clear()


def create_user_feedback_manager(parent: tk.Widget) -> UserFeedbackManager:
    """建立使用者回饋管理器實例"""
    return UserFeedbackManager(parent)