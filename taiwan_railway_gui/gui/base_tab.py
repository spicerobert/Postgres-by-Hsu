"""
基礎分頁元件

提供所有分頁元件的基礎類別和共用功能。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable
from taiwan_railway_gui.config import get_config
from taiwan_railway_gui.dao import get_database_manager
from taiwan_railway_gui.services.validation import create_validation_service
from taiwan_railway_gui.services.error_handler import get_error_handler, ErrorCategory, ErrorSeverity
from taiwan_railway_gui.gui.styles import get_style_manager
from taiwan_railway_gui.gui.accessibility import get_accessibility_helper


class BaseTab(ABC):
    """
    基礎分頁類別

    提供所有分頁元件的共用功能和介面。
    """

    def __init__(self, parent: tk.Widget, main_window=None):
        """
        初始化基礎分頁

        Args:
            parent: 父元件
            main_window: 主視窗參考
        """
        self.parent = parent
        self.main_window = main_window
        self.logger = logging.getLogger(self.__class__.__name__)

        # 載入配置
        self.colors = get_config('colors')
        self.fonts = get_config('fonts')
        self.layout = get_config('layout')
        self.error_messages = get_config('errors')

        # 初始化服務
        self.db_manager = get_database_manager()
        self.validation_service = create_validation_service()
        self.error_handler = get_error_handler()

        # 初始化樣式和無障礙功能
        self.style_manager = get_style_manager()
        self.accessibility = get_accessibility_helper()

        # 建立主框架
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # 初始化 UI
        self.setup_ui()

        self.logger.info(f"{self.__class__.__name__} 初始化完成")

    @abstractmethod
    def setup_ui(self):
        """設定使用者介面（子類別必須實作）"""
        pass

    def create_section_frame(self, parent: tk.Widget, title: str,
                           style: str = 'Card.TLabelFrame') -> ttk.LabelFrame:
        """
        建立區段框架

        Args:
            parent: 父元件
            title: 區段標題
            style: 框架樣式

        Returns:
            區段框架
        """
        # 建立主框架
        section_frame = ttk.LabelFrame(parent, text=title, style=style)

        # 添加無障礙支援
        self.accessibility.make_widget_accessible(
            section_frame,
            label=f"{title}區段",
            role="group"
        )

        return section_frame

    def create_input_frame(self, parent: tk.Widget) -> ttk.Frame:
        """
        建立輸入區域框架

        Args:
            parent: 父元件

        Returns:
            輸入框架
        """
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=self.layout['padding'])

        return input_frame

    def create_button_frame(self, parent: tk.Widget) -> ttk.Frame:
        """
        建立按鈕區域框架

        Args:
            parent: 父元件

        Returns:
            按鈕框架
        """
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=self.layout['padding'])

        return button_frame

    def create_results_frame(self, parent: tk.Widget) -> ttk.Frame:
        """
        建立結果顯示區域框架

        Args:
            parent: 父元件

        Returns:
            結果框架
        """
        results_frame = ttk.Frame(parent)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=self.layout['padding'], pady=self.layout['padding'])

        return results_frame

    def create_labeled_entry(self, parent: tk.Widget, label_text: str,
                           entry_width: Optional[int] = None) -> tuple[ttk.Label, ttk.Entry]:
        """
        建立帶標籤的輸入框

        Args:
            parent: 父元件
            label_text: 標籤文字
            entry_width: 輸入框寬度

        Returns:
            (標籤, 輸入框) 元組
        """
        label = ttk.Label(parent, text=label_text)

        width = entry_width or self.layout['entry_width']
        entry = ttk.Entry(parent, width=width)

        # 添加無障礙支援
        self.accessibility.make_widget_accessible(
            entry,
            label=label_text,
            description=f"輸入{label_text}",
            role="textbox"
        )

        # 添加焦點效果
        self.style_manager.create_focus_effect(entry)

        # 如果是主視窗，添加到鍵盤導航
        if self.main_window and hasattr(self.main_window, 'keyboard_nav'):
            self.main_window.keyboard_nav.add_to_focus_ring(entry)

        return label, entry

    def create_labeled_combobox(self, parent: tk.Widget, label_text: str,
                              values: list, width: Optional[int] = None) -> tuple[ttk.Label, ttk.Combobox]:
        """
        建立帶標籤的下拉選單

        Args:
            parent: 父元件
            label_text: 標籤文字
            values: 選項值列表
            width: 下拉選單寬度

        Returns:
            (標籤, 下拉選單) 元組
        """
        label = ttk.Label(parent, text=label_text)

        combo_width = width or self.layout['entry_width']
        combobox = ttk.Combobox(parent, values=values, width=combo_width, state='readonly')

        # 添加無障礙支援
        self.accessibility.make_widget_accessible(
            combobox,
            label=label_text,
            description=f"選擇{label_text}",
            role="combobox"
        )

        # 添加焦點效果
        self.style_manager.create_focus_effect(combobox)

        # 如果是主視窗，添加到鍵盤導航
        if self.main_window and hasattr(self.main_window, 'keyboard_nav'):
            self.main_window.keyboard_nav.add_to_focus_ring(combobox)

        return label, combobox

    def create_styled_button(self, parent: tk.Widget, text: str, command: Callable,
                           style: str = 'Primary.TButton', width: Optional[int] = None) -> ttk.Button:
        """
        建立樣式化按鈕

        Args:
            parent: 父元件
            text: 按鈕文字
            command: 點擊回調
            style: 按鈕樣式
            width: 按鈕寬度

        Returns:
            樣式化按鈕
        """
        button_width = width or self.layout['button_width']
        button = ttk.Button(parent, text=text, command=command,
                          style=style, width=button_width)

        # 添加無障礙支援
        self.accessibility.make_widget_accessible(
            button,
            label=text,
            description=f"點擊{text}",
            role="button"
        )

        # 添加懸停效果
        theme = self.style_manager.get_theme()
        colors = theme['colors']

        if style == 'Primary.TButton':
            hover_color = colors['primary_light']
            normal_color = colors['primary']
        elif style == 'Secondary.TButton':
            hover_color = colors['hover']
            normal_color = colors['secondary']
        else:
            hover_color = colors['hover']
            normal_color = colors['background']

        # 如果是主視窗，添加到鍵盤導航
        if self.main_window and hasattr(self.main_window, 'keyboard_nav'):
            self.main_window.keyboard_nav.add_to_focus_ring(button)

        return button

    def create_scrollable_listbox(self, parent: tk.Widget, height: Optional[int] = None) -> tuple[tk.Listbox, ttk.Scrollbar]:
        """
        建立可捲動的清單框

        Args:
            parent: 父元件
            height: 清單框高度

        Returns:
            (清單框, 捲軸) 元組
        """
        # 建立框架
        listbox_frame = ttk.Frame(parent)

        # 建立清單框
        listbox_height = height or self.layout['listbox_height']

        # 使用樣式管理器建立清單框
        theme = self.style_manager.get_theme()
        colors = theme['colors']
        fonts = theme['fonts']

        listbox = tk.Listbox(listbox_frame,
                           height=listbox_height,
                           font=fonts['body'],
                           background=colors['background'],
                           foreground=colors['text'],
                           selectbackground=colors['primary'],
                           selectforeground=colors['background'],
                           borderwidth=1,
                           relief='solid')

        # 建立捲軸
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)

        # 佈局
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        # 添加無障礙支援
        self.accessibility.make_widget_accessible(
            listbox,
            label="清單",
            description="使用方向鍵導航，Enter 選擇",
            role="listbox"
        )

        # 如果是主視窗，添加到鍵盤導航
        if self.main_window and hasattr(self.main_window, 'keyboard_nav'):
            self.main_window.keyboard_nav.add_to_focus_ring(listbox)

        return listbox, scrollbar

    def create_treeview_with_scrollbar(self, parent: tk.Widget, columns: list,
                                     headings: list) -> tuple[ttk.Treeview, ttk.Scrollbar]:
        """
        建立帶捲軸的樹狀檢視

        Args:
            parent: 父元件
            columns: 欄位列表
            headings: 標題列表

        Returns:
            (樹狀檢視, 捲軸) 元組
        """
        # 建立框架
        tree_frame = ttk.Frame(parent)

        # 建立樹狀檢視
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        # 設定標題
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=100, anchor=tk.CENTER)

        # 建立捲軸
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.config(yscrollcommand=scrollbar.set)

        # 佈局
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        return tree, scrollbar

    def show_error_message(self, title: str, message: str, error: Exception = None):
        """
        顯示錯誤訊息

        Args:
            title: 錯誤標題
            message: 錯誤訊息
            error: 原始錯誤物件（可選）
        """
        if error:
            # 使用錯誤處理器處理錯誤
            error_info = self.error_handler.handle_error(
                error,
                context={"title": title, "component": self.__class__.__name__},
                category=ErrorCategory.GUI
            )
            # 顯示使用者友善的錯誤訊息
            messagebox.showerror(title, error_info.user_message)

            # 如果有建議動作，顯示提示
            if error_info.suggested_actions:
                suggestions = "\n".join([f"• {action}" for action in error_info.suggested_actions])
                messagebox.showinfo("建議解決方案", f"您可以嘗試以下方法：\n\n{suggestions}")
        else:
            # 傳統錯誤顯示
            self.logger.error(f"{title}: {message}")
            messagebox.showerror(title, message)

    def show_info_message(self, title: str, message: str):
        """
        顯示資訊訊息

        Args:
            title: 訊息標題
            message: 訊息內容
        """
        self.logger.info(f"{title}: {message}")
        messagebox.showinfo(title, message)

    def show_warning_message(self, title: str, message: str):
        """
        顯示警告訊息

        Args:
            title: 警告標題
            message: 警告訊息
        """
        self.logger.warning(f"{title}: {message}")
        messagebox.showwarning(title, message)

    def run_async_task(self, task: Callable, callback: Optional[Callable] = None,
                      loading_message: str = "處理中..."):
        """
        執行非同步任務（帶錯誤處理）

        Args:
            task: 要執行的任務函數
            callback: 任務完成後的回調函數
            loading_message: 載入訊息
        """
        def wrapped_task():
            try:
                return task()
            except Exception as e:
                # 使用錯誤處理器處理錯誤
                error_info = self.error_handler.handle_error(
                    e,
                    context={
                        "task": task.__name__ if hasattr(task, '__name__') else str(task),
                        "component": self.__class__.__name__,
                        "loading_message": loading_message
                    }
                )
                raise e  # 重新拋出錯誤以便上層處理

        def wrapped_callback(result):
            try:
                if callback:
                    callback(result)
            except Exception as e:
                # 回調函數錯誤處理
                self.show_error_message("回調錯誤", "處理結果時發生錯誤", e)

        if self.main_window:
            self.main_window.run_async_task(wrapped_task, wrapped_callback, loading_message)
        else:
            # 如果沒有主視窗參考，直接執行任務
            try:
                result = wrapped_task()
                wrapped_callback(result)
            except Exception as e:
                self.show_error_message("執行錯誤", "任務執行失敗", e)

    def validate_input(self, value: Any, validator_method: str, *args) -> tuple[bool, str]:
        """
        驗證輸入值（增強版）

        Args:
            value: 要驗證的值
            validator_method: 驗證方法名稱
            *args: 驗證方法的額外參數

        Returns:
            (是否有效, 錯誤訊息) 元組
        """
        try:
            # 嘗試使用增強驗證方法
            if hasattr(self.validation_service, 'validate_with_level'):
                from taiwan_railway_gui.services.validation import ValidationLevel
                result = self.validation_service.validate_with_level(
                    value, validator_method, ValidationLevel.BUSINESS
                )

                # 顯示警告（如果有）
                if result.warnings:
                    warning_msg = "\n".join(result.warnings)
                    self.show_warning_message("驗證警告", warning_msg)

                return result.is_valid, result.error_message
            else:
                # 回退到傳統驗證方法
                validator = getattr(self.validation_service, validator_method)
                return validator(value, *args)

        except AttributeError:
            error_msg = f"找不到驗證方法: {validator_method}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            # 使用錯誤處理器處理驗證錯誤
            error_info = self.error_handler.handle_error(
                e,
                context={
                    "validator_method": validator_method,
                    "value": str(value)[:100],  # 限制長度避免日誌過長
                    "component": self.__class__.__name__
                },
                category=ErrorCategory.VALIDATION
            )
            return False, error_info.user_message

    def validate_input_enhanced(self, value: Any, validation_type: str,
                              level: str = "business") -> Dict[str, Any]:
        """
        增強的輸入驗證（返回詳細結果）

        Args:
            value: 要驗證的值
            validation_type: 驗證類型
            level: 驗證層級

        Returns:
            Dict: 包含驗證結果的詳細資訊
        """
        try:
            from taiwan_railway_gui.services.validation import ValidationLevel

            # 轉換驗證層級
            level_map = {
                "basic": ValidationLevel.BASIC,
                "business": ValidationLevel.BUSINESS,
                "strict": ValidationLevel.STRICT
            }
            validation_level = level_map.get(level, ValidationLevel.BUSINESS)

            # 執行驗證
            result = self.validation_service.validate_with_level(
                value, validation_type, validation_level
            )

            return {
                "is_valid": result.is_valid,
                "error_message": result.error_message,
                "error_code": result.error_code,
                "suggestions": result.suggestions,
                "warnings": result.warnings,
                "corrected_value": result.corrected_value
            }

        except Exception as e:
            error_info = self.error_handler.handle_error(
                e,
                context={
                    "validation_type": validation_type,
                    "level": level,
                    "component": self.__class__.__name__
                },
                category=ErrorCategory.VALIDATION
            )

            return {
                "is_valid": False,
                "error_message": error_info.user_message,
                "error_code": "validation_error",
                "suggestions": error_info.suggested_actions,
                "warnings": [],
                "corrected_value": None
            }

    def handle_graceful_degradation(self, error: Exception, fallback_action: Callable = None):
        """
        處理優雅降級

        Args:
            error: 發生的錯誤
            fallback_action: 降級時執行的動作
        """
        try:
            # 使用錯誤處理器處理錯誤
            error_info = self.error_handler.handle_error(
                error,
                context={"component": self.__class__.__name__},
                severity=ErrorSeverity.MEDIUM
            )

            # 顯示錯誤訊息
            self.show_error_message("系統錯誤", error_info.user_message)

            # 執行降級動作
            if fallback_action:
                try:
                    fallback_action()
                except Exception as fallback_error:
                    self.logger.error(f"降級動作執行失敗: {fallback_error}")
                    self.show_warning_message("降級失敗", "系統嘗試恢復時發生錯誤，請重新啟動應用程式")

        except Exception as handler_error:
            # 錯誤處理器本身失敗時的最後手段
            self.logger.critical(f"錯誤處理器失敗: {handler_error}")
            messagebox.showerror("嚴重錯誤", "系統發生嚴重錯誤，請重新啟動應用程式")

    def show_validation_feedback(self, validation_result: Dict[str, Any], field_name: str = ""):
        """
        顯示驗證回饋

        Args:
            validation_result: 驗證結果
            field_name: 欄位名稱
        """
        if not validation_result["is_valid"]:
            # 顯示錯誤訊息
            title = f"{field_name}驗證錯誤" if field_name else "驗證錯誤"
            messagebox.showerror(title, validation_result["error_message"])

            # 顯示建議
            if validation_result["suggestions"]:
                suggestions = "\n".join([f"• {s}" for s in validation_result["suggestions"]])
                messagebox.showinfo("建議", f"請嘗試以下方法：\n\n{suggestions}")

        # 顯示警告
        if validation_result["warnings"]:
            warnings = "\n".join([f"• {w}" for w in validation_result["warnings"]])
            messagebox.showwarning("注意", f"請注意：\n\n{warnings}")

        # 提供修正值
        if validation_result["corrected_value"] is not None:
            response = messagebox.askyesno(
                "自動修正",
                f"系統建議將輸入修正為：{validation_result['corrected_value']}\n\n是否接受此修正？"
            )
            if response:
                return validation_result["corrected_value"]

        return None

    def clear_results(self):
        """清除結果顯示（子類別可覆寫）"""
        pass

    def refresh_data(self):
        """重新整理資料（子類別可覆寫）"""
        pass

    def export_data(self):
        """匯出資料（子類別可覆寫）"""
        self.show_info_message("匯出", "此分頁的匯出功能尚未實作")

    def get_frame(self) -> ttk.Frame:
        """取得分頁框架"""
        return self.frame