"""
跨平台一致性配置

確保應用程式在不同作業系統上保持一致的外觀和行為。
"""

import platform
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Tuple
from taiwan_railway_gui.gui.styles import get_style_manager


class PlatformManager:
    """平台管理器"""

    def __init__(self):
        """初始化平台管理器"""
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_macos = self.system == "Darwin"
        self.is_linux = self.system == "Linux"

        self.style_manager = get_style_manager()

        # 平台特定配置
        self.platform_configs = {
            'Windows': self._get_windows_config(),
            'Darwin': self._get_macos_config(),
            'Linux': self._get_linux_config()
        }

    def _get_windows_config(self) -> Dict[str, Any]:
        """取得Windows平台配置"""
        return {
            'window_style': {
                'use_native_theme': True,
                'title_bar_color': None,  # 使用系統預設
                'border_style': 'normal'
            },
            'fonts': {
                'scaling_factor': 1.0,
                'clear_type': True,
                'use_system_fonts': True
            },
            'spacing': {
                'button_padding': (10, 5),
                'frame_padding': 8,
                'widget_spacing': 5
            },
            'scrollbars': {
                'width': 17,
                'style': 'windows'
            },
            'dialogs': {
                'use_native': True,
                'modal_style': 'windows'
            },
            'shortcuts': {
                'copy': '<Control-c>',
                'paste': '<Control-v>',
                'cut': '<Control-x>',
                'select_all': '<Control-a>',
                'quit': '<Alt-F4>'
            }
        }

    def _get_macos_config(self) -> Dict[str, Any]:
        """取得macOS平台配置"""
        return {
            'window_style': {
                'use_native_theme': True,
                'title_bar_color': 'system',
                'border_style': 'aqua'
            },
            'fonts': {
                'scaling_factor': 1.0,
                'anti_aliasing': True,
                'use_system_fonts': True
            },
            'spacing': {
                'button_padding': (12, 6),
                'frame_padding': 10,
                'widget_spacing': 8
            },
            'scrollbars': {
                'width': 15,
                'style': 'aqua'
            },
            'dialogs': {
                'use_native': True,
                'modal_style': 'sheet'
            },
            'shortcuts': {
                'copy': '<Command-c>',
                'paste': '<Command-v>',
                'cut': '<Command-x>',
                'select_all': '<Command-a>',
                'quit': '<Command-q>'
            }
        }

    def _get_linux_config(self) -> Dict[str, Any]:
        """取得Linux平台配置"""
        return {
            'window_style': {
                'use_native_theme': False,
                'title_bar_color': None,
                'border_style': 'custom'
            },
            'fonts': {
                'scaling_factor': 1.0,
                'anti_aliasing': True,
                'use_system_fonts': False
            },
            'spacing': {
                'button_padding': (10, 5),
                'frame_padding': 8,
                'widget_spacing': 6
            },
            'scrollbars': {
                'width': 16,
                'style': 'gtk'
            },
            'dialogs': {
                'use_native': False,
                'modal_style': 'tkinter'
            },
            'shortcuts': {
                'copy': '<Control-c>',
                'paste': '<Control-v>',
                'cut': '<Control-x>',
                'select_all': '<Control-a>',
                'quit': '<Control-q>'
            }
        }

    def get_current_config(self) -> Dict[str, Any]:
        """取得當前平台配置"""
        return self.platform_configs.get(self.system, self.platform_configs['Linux'])

    def apply_platform_styles(self, root: tk.Tk, style: ttk.Style):
        """套用平台特定樣式"""
        config = self.get_current_config()

        # 套用視窗樣式
        self._apply_window_style(root, config['window_style'])

        # 套用TTK樣式
        self._apply_ttk_styles(style, config)

        # 設定字體縮放
        self._apply_font_scaling(config['fonts'])

    def _apply_window_style(self, root: tk.Tk, window_config: Dict[str, Any]):
        """套用視窗樣式"""
        if self.is_macos:
            # macOS特有設定
            try:
                root.tk.call('::tk::unsupported::MacWindowStyle', 'style', root._w, 'document')
            except Exception:
                pass

        elif self.is_windows:
            # Windows特有設定
            try:
                root.wm_attributes('-transparentcolor', '')
            except Exception:
                pass

        # 設定視窗圖示
        self._set_window_icon(root)

    def _apply_ttk_styles(self, style: ttk.Style, config: Dict[str, Any]):
        """套用TTK樣式"""
        # 選擇合適的主題
        available_themes = style.theme_names()

        if self.is_windows and 'vista' in available_themes:
            style.theme_use('vista')
        elif self.is_macos and 'aqua' in available_themes:
            style.theme_use('aqua')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        else:
            style.theme_use('default')

        # 應用自訂樣式
        self.style_manager.configure_ttk_styles(style)

        # 平台特定調整
        self._apply_platform_specific_adjustments(style, config)

    def _apply_platform_specific_adjustments(self, style: ttk.Style, config: Dict[str, Any]):
        """套用平台特定調整"""
        spacing_config = config['spacing']

        # 調整按鈕內距
        style.configure('TButton', padding=spacing_config['button_padding'])
        style.configure('Primary.TButton', padding=spacing_config['button_padding'])
        style.configure('Secondary.TButton', padding=spacing_config['button_padding'])

        # 調整捲軸寬度
        scrollbar_config = config['scrollbars']
        if 'width' in scrollbar_config:
            style.configure('TScrollbar', width=scrollbar_config['width'])

    def _apply_font_scaling(self, font_config: Dict[str, Any]):
        """套用字體縮放"""
        scaling_factor = font_config.get('scaling_factor', 1.0)

        if scaling_factor != 1.0:
            # 調整所有字體大小
            theme = self.style_manager.get_theme()
            fonts = theme['fonts']

            for font_name, (family, size, weight) in fonts.items():
                new_size = int(size * scaling_factor)
                fonts[font_name] = (family, new_size, weight)

    def _set_window_icon(self, root: tk.Tk):
        """設定視窗圖示"""
        try:
            if self.is_windows:
                # Windows .ico 格式
                root.iconbitmap(default='assets/icon.ico')
            else:
                # 其他平台使用 PNG
                icon = tk.PhotoImage(file='assets/icon.png')
                root.iconphoto(True, icon)
        except Exception:
            # 如果圖示檔案不存在，忽略錯誤
            pass

    def get_platform_shortcuts(self) -> Dict[str, str]:
        """取得平台特定快捷鍵"""
        config = self.get_current_config()
        return config['shortcuts']

    def create_platform_menu(self, root: tk.Tk) -> tk.Menu:
        """建立平台特定選單"""
        menubar = tk.Menu(root)

        if self.is_macos:
            # macOS 應用程式選單
            app_menu = tk.Menu(menubar, name='apple')
            menubar.add_cascade(menu=app_menu)

            app_menu.add_command(label='關於台鐵車站資訊查詢系統')
            app_menu.add_separator()
            app_menu.add_command(label='服務')
            app_menu.add_separator()
            app_menu.add_command(label='隱藏台鐵車站資訊查詢系統', accelerator='Cmd+H')
            app_menu.add_command(label='隱藏其他', accelerator='Cmd+Opt+H')
            app_menu.add_command(label='全部顯示')
            app_menu.add_separator()
            app_menu.add_command(label='結束台鐵車站資訊查詢系統', accelerator='Cmd+Q')

        return menubar

    def configure_high_dpi(self, root: tk.Tk):
        """配置高DPI支援"""
        if self.is_windows:
            try:
                # Windows高DPI感知
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass

        # 取得DPI縮放比例
        try:
            dpi = root.winfo_fpixels('1i')
            scale_factor = dpi / 96.0  # 96 DPI為標準

            if scale_factor > 1.1:  # 如果DPI縮放大於110%
                # 調整字體大小
                self._apply_font_scaling({'scaling_factor': scale_factor})
        except Exception:
            pass

    def get_file_dialog_options(self) -> Dict[str, Any]:
        """取得檔案對話框選項"""
        config = self.get_current_config()

        base_options = {
            'filetypes': [
                ('CSV files', '*.csv'),
                ('All files', '*.*')
            ]
        }

        if config['dialogs']['use_native']:
            # 使用原生對話框
            if self.is_macos:
                base_options.update({
                    'message': '選擇檔案',
                    'defaultextension': '.csv'
                })
            elif self.is_windows:
                base_options.update({
                    'title': '選擇檔案',
                    'defaultextension': '.csv'
                })

        return base_options

    def create_context_menu(self, widget: tk.Widget) -> tk.Menu:
        """建立上下文選單"""
        menu = tk.Menu(widget, tearoff=0)
        shortcuts = self.get_platform_shortcuts()

        if hasattr(widget, 'selection_get'):
            # 文字輸入元件
            menu.add_command(label=f"複製\t{shortcuts['copy']}")
            menu.add_command(label=f"貼上\t{shortcuts['paste']}")
            menu.add_command(label=f"剪下\t{shortcuts['cut']}")
            menu.add_separator()
            menu.add_command(label=f"全選\t{shortcuts['select_all']}")

        return menu

    def apply_accessibility_enhancements(self, root: tk.Tk):
        """套用無障礙增強功能"""
        if self.is_windows:
            # Windows無障礙API整合
            try:
                # 設定視窗可存取性屬性
                root.wm_attributes('-toolwindow', False)
            except Exception:
                pass

        elif self.is_macos:
            # macOS VoiceOver支援
            try:
                # 啟用輔助功能
                root.tk.call('::tk::unsupported::MacWindowStyle', 'style', root._w, 'document')
            except Exception:
                pass


