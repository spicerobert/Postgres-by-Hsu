#!/usr/bin/env python3
"""
測試使用者介面美化和一致性

測試第13項任務的實作：統一色彩配置、字體設計、版面配置、視覺回饋和無障礙功能。
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
import logging

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from taiwan_railway_gui.gui.styles import get_style_manager
from taiwan_railway_gui.gui.accessibility import get_accessibility_helper, get_keyboard_navigation_manager
from taiwan_railway_gui.gui.visual_feedback import (
    get_visual_feedback_manager, IndicatorType, StatusIndicator,
    LoadingSpinner, ProgressBar, NotificationBanner
)
from taiwan_railway_gui.gui.platform_consistency import apply_platform_consistency


class UITestWindow:
    """UI測試視窗"""

    def __init__(self):
        """初始化測試視窗"""
        self.root = tk.Tk()
        self.root.title("使用者介面美化和一致性測試")
        self.root.geometry("800x600")

        # 設定樣式
        self.style = ttk.Style()
        self.setup_styles()

        # 建立測試介面
        self.create_test_interface()

    def setup_styles(self):
        """設定樣式"""
        # 初始化樣式管理器
        self.style_manager = get_style_manager()
        self.style_manager.configure_ttk_styles(self.style)

        # 套用跨平台一致性
        apply_platform_consistency(self.root, self.style)

        # 初始化無障礙功能
        self.keyboard_nav = get_keyboard_navigation_manager(self.root)
        self.accessibility = get_accessibility_helper()

        # 初始化視覺回饋系統
        self.visual_feedback = get_visual_feedback_manager(self.root)

        # 設定主題
        theme = self.style_manager.get_theme()
        colors = theme['colors']
        self.root.configure(bg=colors['background'])

    def create_test_interface(self):
        """建立測試介面"""
        # 建立主要容器
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 建立標題
        title_label = ttk.Label(main_frame, text="使用者介面美化和一致性測試", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # 建立分頁本
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 建立各種測試分頁
        self.create_colors_tab(notebook)
        self.create_fonts_tab(notebook)
        self.create_buttons_tab(notebook)
        self.create_feedback_tab(notebook)
        self.create_accessibility_tab(notebook)

        # 建立狀態列
        self.create_status_bar()

    def create_colors_tab(self, parent):
        """建立色彩測試分頁"""
        frame = ttk.Frame(parent, padding=10)
        parent.add(frame, text="色彩配置")

        ttk.Label(frame, text="色彩配置測試", style='Subtitle.TLabel').pack(pady=(0, 10))

        theme = self.style_manager.get_theme()
        colors = theme['colors']

        # 建立色彩樣本
        colors_frame = ttk.Frame(frame)
        colors_frame.pack(fill=tk.X, pady=10)

        row = 0
        col = 0
        for color_name, color_value in colors.items():
            color_frame = tk.Frame(colors_frame, bg=color_value, width=100, height=60, relief='solid', borderwidth=1)
            color_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            color_frame.grid_propagate(False)

            label = tk.Label(color_frame, text=color_name, bg=color_value,
                           fg='white' if color_name in ['primary', 'error'] else 'black',
                           font=('Arial', 8))
            label.place(relx=0.5, rely=0.5, anchor='center')

            col += 1
            if col > 3:
                col = 0
                row += 1

        # 設定網格權重
        for i in range(4):
            colors_frame.columnconfigure(i, weight=1)

    def create_fonts_tab(self, parent):
        """建立字體測試分頁"""
        frame = ttk.Frame(parent, padding=10)
        parent.add(frame, text="字體設計")

        ttk.Label(frame, text="字體設計測試", style='Subtitle.TLabel').pack(pady=(0, 10))

        theme = self.style_manager.get_theme()
        fonts = theme['fonts']

        # 顯示各種字體樣式
        for font_name, font_config in fonts.items():
            font_frame = ttk.LabelFrame(frame, text=f"{font_name} 字體", padding=10)
            font_frame.pack(fill=tk.X, pady=5)

            sample_text = f"這是 {font_name} 字體的樣本文字 (ABCDabcd1234)"
            label = tk.Label(font_frame, text=sample_text, font=font_config)
            label.pack(anchor='w')

            info_text = f"字體: {font_config[0]}, 大小: {font_config[1]}, 樣式: {font_config[2]}"
            info_label = tk.Label(font_frame, text=info_text,
                                font=('Arial', 8), fg='gray')
            info_label.pack(anchor='w')

    def create_buttons_tab(self, parent):
        """建立按鈕測試分頁"""
        frame = ttk.Frame(parent, padding=10)
        parent.add(frame, text="按鈕樣式")

        ttk.Label(frame, text="按鈕樣式測試", style='Subtitle.TLabel').pack(pady=(0, 10))

        # 建立不同樣式的按鈕
        button_styles = [
            ('Primary.TButton', '主要按鈕'),
            ('Secondary.TButton', '次要按鈕'),
            ('Success.TButton', '成功按鈕'),
            ('Warning.TButton', '警告按鈕'),
            ('Error.TButton', '錯誤按鈕')
        ]

        for style, text in button_styles:
            button_frame = ttk.Frame(frame)
            button_frame.pack(fill=tk.X, pady=5)

            button = ttk.Button(button_frame, text=text, style=style,
                              command=lambda t=text: self.button_clicked(t))
            button.pack(side=tk.LEFT, padx=10)

            # 添加懸停效果
            self.style_manager.create_hover_effect(button)

            # 添加動畫效果
            self.style_manager.create_button_animation(button)

            # 描述標籤
            desc_label = ttk.Label(button_frame, text=f"樣式: {style}")
            desc_label.pack(side=tk.LEFT, padx=20)

    def create_feedback_tab(self, parent):
        """建立視覺回饋測試分頁"""
        frame = ttk.Frame(parent, padding=10)
        parent.add(frame, text="視覺回饋")

        ttk.Label(frame, text="視覺回饋測試", style='Subtitle.TLabel').pack(pady=(0, 10))

        # 狀態指示器測試
        status_frame = ttk.LabelFrame(frame, text="狀態指示器", padding=10)
        status_frame.pack(fill=tk.X, pady=5)

        self.status_indicator = StatusIndicator(status_frame)
        self.status_indicator.pack(side=tk.LEFT, padx=10)

        status_buttons_frame = ttk.Frame(status_frame)
        status_buttons_frame.pack(side=tk.LEFT, padx=20)

        status_types = [
            (IndicatorType.READY, '就緒'),
            (IndicatorType.LOADING, '載入中'),
            (IndicatorType.SUCCESS, '成功'),
            (IndicatorType.WARNING, '警告'),
            (IndicatorType.ERROR, '錯誤')
        ]

        for status_type, text in status_types:
            btn = ttk.Button(status_buttons_frame, text=text,
                           command=lambda st=status_type, t=text: self.status_indicator.set_status(st, t))
            btn.pack(side=tk.LEFT, padx=2)

        # 載入轉圈指示器測試
        spinner_frame = ttk.LabelFrame(frame, text="載入指示器", padding=10)
        spinner_frame.pack(fill=tk.X, pady=5)

        self.loading_spinner = LoadingSpinner(spinner_frame)
        self.loading_spinner.pack(side=tk.LEFT, padx=10)

        ttk.Button(spinner_frame, text="開始",
                  command=self.loading_spinner.start).pack(side=tk.LEFT, padx=5)
        ttk.Button(spinner_frame, text="停止",
                  command=self.loading_spinner.stop).pack(side=tk.LEFT, padx=5)

        # 進度條測試
        progress_frame = ttk.LabelFrame(frame, text="進度條", padding=10)
        progress_frame.pack(fill=tk.X, pady=5)

        self.progress_bar = ProgressBar(progress_frame)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        progress_buttons_frame = ttk.Frame(progress_frame)
        progress_buttons_frame.pack(pady=5)

        ttk.Button(progress_buttons_frame, text="設定 25%",
                  command=lambda: self.progress_bar.set_progress(25)).pack(side=tk.LEFT, padx=2)
        ttk.Button(progress_buttons_frame, text="設定 50%",
                  command=lambda: self.progress_bar.set_progress(50)).pack(side=tk.LEFT, padx=2)
        ttk.Button(progress_buttons_frame, text="設定 75%",
                  command=lambda: self.progress_bar.set_progress(75)).pack(side=tk.LEFT, padx=2)
        ttk.Button(progress_buttons_frame, text="設定 100%",
                  command=lambda: self.progress_bar.set_progress(100)).pack(side=tk.LEFT, padx=2)
        ttk.Button(progress_buttons_frame, text="不定進度",
                  command=lambda: self.progress_bar.set_indeterminate()).pack(side=tk.LEFT, padx=2)

        # 通知橫幅測試
        notification_frame = ttk.LabelFrame(frame, text="通知橫幅", padding=10)
        notification_frame.pack(fill=tk.X, pady=5)

        self.notification_banner = NotificationBanner(frame)

        notification_buttons = [
            (IndicatorType.INFO, "這是一個資訊通知"),
            (IndicatorType.SUCCESS, "操作成功完成"),
            (IndicatorType.WARNING, "請注意這個警告"),
            (IndicatorType.ERROR, "發生了一個錯誤")
        ]

        for notif_type, message in notification_buttons:
            btn = ttk.Button(notification_frame, text=notif_type.value.title(),
                           command=lambda nt=notif_type, m=message: self.notification_banner.show(m, nt))
            btn.pack(side=tk.LEFT, padx=5)

    def create_accessibility_tab(self, parent):
        """建立無障礙功能測試分頁"""
        frame = ttk.Frame(parent, padding=10)
        parent.add(frame, text="無障礙功能")

        ttk.Label(frame, text="無障礙功能測試", style='Subtitle.TLabel').pack(pady=(0, 10))

        # 快捷鍵說明
        shortcuts_frame = ttk.LabelFrame(frame, text="鍵盤快捷鍵", padding=10)
        shortcuts_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        shortcuts_text = self.keyboard_nav.get_shortcuts_help()

        text_widget = tk.Text(shortcuts_frame, wrap=tk.WORD, height=15)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, shortcuts_text)
        text_widget.configure(state=tk.DISABLED)

        # 滾動條
        scrollbar = ttk.Scrollbar(shortcuts_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 焦點測試按鈕
        focus_frame = ttk.LabelFrame(frame, text="焦點測試", padding=10)
        focus_frame.pack(fill=tk.X, pady=5)

        focus_widgets = []
        for i in range(5):
            btn = ttk.Button(focus_frame, text=f"按鈕 {i+1}",
                           command=lambda i=i: self.show_focus_feedback(i+1))
            btn.pack(side=tk.LEFT, padx=5)
            focus_widgets.append(btn)

            # 添加到焦點環
            self.keyboard_nav.add_to_focus_ring(btn, priority=i)

            # 添加工具提示
            self.accessibility.create_accessible_tooltip(btn, f"這是第 {i+1} 個測試按鈕")

    def create_status_bar(self):
        """建立狀態列"""
        self.status_frame = ttk.Frame(self.root, style='Section.TFrame')
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 狀態指示器
        self.main_status_indicator = StatusIndicator(self.status_frame)
        self.main_status_indicator.pack(side=tk.LEFT, padx=5)

        # 狀態訊息
        theme = self.style_manager.get_theme()
        colors = theme['colors']
        fonts = theme['fonts']

        self.status_var = tk.StringVar(value="測試介面已載入")
        self.status_label = tk.Label(self.status_frame,
                                   textvariable=self.status_var,
                                   foreground=colors['text'],
                                   background=colors['background'],
                                   font=fonts['small'])
        self.status_label.pack(side=tk.LEFT, padx=10)

        # 時間標籤
        self.time_var = tk.StringVar()
        self.time_label = tk.Label(self.status_frame,
                                 textvariable=self.time_var,
                                 foreground=colors['text_muted'],
                                 background=colors['background'],
                                 font=fonts['small'])
        self.time_label.pack(side=tk.RIGHT, padx=5)

        # 開始時間更新
        self.update_time()

        # 設定初始狀態
        self.main_status_indicator.set_status(IndicatorType.READY, "就緒")

    def update_time(self):
        """更新時間顯示"""
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)

    def button_clicked(self, button_text):
        """按鈕點擊處理"""
        self.status_var.set(f"點擊了 {button_text}")
        self.main_status_indicator.set_status(IndicatorType.SUCCESS, f"點擊了 {button_text}")

    def show_focus_feedback(self, button_number):
        """顯示焦點回饋"""
        self.status_var.set(f"焦點在按鈕 {button_number}")
        self.main_status_indicator.set_status(IndicatorType.INFO, f"焦點在按鈕 {button_number}")

    def run(self):
        """執行測試視窗"""
        self.root.mainloop()


def main():
    """主函數"""
    # 設定日誌
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    try:
        # 建立並執行測試視窗
        test_window = UITestWindow()
        test_window.run()
    except Exception as e:
        print(f"執行測試時發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
