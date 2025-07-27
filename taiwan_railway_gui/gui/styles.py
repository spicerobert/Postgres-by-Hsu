"""
GUI 樣式管理器

提供統一的樣式配置、主題管理和視覺回饋系統。
"""

import tkinter as tk
from tkinter import ttk
import platform
from typing import Dict, Any, Optional, Tuple
from taiwan_railway_gui.config import get_config


class StyleManager:
    """
    樣式管理器

    負責管理應用程式的視覺樣式、主題和一致性。
    """

    def __init__(self):
        """初始化樣式管理器"""
        self.colors = get_config('colors')
        self.fonts = get_config('fonts')
        self.layout = get_config('layout')

        # 平台特定設定
        self.platform = platform.system()
        self.is_windows = self.platform == "Windows"
        self.is_macos = self.platform == "Darwin"
        self.is_linux = self.platform == "Linux"

        # 樣式快取
        self._style_cache = {}

        # 主題配置
        self.themes = {
            'default': self._create_default_theme(),
            'dark': self._create_dark_theme(),
            'high_contrast': self._create_high_contrast_theme()
        }

        self.current_theme = 'default'

    def _create_default_theme(self) -> Dict[str, Any]:
        """建立預設主題"""
        return {
            'colors': {
                'primary': '#2E86AB',
                'primary_light': '#4A9BC7',
                'primary_dark': '#1E5F7A',
                'secondary': '#F5F5F5',
                'secondary_dark': '#E0E0E0',
                'accent': '#28A745',
                'accent_light': '#34CE57',
                'warning': '#FFC107',
                'warning_light': '#FFD54F',
                'error': '#DC3545',
                'error_light': '#E57373',
                'success': '#28A745',
                'success_light': '#4CAF50',
                'info': '#17A2B8',
                'info_light': '#26C6DA',
                'text': '#333333',
                'text_light': '#666666',
                'text_muted': '#999999',
                'background': '#FFFFFF',
                'background_alt': '#F8F9FA',
                'border': '#DEE2E6',
                'border_light': '#E9ECEF',
                'shadow': '#00000020',
                'focus': '#007BFF',
                'hover': '#E9ECEF',
                'active': '#DEE2E6',
                'disabled': '#6C757D',
                'disabled_bg': '#E9ECEF'
            },
            'fonts': self._get_platform_fonts(),
            'spacing': {
                'xs': 2,
                'sm': 5,
                'md': 10,
                'lg': 15,
                'xl': 20,
                'xxl': 30
            },
            'borders': {
                'thin': 1,
                'normal': 2,
                'thick': 3
            },
            'shadows': {
                'light': '1px 1px 3px rgba(0,0,0,0.1)',
                'normal': '2px 2px 5px rgba(0,0,0,0.15)',
                'heavy': '3px 3px 8px rgba(0,0,0,0.2)'
            }
        }

    def _create_dark_theme(self) -> Dict[str, Any]:
        """建立深色主題"""
        base_theme = self._create_default_theme()
        base_theme['colors'].update({
            'primary': '#4A9BC7',
            'secondary': '#2D3748',
            'background': '#1A202C',
            'background_alt': '#2D3748',
            'text': '#E2E8F0',
            'text_light': '#CBD5E0',
            'text_muted': '#A0AEC0',
            'border': '#4A5568',
            'border_light': '#2D3748',
            'hover': '#4A5568',
            'active': '#2D3748',
            'disabled_bg': '#2D3748'
        })
        return base_theme

    def _create_high_contrast_theme(self) -> Dict[str, Any]:
        """建立高對比主題（無障礙）"""
        base_theme = self._create_default_theme()
        base_theme['colors'].update({
            'primary': '#000080',
            'secondary': '#FFFFFF',
            'background': '#FFFFFF',
            'text': '#000000',
            'border': '#000000',
            'focus': '#FF0000',
            'hover': '#FFFF00',
            'active': '#00FF00'
        })
        return base_theme

    def _get_platform_fonts(self) -> Dict[str, Tuple[str, int, str]]:
        """取得平台特定字體"""
        if self.is_windows:
            return {
                'header': ('Microsoft JhengHei UI', 12, 'bold'),
                'subheader': ('Microsoft JhengHei UI', 11, 'bold'),
                'body': ('Microsoft JhengHei UI', 10, 'normal'),
                'small': ('Microsoft JhengHei UI', 9, 'normal'),
                'monospace': ('Consolas', 9, 'normal'),
                'button': ('Microsoft JhengHei UI', 10, 'normal')
            }
        elif self.is_macos:
            return {
                'header': ('PingFang TC', 12, 'bold'),
                'subheader': ('PingFang TC', 11, 'bold'),
                'body': ('PingFang TC', 10, 'normal'),
                'small': ('PingFang TC', 9, 'normal'),
                'monospace': ('Monaco', 9, 'normal'),
                'button': ('PingFang TC', 10, 'normal')
            }
        else:  # Linux
            return {
                'header': ('Noto Sans CJK TC', 12, 'bold'),
                'subheader': ('Noto Sans CJK TC', 11, 'bold'),
                'body': ('Noto Sans CJK TC', 10, 'normal'),
                'small': ('Noto Sans CJK TC', 9, 'normal'),
                'monospace': ('DejaVu Sans Mono', 9, 'normal'),
                'button': ('Noto Sans CJK TC', 10, 'normal')
            }

    def get_theme(self, theme_name: str = None) -> Dict[str, Any]:
        """取得主題配置"""
        theme_name = theme_name or self.current_theme
        return self.themes.get(theme_name, self.themes['default'])

    def set_theme(self, theme_name: str):
        """設定當前主題"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self._style_cache.clear()  # 清除樣式快取

    def get_color(self, color_name: str, theme_name: str = None) -> str:
        """取得顏色值"""
        theme = self.get_theme(theme_name)
        return theme['colors'].get(color_name, '#000000')

    def get_font(self, font_name: str, theme_name: str = None) -> Tuple[str, int, str]:
        """取得字體配置"""
        theme = self.get_theme(theme_name)
        return theme['fonts'].get(font_name, ('Arial', 10, 'normal'))

    def get_spacing(self, size: str, theme_name: str = None) -> int:
        """取得間距值"""
        theme = self.get_theme(theme_name)
        return theme['spacing'].get(size, 10)

    def configure_ttk_styles(self, style: ttk.Style):
        """配置 ttk 樣式"""
        theme = self.get_theme()
        colors = theme['colors']
        fonts = theme['fonts']
        spacing = theme['spacing']

        # 設定主題
        available_themes = style.theme_names()
        if self.is_windows and 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')

        # 配置基本樣式
        style.configure('.',
                       background=colors['background'],
                       foreground=colors['text'],
                       font=fonts['body'])

        # 標題樣式
        style.configure('Title.TLabel',
                       font=fonts['header'],
                       foreground=colors['primary'],
                       background=colors['background'])

        style.configure('Subtitle.TLabel',
                       font=fonts['subheader'],
                       foreground=colors['text'],
                       background=colors['background'])

        # 按鈕樣式
        style.configure('Primary.TButton',
                       font=fonts['button'],
                       foreground=colors['background'],
                       background=colors['primary'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(spacing['md'], spacing['sm']))

        style.map('Primary.TButton',
                 background=[('active', colors['primary_light']),
                           ('pressed', colors['primary_dark']),
                           ('disabled', colors['disabled'])])

        style.configure('Secondary.TButton',
                       font=fonts['button'],
                       foreground=colors['text'],
                       background=colors['secondary'],
                       borderwidth=1,
                       focuscolor='none',
                       padding=(spacing['md'], spacing['sm']))

        style.map('Secondary.TButton',
                 background=[('active', colors['hover']),
                           ('pressed', colors['active']),
                           ('disabled', colors['disabled_bg'])],
                 foreground=[('disabled', colors['disabled'])])

        # 成功按鈕樣式
        style.configure('Success.TButton',
                       font=fonts['button'],
                       foreground=colors['background'],
                       background=colors['success'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(spacing['md'], spacing['sm']))

        style.map('Success.TButton',
                 background=[('active', colors['success_light']),
                           ('pressed', colors['success']),
                           ('disabled', colors['disabled'])])

        # 警告按鈕樣式
        style.configure('Warning.TButton',
                       font=fonts['button'],
                       foreground=colors['text'],
                       background=colors['warning'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(spacing['md'], spacing['sm']))

        style.map('Warning.TButton',
                 background=[('active', colors['warning_light']),
                           ('pressed', colors['warning']),
                           ('disabled', colors['disabled'])])

        # 錯誤按鈕樣式
        style.configure('Error.TButton',
                       font=fonts['button'],
                       foreground=colors['background'],
                       background=colors['error'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(spacing['md'], spacing['sm']))

        style.map('Error.TButton',
                 background=[('active', colors['error_light']),
                           ('pressed', colors['error']),
                           ('disabled', colors['disabled'])])

        # 框架樣式
        style.configure('Card.TFrame',
                       background=colors['background'],
                       borderwidth=1,
                       relief='solid')

        style.configure('Section.TFrame',
                       background=colors['background_alt'],
                       borderwidth=1,
                       relief='groove')

        # 標籤框架樣式
        style.configure('Card.TLabelFrame',
                       background=colors['background'],
                       borderwidth=1,
                       relief='solid',
                       labelmargins=(spacing['md'], spacing['sm']))

        style.configure('Card.TLabelFrame.Label',
                       font=fonts['subheader'],
                       foreground=colors['primary'],
                       background=colors['background'])

        # 輸入框樣式
        style.configure('TEntry',
                       font=fonts['body'],
                       fieldbackground=colors['background'],
                       borderwidth=1,
                       insertcolor=colors['text'],
                       padding=(spacing['sm'], spacing['sm']))

        style.map('TEntry',
                 focuscolor=[('focus', colors['focus'])],
                 bordercolor=[('focus', colors['focus']),
                            ('!focus', colors['border'])])

        # 下拉選單樣式
        style.configure('TCombobox',
                       font=fonts['body'],
                       fieldbackground=colors['background'],
                       borderwidth=1,
                       padding=(spacing['sm'], spacing['sm']))

        style.map('TCombobox',
                 focuscolor=[('focus', colors['focus'])],
                 bordercolor=[('focus', colors['focus']),
                            ('!focus', colors['border'])])

        # 樹狀檢視樣式
        style.configure('Treeview',
                       font=fonts['body'],
                       background=colors['background'],
                       foreground=colors['text'],
                       fieldbackground=colors['background'],
                       borderwidth=1,
                       rowheight=25)

        style.configure('Treeview.Heading',
                       font=fonts['subheader'],
                       background=colors['secondary'],
                       foreground=colors['text'],
                       borderwidth=1,
                       relief='raised')

        style.map('Treeview',
                 background=[('selected', colors['primary']),
                           ('focus', colors['primary_light'])],
                 foreground=[('selected', colors['background'])])

        # 進度條樣式
        style.configure('TProgressbar',
                       background=colors['primary'],
                       troughcolor=colors['secondary'],
                       borderwidth=0,
                       lightcolor=colors['primary_light'],
                       darkcolor=colors['primary_dark'])

        # 分頁樣式
        style.configure('TNotebook',
                       background=colors['background'],
                       borderwidth=1,
                       tabmargins=(spacing['sm'], spacing['sm'], spacing['sm'], 0))

        style.configure('TNotebook.Tab',
                       font=fonts['body'],
                       background=colors['secondary'],
                       foreground=colors['text'],
                       padding=(spacing['md'], spacing['sm']),
                       borderwidth=1)

        style.map('TNotebook.Tab',
                 background=[('selected', colors['background']),
                           ('active', colors['hover'])],
                 foreground=[('selected', colors['primary'])])

        # 捲軸樣式
        style.configure('TScrollbar',
                       background=colors['secondary'],
                       troughcolor=colors['background_alt'],
                       borderwidth=0,
                       arrowcolor=colors['text'],
                       darkcolor=colors['border'],
                       lightcolor=colors['background'])

        # 分隔線樣式
        style.configure('TSeparator',
                       background=colors['border'])

        # 狀態指示器樣式
        style.configure('Status.TLabel',
                       font=fonts['small'],
                       foreground=colors['text_muted'],
                       background=colors['background'])

        style.configure('Success.TLabel',
                       font=fonts['body'],
                       foreground=colors['success'],
                       background=colors['background'])

        style.configure('Warning.TLabel',
                       font=fonts['body'],
                       foreground=colors['warning'],
                       background=colors['background'])

        style.configure('Error.TLabel',
                       font=fonts['body'],
                       foreground=colors['error'],
                       background=colors['background'])

    def create_styled_widget(self, widget_type: str, parent: tk.Widget,
                           style_name: str = None, **kwargs) -> tk.Widget:
        """建立樣式化的元件"""
        theme = self.get_theme()
        colors = theme['colors']
        fonts = theme['fonts']
        spacing = theme['spacing']

        # 根據元件類型設定預設樣式
        if widget_type == 'Label':
            defaults = {
                'font': fonts['body'],
                'foreground': colors['text'],
                'background': colors['background']
            }
        elif widget_type == 'Button':
            defaults = {
                'font': fonts['button'],
                'foreground': colors['background'],
                'background': colors['primary'],
                'activeforeground': colors['background'],
                'activebackground': colors['primary_light'],
                'borderwidth': 0,
                'cursor': 'hand2',
                'padx': spacing['md'],
                'pady': spacing['sm']
            }
        elif widget_type == 'Entry':
            defaults = {
                'font': fonts['body'],
                'foreground': colors['text'],
                'background': colors['background'],
                'insertbackground': colors['text'],
                'borderwidth': 1,
                'relief': 'solid'
            }
        elif widget_type == 'Text':
            defaults = {
                'font': fonts['body'],
                'foreground': colors['text'],
                'background': colors['background'],
                'insertbackground': colors['text'],
                'borderwidth': 1,
                'relief': 'solid',
                'wrap': tk.WORD
            }
        elif widget_type == 'Listbox':
            defaults = {
                'font': fonts['body'],
                'foreground': colors['text'],
                'background': colors['background'],
                'selectbackground': colors['primary'],
                'selectforeground': colors['background'],
                'borderwidth': 1,
                'relief': 'solid'
            }
        elif widget_type == 'Frame':
            defaults = {
                'background': colors['background'],
                'borderwidth': 0
            }
        else:
            defaults = {}

        # 合併預設值和使用者參數
        final_kwargs = {**defaults, **kwargs}

        # 建立元件
        widget_class = getattr(tk, widget_type)
        widget = widget_class(parent, **final_kwargs)

        # 套用特定樣式
        if style_name:
            self.apply_widget_style(widget, style_name)

        return widget

    def apply_widget_style(self, widget: tk.Widget, style_name: str):
        """套用特定樣式到元件"""
        theme = self.get_theme()
        colors = theme['colors']

        style_configs = {
            'primary': {
                'background': colors['primary'],
                'foreground': colors['background']
            },
            'secondary': {
                'background': colors['secondary'],
                'foreground': colors['text']
            },
            'success': {
                'background': colors['success'],
                'foreground': colors['background']
            },
            'warning': {
                'background': colors['warning'],
                'foreground': colors['text']
            },
            'error': {
                'background': colors['error'],
                'foreground': colors['background']
            },
            'card': {
                'background': colors['background'],
                'borderwidth': 1,
                'relief': 'solid'
            },
            'muted': {
                'foreground': colors['text_muted']
            }
        }

        config = style_configs.get(style_name, {})
        if config:
            widget.configure(**config)

    def create_hover_effect(self, widget: tk.Widget,
                          hover_color: str = None,
                          normal_color: str = None):
        """為元件添加懸停效果"""
        theme = self.get_theme()
        colors = theme['colors']

        # 如果沒有指定顏色，使用預設值
        if hover_color is None:
            hover_color = colors.get('hover', colors['secondary'])
        if normal_color is None:
            normal_color = colors.get('background', '#FFFFFF')

        original_bg = widget.cget('background') if hasattr(widget, 'cget') else normal_color

        def on_enter(event):
            try:
                widget.configure(background=hover_color)
                # 添加光標變化
                widget.configure(cursor='hand2')
            except tk.TclError:
                pass

        def on_leave(event):
            try:
                widget.configure(background=original_bg)
                widget.configure(cursor='')
            except tk.TclError:
                pass

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def create_button_animation(self, button: tk.Widget):
        """為按鈕添加點擊動畫效果"""
        theme = self.get_theme()
        colors = theme['colors']

        original_relief = button.cget('relief') if hasattr(button, 'cget') else 'raised'

        def on_button_press(event):
            try:
                button.configure(relief='sunken')
                # 短暫延遲後恢復
                button.after(100, lambda: button.configure(relief=original_relief))
            except tk.TclError:
                pass

        button.bind('<Button-1>', on_button_press)

    def apply_card_style(self, widget: tk.Widget, elevated: bool = False):
        """套用卡片樣式"""
        theme = self.get_theme()
        colors = theme['colors']
        spacing = theme['spacing']

        if elevated:
            # 高度較高的卡片樣式（有陰影效果）
            widget.configure(
                background=colors['background'],
                borderwidth=2,
                relief='raised',
                padx=spacing['md'],
                pady=spacing['md']
            )
        else:
            # 扁平卡片樣式
            widget.configure(
                background=colors['background'],
                borderwidth=1,
                relief='solid',
                padx=spacing['sm'],
                pady=spacing['sm']
            )

    def create_loading_indicator_style(self, widget: tk.Widget):
        """創建載入指示器樣式"""
        theme = self.get_theme()
        colors = theme['colors']

        widget.configure(
            foreground=colors['primary'],
            background=colors['background']
        )

    def apply_status_style(self, widget: tk.Widget, status: str):
        """套用狀態樣式"""
        theme = self.get_theme()
        colors = theme['colors']

        status_colors = {
            'success': colors['success'],
            'warning': colors['warning'],
            'error': colors['error'],
            'info': colors['info'],
            'default': colors['text']
        }

        color = status_colors.get(status, status_colors['default'])
        widget.configure(foreground=color)

    def create_focus_effect(self, widget: tk.Widget):
        """為元件添加焦點效果"""
        theme = self.get_theme()
        colors = theme['colors']

        original_relief = widget.cget('relief')
        original_borderwidth = widget.cget('borderwidth')

        def on_focus_in(event):
            widget.configure(relief='solid', borderwidth=2,
                           highlightbackground=colors['focus'])

        def on_focus_out(event):
            widget.configure(relief=original_relief,
                           borderwidth=original_borderwidth)

        widget.bind('<FocusIn>', on_focus_in)
        widget.bind('<FocusOut>', on_focus_out)

    def get_icon_font(self) -> Tuple[str, int]:
        """取得圖示字體（如果可用）"""
        # 這裡可以擴展支援圖示字體
        return ('Segoe UI Symbol', 12) if self.is_windows else ('Arial Unicode MS', 12)


# 全域樣式管理器實例
_style_manager = None

def get_style_manager() -> StyleManager:
    """取得全域樣式管理器實例"""
    global _style_manager
    if _style_manager is None:
        _style_manager = StyleManager()
    return _style_manager