# 全域實例
_platform_manager = None


def get_platform_manager() -> PlatformManager:
    """取得全域平台管理器實例"""
    global _platform_manager
    if _platform_manager is None:
        _platform_manager = PlatformManager()
    return _platform_manager


def apply_platform_consistency(root: tk.Tk, style: ttk.Style):
    """套用跨平台一致性"""
    platform_manager = get_platform_manager()

    # 套用平台樣式
    platform_manager.apply_platform_styles(root, style)

    # 配置高DPI支援
    platform_manager.configure_high_dpi(root)

    # 套用無障礙增強
    platform_manager.apply_accessibility_enhancements(root)


def get_platform_appropriate_font() -> Tuple[str, int, str]:
    """取得平台適當的字體"""
    platform_manager = get_platform_manager()

    if platform_manager.is_windows:
        return ('Microsoft JhengHei UI', 10, 'normal')
    elif platform_manager.is_macos:
        return ('PingFang TC', 10, 'normal')
    else:  # Linux
        return ('Noto Sans CJK TC', 10, 'normal')


def create_platform_appropriate_dialog(parent: tk.Widget, title: str, message: str,
                                      dialog_type: str = 'info') -> None:
    """建立平台適當的對話框"""
    platform_manager = get_platform_manager()
    config = platform_manager.get_current_config()

    if config['dialogs']['use_native']:
        # 使用原生對話框
        from tkinter import messagebox

        if dialog_type == 'info':
            messagebox.showinfo(title, message, parent=parent)
        elif dialog_type == 'warning':
            messagebox.showwarning(title, message, parent=parent)
        elif dialog_type == 'error':
            messagebox.showerror(title, message, parent=parent)
    else:
        # 使用自訂對話框
        _create_custom_dialog(parent, title, message, dialog_type)


def _create_custom_dialog(parent: tk.Widget, title: str, message: str, dialog_type: str):
    """建立自訂對話框"""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.grab_set()

    # 居中顯示
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_reqwidth() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_reqheight() // 2)
    dialog.geometry(f"+{x}+{y}")

    # 建立內容
    frame = ttk.Frame(dialog, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)

    # 圖示和訊息
    icon_map = {
        'info': 'ℹ',
        'warning': '⚠',
        'error': '✗'
    }

    icon_label = tk.Label(frame, text=icon_map.get(dialog_type, 'ℹ'),
                         font=('Arial', 24))
    icon_label.pack(pady=(0, 10))

    message_label = tk.Label(frame, text=message, wraplength=300,
                           justify=tk.CENTER)
    message_label.pack(pady=(0, 20))

    # 確定按鈕
    ok_button = ttk.Button(frame, text='確定', command=dialog.destroy)
    ok_button.pack()
    ok_button.focus_set()

    # 鍵盤事件
    dialog.bind('<Return>', lambda e: dialog.destroy())
    dialog.bind('<Escape>', lambda e: dialog.destroy())
