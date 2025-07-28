"""
無障礙功能和鍵盤導航

提供無障礙功能支援和鍵盤導航系統。
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional, Callable
from taiwan_railway_gui.gui.styles import get_style_manager


class KeyboardNavigationManager:
    """鍵盤導航管理器"""

    def __init__(self, root: tk.Widget):
        """初始化鍵盤導航管理器"""
        self.root = root
        self.style_manager = get_style_manager()

        # 導航歷史
        self.navigation_history = []
        self.current_index = -1

        # 快捷鍵映射
        self.shortcuts = {}

        # 焦點環
        self.focus_ring = []
        self.current_focus_index = 0

        # 設定全域快捷鍵
        self.setup_global_shortcuts()

    def setup_global_shortcuts(self):
        """設定全域快捷鍵"""
        # Tab 循環導航
        self.root.bind('<Tab>', self.next_focus)
        self.root.bind('<Shift-Tab>', self.previous_focus)

        # 方向鍵導航
        self.root.bind('<Up>', self.navigate_up)
        self.root.bind('<Down>', self.navigate_down)
        self.root.bind('<Left>', self.navigate_left)
        self.root.bind('<Right>', self.navigate_right)

        # Enter 和 Space 激活
        self.root.bind('<Return>', self.activate_current)
        self.root.bind('<space>', self.activate_current)

        # Escape 取消
        self.root.bind('<Escape>', self.cancel_current)

        # Alt + 數字鍵快速導航
        for i in range(1, 10):
            self.root.bind(f'<Alt-{i}>', lambda e, idx=i-1: self.quick_navigate(idx))

        # Ctrl + 快捷鍵
        self.root.bind('<Control-f>', self.focus_search)
        self.root.bind('<Control-r>', self.refresh_current)
        self.root.bind('<Control-e>', self.export_current)
        self.root.bind('<Control-h>', self.show_help)

    def register_shortcut(self, key_combination: str, callback: Callable, description: str = ""):
        """
        註冊快捷鍵

        Args:
            key_combination: 按鍵組合（如 '<Control-s>'）
            callback: 回調函數
            description: 快捷鍵描述
        """
        self.shortcuts[key_combination] = {
            'callback': callback,
            'description': description
        }
        self.root.bind(key_combination, lambda e: callback())

    def add_to_focus_ring(self, widget: tk.Widget, priority: int = 0):
        """
        添加元件到焦點環

        Args:
            widget: 要添加的元件
            priority: 優先級（數字越小優先級越高）
        """
        self.focus_ring.append({
            'widget': widget,
            'priority': priority
        })

        # 按優先級排序
        self.focus_ring.sort(key=lambda x: x['priority'])

        # 為元件添加焦點事件
        widget.bind('<FocusIn>', self.on_focus_in)
        widget.bind('<FocusOut>', self.on_focus_out)

    def next_focus(self, event=None):
        """移動到下一個焦點"""
        if not self.focus_ring:
            return

        self.current_focus_index = (self.current_focus_index + 1) % len(self.focus_ring)
        widget = self.focus_ring[self.current_focus_index]['widget']

        try:
            widget.focus_set()
        except tk.TclError:
            # 元件可能已被銷毀，移除並重試
            self.focus_ring.pop(self.current_focus_index)
            if self.focus_ring:
                self.next_focus()

    def previous_focus(self, event=None):
        """移動到上一個焦點"""
        if not self.focus_ring:
            return

        self.current_focus_index = (self.current_focus_index - 1) % len(self.focus_ring)
        widget = self.focus_ring[self.current_focus_index]['widget']

        try:
            widget.focus_set()
        except tk.TclError:
            # 元件可能已被銷毀，移除並重試
            self.focus_ring.pop(self.current_focus_index)
            if self.focus_ring:
                self.previous_focus()

    def navigate_up(self, event=None):
        """向上導航"""
        current_widget = self.root.focus_get()
        if isinstance(current_widget, tk.Listbox):
            # 在列表框中向上移動
            current_selection = current_widget.curselection()
            if current_selection:
                new_index = max(0, current_selection[0] - 1)
                current_widget.selection_clear(0, tk.END)
                current_widget.selection_set(new_index)
                current_widget.see(new_index)
        elif isinstance(current_widget, ttk.Treeview):
            # 在樹狀檢視中向上移動
            current_item = current_widget.selection()
            if current_item:
                prev_item = current_widget.prev(current_item[0])
                if prev_item:
                    current_widget.selection_set(prev_item)
                    current_widget.see(prev_item)

    def navigate_down(self, event=None):
        """向下導航"""
        current_widget = self.root.focus_get()
        if isinstance(current_widget, tk.Listbox):
            # 在列表框中向下移動
            current_selection = current_widget.curselection()
            if current_selection:
                new_index = min(current_widget.size() - 1, current_selection[0] + 1)
                current_widget.selection_clear(0, tk.END)
                current_widget.selection_set(new_index)
                current_widget.see(new_index)
        elif isinstance(current_widget, ttk.Treeview):
            # 在樹狀檢視中向下移動
            current_item = current_widget.selection()
            if current_item:
                next_item = current_widget.next(current_item[0])
                if next_item:
                    current_widget.selection_set(next_item)
                    current_widget.see(next_item)

    def navigate_left(self, event=None):
        """向左導航"""
        current_widget = self.root.focus_get()
        if isinstance(current_widget, ttk.Notebook):
            # 在分頁中向左切換
            current_tab = current_widget.index(current_widget.select())
            if current_tab > 0:
                current_widget.select(current_tab - 1)

    def navigate_right(self, event=None):
        """向右導航"""
        current_widget = self.root.focus_get()
        if isinstance(current_widget, ttk.Notebook):
            # 在分頁中向右切換
            current_tab = current_widget.index(current_widget.select())
            if current_tab < len(current_widget.tabs()) - 1:
                current_widget.select(current_tab + 1)

    def activate_current(self, event=None):
        """激活當前元件"""
        current_widget = self.root.focus_get()
        if isinstance(current_widget, (tk.Button, ttk.Button)):
            current_widget.invoke()
        elif isinstance(current_widget, tk.Listbox):
            # 觸發雙擊事件
            current_widget.event_generate('<Double-Button-1>')
        elif isinstance(current_widget, ttk.Treeview):
            # 觸發雙擊事件
            current_widget.event_generate('<Double-Button-1>')

    def cancel_current(self, event=None):
        """取消當前操作"""
        # 可以由各個元件自行處理
        pass

    def quick_navigate(self, index: int):
        """快速導航到指定索引"""
        if 0 <= index < len(self.focus_ring):
            self.current_focus_index = index
            widget = self.focus_ring[index]['widget']
            try:
                widget.focus_set()
            except tk.TclError:
                pass

    def focus_search(self, event=None):
        """聚焦到搜尋框"""
        # 尋找搜尋相關的元件
        for item in self.focus_ring:
            widget = item['widget']
            if isinstance(widget, (tk.Entry, ttk.Entry)):
                # 檢查是否為搜尋框（通過名稱或標籤判斷）
                widget_name = str(widget).lower()
                if 'search' in widget_name or '搜尋' in widget_name:
                    widget.focus_set()
                    return

    def refresh_current(self, event=None):
        """重新整理當前內容"""
        # 觸發重新整理事件
        self.root.event_generate('<<Refresh>>')

    def export_current(self, event=None):
        """匯出當前內容"""
        # 觸發匯出事件
        self.root.event_generate('<<Export>>')

    def show_help(self, event=None):
        """顯示說明"""
        # 觸發說明事件
        self.root.event_generate('<<ShowHelp>>')

    def on_focus_in(self, event):
        """焦點進入事件"""
        widget = event.widget

        # 添加焦點視覺效果
        self.style_manager.create_focus_effect(widget)

        # 更新當前焦點索引
        for i, item in enumerate(self.focus_ring):
            if item['widget'] == widget:
                self.current_focus_index = i
                break

    def on_focus_out(self, event):
        """焦點離開事件"""
        # 移除焦點視覺效果（如果需要）
        pass

    def get_shortcuts_help(self) -> str:
        """取得快捷鍵說明"""
        help_text = "鍵盤快捷鍵:\n\n"

        # 基本導航
        help_text += "基本導航:\n"
        help_text += "  Tab / Shift+Tab - 下一個/上一個元件\n"
        help_text += "  方向鍵 - 在列表和分頁中導航\n"
        help_text += "  Enter / Space - 激活當前元件\n"
        help_text += "  Escape - 取消當前操作\n\n"

        # 快速導航
        help_text += "快速導航:\n"
        help_text += "  Alt+1~9 - 快速跳轉到指定元件\n"
        help_text += "  Ctrl+F - 聚焦搜尋框\n\n"

        # 功能快捷鍵
        help_text += "功能快捷鍵:\n"
        help_text += "  Ctrl+R - 重新整理\n"
        help_text += "  Ctrl+E - 匯出資料\n"
        help_text += "  Ctrl+H - 顯示說明\n\n"

        # 自訂快捷鍵
        if self.shortcuts:
            help_text += "自訂快捷鍵:\n"
            for key, info in self.shortcuts.items():
                if info['description']:
                    help_text += f"  {key} - {info['description']}\n"

        return help_text


class AccessibilityHelper:
    """無障礙輔助工具"""

    def __init__(self):
        """初始化無障礙輔助工具"""
        self.style_manager = get_style_manager()
        self.high_contrast_mode = False
        self.large_font_mode = False
        self.screen_reader_mode = False

    def enable_high_contrast(self):
        """啟用高對比模式"""
        self.high_contrast_mode = True
        self.style_manager.set_theme('high_contrast')

    def disable_high_contrast(self):
        """停用高對比模式"""
        self.high_contrast_mode = False
        self.style_manager.set_theme('default')

    def enable_large_fonts(self):
        """啟用大字體模式"""
        self.large_font_mode = True
        # 增加字體大小
        theme = self.style_manager.get_theme()
        fonts = theme['fonts']

        # 放大所有字體
        for font_name, (family, size, weight) in fonts.items():
            fonts[font_name] = (family, int(size * 1.2), weight)

    def disable_large_fonts(self):
        """停用大字體模式"""
        self.large_font_mode = False
        # 恢復原始字體大小
        self.style_manager.set_theme(self.style_manager.current_theme)

    def add_aria_label(self, widget: tk.Widget, label: str):
        """
        為元件添加 ARIA 標籤（螢幕閱讀器支援）

        Args:
            widget: 目標元件
            label: ARIA 標籤文字
        """
        # 在 tkinter 中，我們可以使用工具提示來模擬 ARIA 標籤
        self.create_accessible_tooltip(widget, label)

    def create_accessible_tooltip(self, widget: tk.Widget, text: str):
        """
        建立無障礙工具提示

        Args:
            widget: 目標元件
            text: 提示文字
        """
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(tooltip, text=text,
                           background='#FFFFDD',
                           foreground='#000000',
                           font=('Arial', 10),
                           borderwidth=1,
                           relief='solid',
                           padx=5, pady=3)
            label.pack()

            # 自動隱藏
            tooltip.after(3000, tooltip.destroy)

            # 儲存參考以便手動隱藏
            widget.tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                try:
                    widget.tooltip.destroy()
                except:
                    pass

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
        widget.bind('<FocusIn>', show_tooltip)
        widget.bind('<FocusOut>', hide_tooltip)

    def make_widget_accessible(self, widget: tk.Widget,
                             label: str = "",
                             description: str = "",
                             role: str = ""):
        """
        使元件更具無障礙性

        Args:
            widget: 目標元件
            label: 元件標籤
            description: 元件描述
            role: 元件角色
        """
        # 添加標籤
        if label:
            self.add_aria_label(widget, label)

        # 添加描述
        if description:
            self.create_accessible_tooltip(widget, description)

        # 確保元件可以接收焦點
        if hasattr(widget, 'configure'):
            try:
                widget.configure(takefocus=True)
            except:
                pass

        # 添加鍵盤事件處理
        self.add_keyboard_support(widget)

    def add_keyboard_support(self, widget: tk.Widget):
        """
        為元件添加鍵盤支援

        Args:
            widget: 目標元件
        """
        if isinstance(widget, (tk.Button, ttk.Button)):
            # 按鈕支援 Space 和 Enter
            widget.bind('<space>', lambda e: widget.invoke())
            widget.bind('<Return>', lambda e: widget.invoke())

        elif isinstance(widget, (tk.Checkbutton, ttk.Checkbutton)):
            # 核取方塊支援 Space
            widget.bind('<space>', lambda e: widget.invoke())

        elif isinstance(widget, (tk.Radiobutton, ttk.Radiobutton)):
            # 單選按鈕支援 Space
            widget.bind('<space>', lambda e: widget.invoke())

        elif isinstance(widget, tk.Listbox):
            # 列表框支援方向鍵和 Enter
            def on_key(event):
                if event.keysym == 'Return':
                    widget.event_generate('<Double-Button-1>')
            widget.bind('<Key>', on_key)

        elif isinstance(widget, ttk.Treeview):
            # 樹狀檢視支援方向鍵和 Enter
            def on_key(event):
                if event.keysym == 'Return':
                    widget.event_generate('<Double-Button-1>')
            widget.bind('<Key>', on_key)

    def create_skip_link(self, parent: tk.Widget, target_widget: tk.Widget,
                        text: str = "跳到主要內容"):
        """
        建立跳過連結（無障礙導航）

        Args:
            parent: 父元件
            target_widget: 目標元件
            text: 連結文字
        """
        skip_button = tk.Button(parent, text=text,
                              command=lambda: target_widget.focus_set(),
                              font=('Arial', 8),
                              relief=tk.FLAT,
                              borderwidth=0)

        # 預設隱藏，獲得焦點時顯示
        skip_button.pack_forget()

        def show_skip_link(event):
            skip_button.pack(side=tk.TOP, anchor=tk.W)

        def hide_skip_link(event):
            skip_button.pack_forget()

        skip_button.bind('<FocusIn>', show_skip_link)
        skip_button.bind('<FocusOut>', hide_skip_link)

        return skip_button

    def announce_to_screen_reader(self, message: str):
        """
        向螢幕閱讀器宣告訊息

        Args:
            message: 要宣告的訊息
        """
        # 在 tkinter 中，我們可以使用隱藏的標籤來模擬
        # 實際應用中可能需要使用平台特定的 API
        if self.screen_reader_mode:
            print(f"螢幕閱讀器: {message}")  # 簡單的模擬


# 全域實例
_keyboard_nav_manager = None
_accessibility_helper = None

def get_keyboard_navigation_manager(root: tk.Widget = None) -> KeyboardNavigationManager:
    """取得鍵盤導航管理器實例"""
    global _keyboard_nav_manager
    if _keyboard_nav_manager is None and root:
        _keyboard_nav_manager = KeyboardNavigationManager(root)
    return _keyboard_nav_manager

def get_accessibility_helper() -> AccessibilityHelper:
    """取得無障礙輔助工具實例"""
    global _accessibility_helper
    if _accessibility_helper is None:
        _accessibility_helper = AccessibilityHelper()
    return _accessibility_helper