"""
圖表視覺化分頁

實作客流量資料的圖表視覺化功能。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
import matplotlib
matplotlib.use('TkAgg')  # 設定 matplotlib 後端
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from taiwan_railway_gui.gui.base_tab import BaseTab
from taiwan_railway_gui.gui.passenger_flow_tab import DatePicker
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow
from taiwan_railway_gui.dao.station_dao import create_station_dao
from taiwan_railway_gui.dao.passenger_flow_dao import create_passenger_flow_dao
from taiwan_railway_gui.utils.gui_helpers import create_tooltip, format_number
from taiwan_railway_gui.config import get_config


class ChartCanvas:
    """圖表畫布元件"""

    def __init__(self, parent: tk.Widget):
        """
        初始化圖表畫布

        Args:
            parent: 父元件
        """
        self.parent = parent

        # 建立 matplotlib 圖形
        self.figure = Figure(figsize=(12, 6), dpi=100)
        self.figure.patch.set_facecolor('white')

        # 建立畫布
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 建立工具列
        self.toolbar = NavigationToolbar2Tk(self.canvas, parent)
        self.toolbar.update()

        # 初始化軸
        self.ax = None
        self.current_data = None
        self.current_chart_type = 'line'

        # 設定中文字體
        self.setup_chinese_font()

    def setup_chinese_font(self):
        """設定中文字體"""
        try:
            # 嘗試設定中文字體
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
        except Exception:
            # 如果設定失敗，使用預設字體
            pass

    def clear_chart(self):
        """清除圖表"""
        self.figure.clear()
        self.ax = None
        self.canvas.draw()

    def create_line_chart(self, flows: List[PassengerFlow], station_name: str, title: str = None):
        """
        建立線圖

        Args:
            flows: 客流量資料列表
            station_name: 車站名稱
            title: 圖表標題
        """
        self.clear_chart()

        if not flows:
            self._show_no_data_message()
            return

        # 建立子圖
        self.ax = self.figure.add_subplot(111)

        # 準備資料
        dates = [flow.date for flow in flows]
        in_passengers = [flow.in_passengers for flow in flows]
        out_passengers = [flow.out_passengers for flow in flows]

        # 繪製線圖
        self.ax.plot(dates, in_passengers, label='進站人數', marker='o', linewidth=2, markersize=4)
        self.ax.plot(dates, out_passengers, label='出站人數', marker='s', linewidth=2, markersize=4)

        # 設定標題和標籤
        chart_title = title or f'{station_name} 客流量趨勢圖'
        self.ax.set_title(chart_title, fontsize=14, fontweight='bold', pad=20)
        self.ax.set_xlabel('日期', fontsize=12)
        self.ax.set_ylabel('人數', fontsize=12)

        # 設定圖例
        self.ax.legend(loc='upper right')

        # 設定日期格式
        self._format_date_axis()

        # 設定網格
        self.ax.grid(True, alpha=0.3)

        # 自動調整佈局
        self.figure.tight_layout()

        # 更新畫布
        self.canvas.draw()

        # 儲存當前資料
        self.current_data = {'flows': flows, 'station_name': station_name, 'title': title}
        self.current_chart_type = 'line'

    def create_bar_chart(self, flows: List[PassengerFlow], station_name: str, title: str = None):
        """
        建立長條圖

        Args:
            flows: 客流量資料列表
            station_name: 車站名稱
            title: 圖表標題
        """
        self.clear_chart()

        if not flows:
            self._show_no_data_message()
            return

        # 建立子圖
        self.ax = self.figure.add_subplot(111)

        # 準備資料
        dates = [flow.date for flow in flows]
        in_passengers = [flow.in_passengers for flow in flows]
        out_passengers = [flow.out_passengers for flow in flows]

        # 設定長條寬度
        bar_width = 0.35
        x_pos = range(len(dates))

        # 繪製長條圖
        bars1 = self.ax.bar([x - bar_width/2 for x in x_pos], in_passengers,
                           bar_width, label='進站人數', alpha=0.8)
        bars2 = self.ax.bar([x + bar_width/2 for x in x_pos], out_passengers,
                           bar_width, label='出站人數', alpha=0.8)

        # 設定標題和標籤
        chart_title = title or f'{station_name} 客流量長條圖'
        self.ax.set_title(chart_title, fontsize=14, fontweight='bold', pad=20)
        self.ax.set_xlabel('日期', fontsize=12)
        self.ax.set_ylabel('人數', fontsize=12)

        # 設定 x 軸標籤
        self.ax.set_xticks(x_pos)
        if len(dates) <= 31:  # 如果資料點不多，顯示所有日期
            self.ax.set_xticklabels([d.strftime('%m/%d') for d in dates], rotation=45)
        else:  # 如果資料點太多，只顯示部分日期
            step = max(1, len(dates) // 10)
            labels = [d.strftime('%m/%d') if i % step == 0 else '' for i, d in enumerate(dates)]
            self.ax.set_xticklabels(labels, rotation=45)

        # 設定圖例
        self.ax.legend(loc='upper right')

        # 設定網格
        self.ax.grid(True, alpha=0.3, axis='y')

        # 自動調整佈局
        self.figure.tight_layout()

        # 更新畫布
        self.canvas.draw()

        # 儲存當前資料
        self.current_data = {'flows': flows, 'station_name': station_name, 'title': title}
        self.current_chart_type = 'bar'

    def _format_date_axis(self):
        """格式化日期軸"""
        if self.ax is None or self.current_data is None:
            return

        # 設定日期格式器
        if len(self.current_data['flows']) <= 31:
            # 少於31天，顯示月/日
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(self.current_data['flows']) // 10)))
        else:
            # 超過31天，顯示月份
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
            self.ax.xaxis.set_major_locator(mdates.MonthLocator())

        # 旋轉日期標籤
        self.figure.autofmt_xdate()

    def _show_no_data_message(self):
        """顯示無資料訊息"""
        self.ax = self.figure.add_subplot(111)
        self.ax.text(0.5, 0.5, '沒有資料可顯示',
                    horizontalalignment='center', verticalalignment='center',
                    transform=self.ax.transAxes, fontsize=16, color='gray')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()

    def refresh_chart(self):
        """重新整理圖表"""
        if self.current_data:
            if self.current_chart_type == 'line':
                self.create_line_chart(**self.current_data)
            elif self.current_chart_type == 'bar':
                self.create_bar_chart(**self.current_data)

    def save_chart(self, filename: str, **kwargs):
        """
        儲存圖表

        Args:
            filename: 檔案名稱
            **kwargs: 儲存參數
        """
        import os

        # 預設參數
        default_params = {
            'dpi': 300,
            'bbox_inches': 'tight',
            'facecolor': 'white',
            'edgecolor': 'none',
            'pad_inches': 0.1
        }

        # 合併參數
        save_params = {**default_params, **kwargs}

        # 確保目錄存在
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # 儲存圖表
        try:
            self.figure.savefig(filename, **save_params)

            # 強制清理記憶體
            import gc
            gc.collect()

        except Exception as e:
            # 記錄詳細錯誤資訊
            import logging
            logging.error(f"儲存圖表失敗 - 檔案: {filename}, 參數: {save_params}, 錯誤: {e}")
            raise


class ChartTab(BaseTab):
    """
    圖表視覺化分頁實作

    提供客流量資料的圖表視覺化功能。
    """

    def __init__(self, parent: tk.Widget, main_window=None):
        """
        初始化圖表視覺化分頁

        Args:
            parent: 父元件
            main_window: 主視窗參考
        """
        # 初始化 DAO
        self.station_dao = create_station_dao()
        self.passenger_flow_dao = create_passenger_flow_dao()

        # 圖表相關變數
        self.stations_list = []
        self.current_flows = []
        self.chart_canvas = None

        # 呼叫父類別初始化
        super().__init__(parent, main_window)

    def setup_ui(self):
        """設定使用者介面"""
        # 建立主要區域
        self.create_control_section()
        self.create_chart_section()

        # 載入車站清單
        self.load_stations()

    def create_control_section(self):
        """建立控制區域"""
        control_frame = self.create_section_frame(self.frame, "圖表設定")
        control_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立輸入區域
        input_frame = self.create_input_frame(control_frame)

        # 第一行：車站選擇和圖表類型
        row1_frame = ttk.Frame(input_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 10))

        # 車站選擇
        self.station_label, self.station_combobox = self.create_labeled_combobox(
            row1_frame, "選擇車站:", [], width=25
        )
        self.station_label.pack(side=tk.LEFT, padx=(0, 10))
        self.station_combobox.pack(side=tk.LEFT, padx=(0, 20))

        # 圖表類型選擇
        chart_type_label = ttk.Label(row1_frame, text="圖表類型:", font=self.fonts['body'])
        chart_type_label.pack(side=tk.LEFT, padx=(0, 10))

        self.chart_type_var = tk.StringVar(value="line")
        self.chart_type_combobox = ttk.Combobox(
            row1_frame,
            textvariable=self.chart_type_var,
            values=["line", "bar"],
            state="readonly",
            width=10
        )
        self.chart_type_combobox.pack(side=tk.LEFT)

        # 設定圖表類型顯示文字
        self.chart_type_combobox.set("line")

        # 第二行：日期範圍選擇
        row2_frame = ttk.Frame(input_frame)
        row2_frame.pack(fill=tk.X, pady=(0, 10))

        # 開始日期
        self.start_date_picker = DatePicker(
            row2_frame,
            "開始日期:",
            date.today() - timedelta(days=30)
        )
        self.start_date_picker.pack(side=tk.LEFT, padx=(0, 20))

        # 結束日期
        self.end_date_picker = DatePicker(
            row2_frame,
            "結束日期:",
            date.today()
        )
        self.end_date_picker.pack(side=tk.LEFT)

        # 建立按鈕區域
        button_frame = self.create_button_frame(control_frame)

        # 生成圖表按鈕
        self.generate_button = ttk.Button(
            button_frame,
            text="生成圖表",
            command=self.generate_chart,
            width=self.layout['button_width']
        )
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))

        # 重新整理按鈕
        self.refresh_button = ttk.Button(
            button_frame,
            text="重新整理",
            command=self.refresh_chart,
            width=self.layout['button_width']
        )
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 10))

        # 清除圖表按鈕
        self.clear_button = ttk.Button(
            button_frame,
            text="清除圖表",
            command=self.clear_chart,
            width=self.layout['button_width']
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))

        # 儲存圖表按鈕
        self.save_button = ttk.Button(
            button_frame,
            text="儲存圖表",
            command=self.save_chart,
            width=self.layout['button_width'],
            state=tk.DISABLED
        )
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))

        # 匯出選項按鈕
        self.export_options_button = ttk.Button(
            button_frame,
            text="匯出選項",
            command=self.show_export_options,
            width=self.layout['button_width'],
            state=tk.DISABLED
        )
        self.export_options_button.pack(side=tk.LEFT)

        # 加入工具提示
        create_tooltip(self.station_combobox, "選擇要繪製圖表的車站")
        create_tooltip(self.chart_type_combobox, "選擇圖表類型：線圖或長條圖")
        create_tooltip(self.generate_button, "根據設定生成圖表")
        create_tooltip(self.refresh_button, "重新整理當前圖表")
        create_tooltip(self.clear_button, "清除圖表內容")
        create_tooltip(self.save_button, "將圖表儲存為圖片檔案")
        create_tooltip(self.export_options_button, "開啟進階匯出選項")

    def create_chart_section(self):
        """建立圖表區域"""
        chart_frame = self.create_section_frame(self.frame, "圖表顯示")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=self.layout['padding'], pady=self.layout['padding'])

        # 建立圖表畫布
        canvas_frame = ttk.Frame(chart_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=self.layout['padding'], pady=self.layout['padding'])

        self.chart_canvas = ChartCanvas(canvas_frame)

        # 建立圖表資訊標籤
        info_frame = ttk.Frame(chart_frame)
        info_frame.pack(fill=tk.X, padx=self.layout['padding'], pady=(0, self.layout['padding']))

        self.chart_info_var = tk.StringVar(value="請選擇車站和日期範圍，然後點選「生成圖表」")
        self.chart_info_label = ttk.Label(
            info_frame,
            textvariable=self.chart_info_var,
            font=self.fonts['body']
        )
        self.chart_info_label.pack(anchor=tk.W)

    def load_stations(self):
        """載入車站清單"""
        def load_task():
            try:
                return self.station_dao.get_all_stations()
            except Exception as e:
                self.logger.error(f"載入車站清單失敗: {e}")
                raise

        def load_callback(stations):
            self.stations_list = stations

            # 更新下拉選單
            station_names = [f"{station.station_name} ({station.station_code})"
                           for station in stations]
            self.station_combobox['values'] = station_names

            if stations:
                self.station_combobox.set(station_names[0])  # 預設選擇第一個

            self.show_info_message("載入完成", f"已載入 {len(stations)} 個車站")

        self.run_async_task(load_task, load_callback, "載入車站清單")

    def get_selected_station_code(self) -> Optional[str]:
        """取得選中的車站代碼"""
        selection = self.station_combobox.get()
        if not selection:
            return None

        # 從 "車站名稱 (代碼)" 格式中提取代碼
        try:
            start = selection.rfind('(') + 1
            end = selection.rfind(')')
            if start > 0 and end > start:
                return selection[start:end]
        except:
            pass

        return None

    def generate_chart(self):
        """生成圖表"""
        # 驗證輸入
        station_code = self.get_selected_station_code()
        if not station_code:
            self.show_warning_message("輸入錯誤", "請選擇一個車站")
            return

        start_date = self.start_date_picker.get_date()
        end_date = self.end_date_picker.get_date()

        # 驗證日期範圍
        is_valid, error_msg = self.validate_input(
            (start_date, end_date), 'validate_date_range'
        )
        if not is_valid:
            self.show_error_message("日期錯誤", error_msg)
            return

        def query_task():
            try:
                # 查詢客流量資料
                flows = self.passenger_flow_dao.get_passenger_flow(
                    station_code, start_date, end_date
                )

                # 取得車站名稱
                station = self.station_dao.get_station_by_code(station_code)
                station_name = station.station_name if station else f"車站 {station_code}"

                return flows, station_name
            except Exception as e:
                self.logger.error(f"查詢客流量資料失敗: {e}")
                raise

        def query_callback(result):
            flows, station_name = result
            self.current_flows = flows

            if flows:
                # 生成圖表
                chart_type = self.chart_type_var.get()

                if chart_type == "line":
                    self.chart_canvas.create_line_chart(flows, station_name)
                elif chart_type == "bar":
                    self.chart_canvas.create_bar_chart(flows, station_name)

                # 更新資訊
                days_count = len(flows)
                total_passengers = sum(flow.total_passengers for flow in flows)
                info_text = f"已生成 {station_name} 的{chart_type}圖表，共 {days_count} 天資料，總客流量 {format_number(total_passengers)} 人次"
                self.chart_info_var.set(info_text)

                # 啟用儲存和匯出按鈕
                self.save_button.config(state=tk.NORMAL)
                self.export_options_button.config(state=tk.NORMAL)

                self.show_info_message("圖表生成", f"已生成 {station_name} 的圖表")
            else:
                self.chart_canvas.clear_chart()
                self.chart_info_var.set("查詢期間內沒有資料")
                self.save_button.config(state=tk.DISABLED)
                self.export_options_button.config(state=tk.DISABLED)
                self.show_info_message("查詢結果", "查詢期間內沒有資料")

        # 執行非同步查詢
        station_name = self.station_combobox.get().split(' (')[0]
        loading_msg = f"查詢 {station_name} 客流量資料"
        self.run_async_task(query_task, query_callback, loading_msg)

    def refresh_chart(self):
        """重新整理圖表"""
        if self.chart_canvas and self.chart_canvas.current_data:
            self.chart_canvas.refresh_chart()
            self.show_info_message("重新整理", "圖表已重新整理")
        else:
            self.show_warning_message("重新整理", "沒有圖表可以重新整理")

    def clear_chart(self):
        """清除圖表"""
        if self.chart_canvas:
            self.chart_canvas.clear_chart()
            self.current_flows = []
            self.chart_info_var.set("圖表已清除")
            self.save_button.config(state=tk.DISABLED)
            self.export_options_button.config(state=tk.DISABLED)
            self.show_info_message("清除", "圖表已清除")

    def save_chart(self):
        """儲存圖表 - 快速儲存功能"""
        if not self.chart_canvas or not self.chart_canvas.current_data:
            self.show_warning_message("儲存", "沒有圖表可以儲存")
            return

        try:
            from tkinter import filedialog
            import os

            # 取得預設檔案名稱
            station_name = self.chart_canvas.current_data['station_name']
            chart_type = self.chart_canvas.current_chart_type
            default_filename = f"{station_name}_{chart_type}圖_{date.today().strftime('%Y%m%d')}"

            # 選擇儲存位置
            filename = filedialog.asksaveasfilename(
                title="儲存圖表",
                defaultextension=".png",
                initialvalue=default_filename,
                filetypes=[
                    ("PNG 檔案", "*.png"),
                    ("JPG 檔案", "*.jpg;*.jpeg"),
                    ("SVG 檔案", "*.svg"),
                    ("PDF 檔案", "*.pdf"),
                    ("所有檔案", "*.*")
                ]
            )

            if filename:
                # 顯示匯出進度
                self.show_info_message("匯出中", "正在儲存圖表...")
                self.update_ui()  # 強制更新 UI

                # 取得檔案副檔名
                _, ext = os.path.splitext(filename.lower())

                # 根據檔案格式設定參數
                save_params = self._get_save_parameters(ext)

                # 儲存圖表
                self.chart_canvas.save_chart(filename, **save_params)

                # 驗證檔案是否成功建立
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    # 取得檔案格式資訊
                    format_info = self._get_format_info(ext)
                    self.show_info_message("匯出成功",
                                         f"圖表已成功儲存為 {format_info} 格式:\n{filename}\n"
                                         f"檔案大小: {file_size:,} bytes")
                else:
                    self.show_error_message("匯出失敗", "檔案儲存失敗，請檢查檔案路徑和權限")

        except Exception as e:
            self.logger.error(f"儲存圖表失敗: {e}")
            error_msg = self._get_export_error_message(e)
            self.show_error_message("匯出失敗", error_msg)

    def _get_save_parameters(self, file_extension: str) -> Dict[str, Any]:
        """
        根據檔案副檔名取得儲存參數

        Args:
            file_extension: 檔案副檔名

        Returns:
            儲存參數字典
        """
        params = {
            'dpi': 300,
            'bbox_inches': 'tight',
            'facecolor': 'white',
            'edgecolor': 'none',
            'pad_inches': 0.1
        }

        if file_extension in ['.jpg', '.jpeg']:
            params.update({
                'format': 'jpeg',
                'facecolor': 'white',  # JPEG 不支援透明背景
                'quality': 95  # 高品質設定
            })
        elif file_extension == '.png':
            params.update({
                'format': 'png',
                'transparent': False
            })
        elif file_extension == '.svg':
            params.update({
                'format': 'svg',
                'dpi': 72,  # SVG 不需要高 DPI
                'transparent': True
            })
        elif file_extension == '.pdf':
            params.update({
                'format': 'pdf',
                'orientation': 'landscape'
            })

        return params

    def _get_format_info(self, file_extension: str) -> str:
        """
        根據檔案副檔名取得格式資訊

        Args:
            file_extension: 檔案副檔名

        Returns:
            格式資訊字串
        """
        format_map = {
            '.png': 'PNG (可攜式網路圖形)',
            '.jpg': 'JPEG (聯合圖像專家組)',
            '.jpeg': 'JPEG (聯合圖像專家組)',
            '.svg': 'SVG (可縮放向量圖形)',
            '.pdf': 'PDF (可攜式文件格式)'
        }
        return format_map.get(file_extension, '未知格式')

    def _get_export_error_message(self, error: Exception) -> str:
        """
        根據錯誤類型產生使用者友善的錯誤訊息

        Args:
            error: 錯誤物件

        Returns:
            使用者友善的錯誤訊息
        """
        error_str = str(error).lower()

        if 'permission' in error_str or 'access' in error_str:
            return ("檔案存取權限不足\n\n建議解決方案:\n"
                   "• 選擇其他儲存位置\n"
                   "• 檢查資料夾權限\n"
                   "• 關閉可能正在使用該檔案的程式")
        elif 'disk' in error_str or 'space' in error_str:
            return ("磁碟空間不足\n\n建議解決方案:\n"
                   "• 清理磁碟空間\n"
                   "• 選擇其他儲存位置")
        elif 'format' in error_str or 'codec' in error_str:
            return ("不支援的檔案格式\n\n建議解決方案:\n"
                   "• 使用 PNG 或 JPG 格式\n"
                   "• 檢查檔案副檔名是否正確")
        else:
            return f"無法儲存圖表: {error}\n\n建議解決方案:\n• 重新嘗試儲存\n• 選擇不同的檔案名稱或位置"

    def show_export_options(self):
        """顯示匯出選項對話框"""
        if not self.chart_canvas or not self.chart_canvas.current_data:
            self.show_warning_message("匯出選項", "沒有圖表可以匯出")
            return

        # 建立匯出選項對話框
        dialog = ExportOptionsDialog(self.frame, self.chart_canvas.current_data)
        result = dialog.show()

        if result:
            self._export_with_options(result)

    def _export_with_options(self, options: Dict[str, Any]):
        """
        使用指定選項匯出圖表

        Args:
            options: 匯出選項
        """
        try:
            from tkinter import filedialog
            import os
            import time

            # 取得預設檔案名稱
            station_name = self.chart_canvas.current_data['station_name']
            chart_type = self.chart_canvas.current_chart_type
            format_ext = options['format'].lower()
            timestamp = date.today().strftime('%Y%m%d')
            default_filename = f"{station_name}_{chart_type}圖_{timestamp}.{format_ext}"

            # 選擇儲存位置
            filetypes = self._get_filetypes_for_format(options['format'])
            filename = filedialog.asksaveasfilename(
                title="匯出圖表",
                defaultextension=f".{format_ext}",
                initialvalue=default_filename,
                filetypes=filetypes
            )

            if filename:
                # 顯示匯出進度
                progress_msg = f"正在匯出 {options['format']} 格式圖表..."
                self.show_info_message("匯出中", progress_msg)
                self.update_ui()  # 強制更新 UI

                # 記錄開始時間
                start_time = time.time()

                # 準備儲存參數
                save_params = {
                    'dpi': options['dpi'],
                    'bbox_inches': 'tight',
                    'facecolor': options['background_color'],
                    'edgecolor': 'none',
                    'pad_inches': 0.1
                }

                # 根據格式調整參數
                if format_ext in ['jpg', 'jpeg']:
                    save_params.update({
                        'format': 'jpeg',
                        'facecolor': 'white' if options['background_color'] == 'none' else options['background_color']
                    })
                elif format_ext == 'png':
                    save_params.update({
                        'format': 'png',
                        'transparent': options.get('transparent', False)
                    })
                elif format_ext == 'svg':
                    save_params.update({
                        'format': 'svg',
                        'transparent': True
                    })
                elif format_ext == 'pdf':
                    save_params.update({
                        'format': 'pdf',
                        'orientation': 'landscape'
                    })

                # 儲存圖表
                self.chart_canvas.save_chart(filename, **save_params)

                # 計算匯出時間
                export_time = time.time() - start_time

                # 驗證檔案
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    format_info = self._get_format_info(f".{format_ext}")

                    success_msg = (
                        f"圖表已成功匯出為 {format_info} 格式:\n"
                        f"檔案位置: {filename}\n"
                        f"解析度: {options['dpi']} DPI\n"
                        f"檔案大小: {file_size:,} bytes\n"
                        f"匯出時間: {export_time:.2f} 秒"
                    )

                    # 如果是透明背景，加入說明
                    if format_ext == 'png' and options.get('transparent', False):
                        success_msg += "\n背景: 透明"

                    self.show_info_message("匯出成功", success_msg)
                else:
                    self.show_error_message("匯出失敗", "檔案儲存失敗，請檢查檔案路徑和權限")

        except Exception as e:
            self.logger.error(f"匯出圖表失敗: {e}")
            error_msg = self._get_export_error_message(e)
            self.show_error_message("匯出失敗", error_msg)

    def _get_filetypes_for_format(self, format_name: str) -> List[tuple]:
        """
        根據格式取得檔案類型清單

        Args:
            format_name: 格式名稱

        Returns:
            檔案類型清單
        """
        format_map = {
            'PNG': [("PNG 檔案", "*.png")],
            'JPG': [("JPG 檔案", "*.jpg;*.jpeg")],
            'SVG': [("SVG 檔案", "*.svg")],
            'PDF': [("PDF 檔案", "*.pdf")]
        }

        return format_map.get(format_name, [("所有檔案", "*.*")])

    def export_data(self):
        """匯出圖表（與儲存圖表相同）"""
        self.save_chart()

    def refresh_data(self):
        """重新整理資料"""
        # 重新載入車站清單
        self.load_stations()

        # 如果有當前圖表，重新生成
        if self.current_flows:
            self.generate_chart()

    def update_ui(self):
        """強制更新使用者介面"""
        try:
            self.frame.update_idletasks()
            self.frame.update()
        except tk.TclError:
            # 如果視窗已關閉，忽略錯誤
            pass


class ExportOptionsDialog:
    """匯出選項對話框"""

    def __init__(self, parent: tk.Widget, chart_data: Dict[str, Any]):
        """
        初始化匯出選項對話框

        Args:
            parent: 父元件
            chart_data: 圖表資料
        """
        self.parent = parent
        self.chart_data = chart_data
        self.result = None
        self.dialog = None

    def show(self) -> Optional[Dict[str, Any]]:
        """
        顯示對話框

        Returns:
            使用者選擇的選項，如果取消則返回 None
        """
        # 建立對話框視窗
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("圖表匯出選項")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 置中顯示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"400x500+{x}+{y}")

        self._create_widgets()

        # 等待使用者操作
        self.dialog.wait_window()

        return self.result

    def _create_widgets(self):
        """建立對話框元件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 標題
        title_label = ttk.Label(main_frame, text="圖表匯出設定", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))

        # 圖表資訊
        info_text = f"圖表: {self.chart_data['station_name']}"
        if 'title' in self.chart_data and self.chart_data['title']:
            info_text = self.chart_data['title']

        info_label = ttk.Label(main_frame, text=info_text, font=('Arial', 10), foreground='gray')
        info_label.pack(pady=(0, 15))

        # 格式選擇
        format_frame = ttk.LabelFrame(main_frame, text="檔案格式", padding="10")
        format_frame.pack(fill=tk.X, pady=(0, 15))

        self.format_var = tk.StringVar(value="PNG")
        formats = [
            ("PNG", "PNG - 支援透明背景，適合網頁使用"),
            ("JPG", "JPG - 檔案較小，適合列印"),
            ("SVG", "SVG - 向量格式，可無限縮放"),
            ("PDF", "PDF - 適合文件嵌入")
        ]

        for i, (fmt, desc) in enumerate(formats):
            frame = ttk.Frame(format_frame)
            frame.pack(fill=tk.X, pady=2)

            ttk.Radiobutton(frame, text=fmt, variable=self.format_var,
                           value=fmt, command=self._on_format_change).pack(side=tk.LEFT)
            ttk.Label(frame, text=desc, font=('Arial', 9), foreground='gray').pack(side=tk.LEFT, padx=(10, 0))

        # 解析度設定
        dpi_frame = ttk.LabelFrame(main_frame, text="解析度 (DPI)", padding="10")
        dpi_frame.pack(fill=tk.X, pady=(0, 15))

        dpi_info_frame = ttk.Frame(dpi_frame)
        dpi_info_frame.pack(fill=tk.X)

        self.dpi_var = tk.StringVar(value="300")
        dpi_options = [
            ("72", "螢幕顯示"),
            ("150", "一般列印"),
            ("300", "高品質列印"),
            ("600", "專業列印")
        ]

        for dpi, desc in dpi_options:
            frame = ttk.Frame(dpi_info_frame)
            frame.pack(side=tk.LEFT, padx=(0, 20))

            ttk.Radiobutton(frame, text=f"{dpi} ({desc})", variable=self.dpi_var,
                           value=dpi).pack()

        # 背景顏色
        bg_frame = ttk.LabelFrame(main_frame, text="背景顏色", padding="10")
        bg_frame.pack(fill=tk.X, pady=(0, 15))

        self.bg_var = tk.StringVar(value="white")
        bg_options = [("白色", "white"), ("透明", "none"), ("淺灰", "#f5f5f5")]

        bg_radio_frame = ttk.Frame(bg_frame)
        bg_radio_frame.pack(fill=tk.X)

        for text, value in bg_options:
            ttk.Radiobutton(bg_radio_frame, text=text, variable=self.bg_var,
                           value=value, command=self._on_background_change).pack(side=tk.LEFT, padx=(0, 20))

        # JPG 品質設定
        self.quality_frame = ttk.LabelFrame(main_frame, text="JPG 品質", padding="10")
        self.quality_frame.pack(fill=tk.X, pady=(0, 15))

        quality_control_frame = ttk.Frame(self.quality_frame)
        quality_control_frame.pack(fill=tk.X)

        self.quality_var = tk.StringVar(value="95")
        self.quality_scale = ttk.Scale(quality_control_frame, from_=1, to=100,
                                      variable=self.quality_var, orient=tk.HORIZONTAL)
        self.quality_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.quality_label = ttk.Label(quality_control_frame, textvariable=self.quality_var, width=5)
        self.quality_label.pack(side=tk.RIGHT)

        quality_desc = ttk.Label(self.quality_frame, text="較高的品質會產生較大的檔案",
                                font=('Arial', 9), foreground='gray')
        quality_desc.pack(pady=(5, 0))

        # PNG 透明度
        self.transparent_frame = ttk.Frame(main_frame)
        self.transparent_frame.pack(fill=tk.X, pady=(0, 20))

        self.transparent_var = tk.BooleanVar(value=False)
        self.transparent_check = ttk.Checkbutton(self.transparent_frame, text="PNG 透明背景",
                                                variable=self.transparent_var)
        self.transparent_check.pack(side=tk.LEFT)

        transparent_desc = ttk.Label(self.transparent_frame, text="僅適用於 PNG 格式",
                                    font=('Arial', 9), foreground='gray')
        transparent_desc.pack(side=tk.LEFT, padx=(10, 0))

        # 按鈕區域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="匯出", command=self._export).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="取消", command=self._cancel).pack(side=tk.RIGHT)

        # 初始化控制項狀態
        self._on_format_change()

    def _on_format_change(self):
        """格式變更時的處理"""
        format_type = self.format_var.get()

        # 根據格式顯示/隱藏相關控制項
        if format_type == "JPG":
            self.quality_frame.pack(fill=tk.X, pady=(0, 15), before=self.transparent_frame)
            self.transparent_frame.pack_forget()
            # JPG 不支援透明背景
            if self.bg_var.get() == "none":
                self.bg_var.set("white")
        elif format_type == "PNG":
            self.quality_frame.pack_forget()
            self.transparent_frame.pack(fill=tk.X, pady=(0, 20))
        else:  # SVG, PDF
            self.quality_frame.pack_forget()
            self.transparent_frame.pack_forget()

    def _on_background_change(self):
        """背景顏色變更時的處理"""
        bg_color = self.bg_var.get()
        format_type = self.format_var.get()

        # JPG 不支援透明背景
        if format_type == "JPG" and bg_color == "none":
            self.bg_var.set("white")

        # 如果選擇透明背景，自動啟用 PNG 透明選項
        if bg_color == "none" and format_type == "PNG":
            self.transparent_var.set(True)

    def _export(self):
        """執行匯出"""
        try:
            self.result = {
                'format': self.format_var.get(),
                'dpi': int(self.dpi_var.get()),
                'background_color': self.bg_var.get(),
                'quality': int(float(self.quality_var.get())),
                'transparent': self.transparent_var.get()
            }
            self.dialog.destroy()
        except ValueError as e:
            tk.messagebox.showerror("輸入錯誤", f"請檢查輸入值: {e}")

    def _cancel(self):
        """取消匯出"""
        self.result = None
        self.dialog.destroy()


def create_chart_tab(parent: tk.Widget, main_window=None) -> ChartTab:
    """建立圖表視覺化分頁實例"""
    return ChartTab(parent, main_window)