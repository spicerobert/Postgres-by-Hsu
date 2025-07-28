"""
資料匯出管理器

提供統一的資料匯出功能，支援 CSV 格式匯出和自訂欄位選擇。
"""

import csv
import os
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow, StationStatistics, ComparisonResult


class ExportFormat(Enum):
    """匯出格式枚舉"""
    CSV = "csv"


class ExportStatus(Enum):
    """匯出狀態枚舉"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExportField:
    """匯出欄位定義"""
    key: str
    display_name: str
    data_type: type
    formatter: Optional[Callable[[Any], str]] = None
    default_selected: bool = True


@dataclass
class ExportTask:
    """匯出任務"""
    task_id: str
    data_type: str
    data: List[Any]
    fields: List[ExportField]
    selected_fields: List[str]
    filename: str
    format: ExportFormat
    status: ExportStatus
    progress: float = 0.0
    error_message: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class FieldSelectionDialog:
    """欄位選擇對話框"""

    def __init__(self, parent: tk.Widget, fields: List[ExportField], title: str = "選擇匯出欄位"):
        """
        初始化欄位選擇對話框

        Args:
            parent: 父視窗
            fields: 可選欄位列表
            title: 對話框標題
        """
        self.parent = parent
        self.fields = fields
        self.selected_fields = []
        self.result = None

        # 建立對話框視窗
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 置中顯示
        self.center_dialog()

        # 建立介面
        self.setup_ui()

        # 等待使用者操作
        self.dialog.wait_window()

    def center_dialog(self):
        """將對話框置中顯示"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"400x500+{x}+{y}")

    def setup_ui(self):
        """設定使用者介面"""
        # 標題
        title_label = ttk.Label(
            self.dialog,
            text="請選擇要匯出的欄位:",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(pady=(10, 5))

        # 建立欄位選擇區域
        self.create_field_selection()

        # 建立按鈕區域
        self.create_buttons()

    def create_field_selection(self):
        """建立欄位選擇區域"""
        # 建立框架
        frame = ttk.Frame(self.dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 建立捲軸清單框
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 建立 Treeview 用於顯示欄位
        columns = ('selected', 'field_name', 'data_type')
        self.field_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        # 設定欄位標題
        self.field_tree.heading('selected', text='選擇')
        self.field_tree.heading('field_name', text='欄位名稱')
        self.field_tree.heading('data_type', text='資料類型')

        # 設定欄位寬度
        self.field_tree.column('selected', width=60, anchor=tk.CENTER)
        self.field_tree.column('field_name', width=200, anchor=tk.W)
        self.field_tree.column('data_type', width=100, anchor=tk.CENTER)

        # 建立捲軸
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.field_tree.yview)
        self.field_tree.configure(yscrollcommand=scrollbar.set)

        # 打包元件
        self.field_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 載入欄位資料
        self.load_fields()

        # 綁定點擊事件
        self.field_tree.bind('<Button-1>', self.on_field_click)

        # 建立操作按鈕
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="全選", command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="全不選", command=self.deselect_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="反選", command=self.invert_selection).pack(side=tk.LEFT)

    def load_fields(self):
        """載入欄位資料"""
        for field in self.fields:
            # 判斷是否預設選中
            selected = "✓" if field.default_selected else ""
            data_type_name = field.data_type.__name__ if field.data_type else "str"

            item_id = self.field_tree.insert('', tk.END, values=(
                selected,
                field.display_name,
                data_type_name
            ))

            # 儲存欄位資訊到項目
            self.field_tree.set(item_id, 'field_key', field.key)
            self.field_tree.set(item_id, 'selected_state', field.default_selected)

    def on_field_click(self, event):
        """處理欄位點擊事件"""
        region = self.field_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.field_tree.identify_column(event.x, event.y)
            if column == '#1':  # 選擇欄位
                item = self.field_tree.identify_row(event.y)
                if item:
                    self.toggle_field_selection(item)

    def toggle_field_selection(self, item):
        """切換欄位選擇狀態"""
        current_state = self.field_tree.set(item, 'selected_state')
        new_state = not bool(current_state)

        # 更新顯示
        selected_text = "✓" if new_state else ""
        self.field_tree.set(item, 'selected', selected_text)
        self.field_tree.set(item, 'selected_state', new_state)

    def select_all(self):
        """全選"""
        for item in self.field_tree.get_children():
            self.field_tree.set(item, 'selected', "✓")
            self.field_tree.set(item, 'selected_state', True)

    def deselect_all(self):
        """全不選"""
        for item in self.field_tree.get_children():
            self.field_tree.set(item, 'selected', "")
            self.field_tree.set(item, 'selected_state', False)

    def invert_selection(self):
        """反選"""
        for item in self.field_tree.get_children():
            current_state = self.field_tree.set(item, 'selected_state')
            new_state = not bool(current_state)
            selected_text = "✓" if new_state else ""
            self.field_tree.set(item, 'selected', selected_text)
            self.field_tree.set(item, 'selected_state', new_state)

    def create_buttons(self):
        """建立按鈕區域"""
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # 確定按鈕
        ttk.Button(
            button_frame,
            text="確定",
            command=self.on_ok,
            width=10
        ).pack(side=tk.RIGHT, padx=(5, 0))

        # 取消按鈕
        ttk.Button(
            button_frame,
            text="取消",
            command=self.on_cancel,
            width=10
        ).pack(side=tk.RIGHT)

    def on_ok(self):
        """確定按鈕處理"""
        # 收集選中的欄位
        selected_fields = []
        for item in self.field_tree.get_children():
            if self.field_tree.set(item, 'selected_state'):
                field_key = self.field_tree.set(item, 'field_key')
                selected_fields.append(field_key)

        if not selected_fields:
            messagebox.showwarning("警告", "請至少選擇一個欄位")
            return

        self.selected_fields = selected_fields
        self.result = True
        self.dialog.destroy()

    def on_cancel(self):
        """取消按鈕處理"""
        self.result = False
        self.dialog.destroy()

    def get_selected_fields(self) -> Optional[List[str]]:
        """取得選中的欄位"""
        return self.selected_fields if self.result else None


class ExportProgressDialog:
    """匯出進度對話框"""

    def __init__(self, parent: tk.Widget, task: ExportTask):
        """
        初始化進度對話框

        Args:
            parent: 父視窗
            task: 匯出任務
        """
        self.parent = parent
        self.task = task
        self.cancelled = False

        # 建立對話框視窗
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("匯出進度")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 置中顯示
        self.center_dialog()

        # 建立介面
        self.setup_ui()

        # 防止關閉視窗
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def center_dialog(self):
        """將對話框置中顯示"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (200 // 2)
        self.dialog.geometry(f"400x200+{x}+{y}")

    def setup_ui(self):
        """設定使用者介面"""
        # 標題
        title_label = ttk.Label(
            self.dialog,
            text=f"正在匯出: {os.path.basename(self.task.filename)}",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(pady=(20, 10))

        # 進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.dialog,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.pack(pady=10)

        # 狀態標籤
        self.status_var = tk.StringVar(value="準備中...")
        self.status_label = ttk.Label(
            self.dialog,
            textvariable=self.status_var
        )
        self.status_label.pack(pady=5)

        # 取消按鈕
        self.cancel_button = ttk.Button(
            self.dialog,
            text="取消",
            command=self.on_cancel,
            width=10
        )
        self.cancel_button.pack(pady=10)

    def update_progress(self, progress: float, status: str):
        """更新進度"""
        self.progress_var.set(progress)
        self.status_var.set(status)
        self.dialog.update()

    def on_cancel(self):
        """取消匯出"""
        if messagebox.askyesno("確認", "確定要取消匯出嗎？"):
            self.cancelled = True
            self.task.status = ExportStatus.CANCELLED
            self.dialog.destroy()

    def close(self):
        """關閉對話框"""
        self.dialog.destroy()

    def is_cancelled(self) -> bool:
        """檢查是否已取消"""
        return self.cancelled


class ExportManager:
    """
    資料匯出管理器

    提供統一的資料匯出功能，支援多種資料類型和格式。
    """

    def __init__(self):
        """初始化匯出管理器"""
        self.logger = logging.getLogger(__name__)
        self.tasks = {}  # 任務字典
        self.task_counter = 0

        # 預定義的欄位格式化器
        self.formatters = {
            'number': lambda x: f"{x:,}" if isinstance(x, (int, float)) else str(x),
            'float': lambda x: f"{x:.2f}" if isinstance(x, float) else str(x),
            'date': lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else str(x),
            'datetime': lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if hasattr(x, 'strftime') else str(x),
            'boolean': lambda x: "是" if x else "否",
            'default': lambda x: str(x) if x is not None else ""
        }

    def get_station_fields(self) -> List[ExportField]:
        """取得車站資料的匯出欄位定義"""
        return [
            ExportField('station_code', '車站代碼', str, self.formatters['default']),
            ExportField('station_name', '車站名稱', str, self.formatters['default']),
            ExportField('address', '地址', str, self.formatters['default']),
            ExportField('phone', '電話', str, self.formatters['default']),
            ExportField('gps_lat', '緯度', float, self.formatters['float']),
            ExportField('gps_lng', '經度', float, self.formatters['float']),
            ExportField('has_bike_rental', '自行車租借', bool, self.formatters['boolean']),
        ]

    def get_passenger_flow_fields(self) -> List[ExportField]:
        """取得客流量資料的匯出欄位定義"""
        return [
            ExportField('date', '日期', date, self.formatters['date']),
            ExportField('station_code', '車站代碼', str, self.formatters['default']),
            ExportField('in_passengers', '進站人數', int, self.formatters['number']),
            ExportField('out_passengers', '出站人數', int, self.formatters['number']),
            ExportField('total_passengers', '總人數', int, self.formatters['number']),
            ExportField('net_flow', '淨流量', int, self.formatters['number']),
        ]

    def get_station_statistics_fields(self) -> List[ExportField]:
        """取得車站統計資料的匯出欄位定義"""
        return [
            ExportField('station_code', '車站代碼', str, self.formatters['default']),
            ExportField('station_name', '車站名稱', str, self.formatters['default']),
            ExportField('total_in', '總進站人數', int, self.formatters['number']),
            ExportField('total_out', '總出站人數', int, self.formatters['number']),
            ExportField('total_passengers', '總客流量', int, self.formatters['number']),
            ExportField('average_daily', '平均每日客流量', float, self.formatters['float']),
            ExportField('date_range_str', '統計期間', str, self.formatters['default']),
            ExportField('net_flow', '淨流量', int, self.formatters['number']),
        ]

    def get_comparison_result_fields(self) -> List[ExportField]:
        """取得比較結果的匯出欄位定義"""
        return [
            ExportField('rank', '排名', int, self.formatters['default']),
            ExportField('station_name', '車站名稱', str, self.formatters['default']),
            ExportField('total_in', '總進站人數', int, self.formatters['number']),
            ExportField('total_out', '總出站人數', int, self.formatters['number']),
            ExportField('total_passengers', '總客流量', int, self.formatters['number']),
            ExportField('average_daily', '平均每日客流量', float, self.formatters['float']),
            ExportField('net_flow', '淨流量', int, self.formatters['number']),
        ]

    def export_stations(self, parent: tk.Widget, stations: List[Station],
                       default_filename: str = None) -> bool:
        """
        匯出車站資料

        Args:
            parent: 父視窗
            stations: 車站資料列表
            default_filename: 預設檔案名稱

        Returns:
            bool: 匯出是否成功
        """
        if not stations:
            messagebox.showwarning("警告", "沒有可匯出的車站資料")
            return False

        return self._export_data(
            parent=parent,
            data=stations,
            data_type="stations",
            fields=self.get_station_fields(),
            default_filename=default_filename or f"車站資料_{date.today().strftime('%Y%m%d')}.csv"
        )

    def export_passenger_flows(self, parent: tk.Widget, flows: List[PassengerFlow],
                              default_filename: str = None) -> bool:
        """
        匯出客流量資料

        Args:
            parent: 父視窗
            flows: 客流量資料列表
            default_filename: 預設檔案名稱

        Returns:
            bool: 匯出是否成功
        """
        if not flows:
            messagebox.showwarning("警告", "沒有可匯出的客流量資料")
            return False

        return self._export_data(
            parent=parent,
            data=flows,
            data_type="passenger_flows",
            fields=self.get_passenger_flow_fields(),
            default_filename=default_filename or f"客流量資料_{date.today().strftime('%Y%m%d')}.csv"
        )

    def export_station_statistics(self, parent: tk.Widget, statistics: List[StationStatistics],
                                 default_filename: str = None) -> bool:
        """
        匯出車站統計資料

        Args:
            parent: 父視窗
            statistics: 車站統計資料列表
            default_filename: 預設檔案名稱

        Returns:
            bool: 匯出是否成功
        """
        if not statistics:
            messagebox.showwarning("警告", "沒有可匯出的統計資料")
            return False

        return self._export_data(
            parent=parent,
            data=statistics,
            data_type="station_statistics",
            fields=self.get_station_statistics_fields(),
            default_filename=default_filename or f"車站統計_{date.today().strftime('%Y%m%d')}.csv"
        )

    def export_comparison_result(self, parent: tk.Widget, comparison_result: ComparisonResult,
                                default_filename: str = None) -> bool:
        """
        匯出比較結果

        Args:
            parent: 父視窗
            comparison_result: 比較結果
            default_filename: 預設檔案名稱

        Returns:
            bool: 匯出是否成功
        """
        if not comparison_result or not comparison_result.stations:
            messagebox.showwarning("警告", "沒有可匯出的比較資料")
            return False

        # 準備比較資料（包含排名）
        comparison_data = []
        for rank, (station_name, total_passengers) in enumerate(comparison_result.ranking, 1):
            # 找到對應的統計資料
            station_stats = None
            for stats in comparison_result.stations:
                if stats.station_name == station_name:
                    station_stats = stats
                    break

            if station_stats:
                # 建立包含排名的資料物件
                data_item = type('ComparisonItem', (), {
                    'rank': rank,
                    'station_name': station_name,
                    'total_in': station_stats.total_in,
                    'total_out': station_stats.total_out,
                    'total_passengers': station_stats.total_passengers,
                    'average_daily': station_stats.average_daily,
                    'net_flow': station_stats.net_flow
                })()
                comparison_data.append(data_item)

        return self._export_data(
            parent=parent,
            data=comparison_data,
            data_type="comparison_result",
            fields=self.get_comparison_result_fields(),
            default_filename=default_filename or f"車站比較_{date.today().strftime('%Y%m%d')}.csv"
        )

    def _export_data(self, parent: tk.Widget, data: List[Any], data_type: str,
                    fields: List[ExportField], default_filename: str) -> bool:
        """
        通用資料匯出方法

        Args:
            parent: 父視窗
            data: 要匯出的資料
            data_type: 資料類型
            fields: 欄位定義
            default_filename: 預設檔案名稱

        Returns:
            bool: 匯出是否成功
        """
        try:
            # 顯示欄位選擇對話框
            field_dialog = FieldSelectionDialog(parent, fields, "選擇匯出欄位")
            selected_fields = field_dialog.get_selected_fields()

            if not selected_fields:
                return False

            # 選擇儲存位置
            filename = filedialog.asksaveasfilename(
                title="匯出資料",
                defaultextension=".csv",
                initialvalue=default_filename,
                filetypes=[("CSV 檔案", "*.csv"), ("所有檔案", "*.*")]
            )

            if not filename:
                return False

            # 建立匯出任務
            task = self._create_export_task(
                data=data,
                data_type=data_type,
                fields=fields,
                selected_fields=selected_fields,
                filename=filename
            )

            # 執行匯出
            return self._execute_export_task(parent, task)

        except Exception as e:
            self.logger.error(f"匯出資料失敗: {e}")
            messagebox.showerror("匯出失敗", f"匯出資料時發生錯誤: {e}")
            return False

    def _create_export_task(self, data: List[Any], data_type: str, fields: List[ExportField],
                           selected_fields: List[str], filename: str) -> ExportTask:
        """建立匯出任務"""
        self.task_counter += 1
        task_id = f"export_{self.task_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        task = ExportTask(
            task_id=task_id,
            data_type=data_type,
            data=data,
            fields=fields,
            selected_fields=selected_fields,
            filename=filename,
            format=ExportFormat.CSV,
            status=ExportStatus.PENDING
        )

        self.tasks[task_id] = task
        return task

    def _execute_export_task(self, parent: tk.Widget, task: ExportTask) -> bool:
        """執行匯出任務"""
        # 顯示進度對話框
        progress_dialog = ExportProgressDialog(parent, task)

        # 在背景執行緒中執行匯出
        def export_thread():
            try:
                task.status = ExportStatus.IN_PROGRESS
                self._perform_csv_export(task, progress_dialog)

                if not progress_dialog.is_cancelled():
                    task.status = ExportStatus.COMPLETED
                    task.completed_at = datetime.now()

            except Exception as e:
                self.logger.error(f"匯出任務失敗: {e}")
                task.status = ExportStatus.FAILED
                task.error_message = str(e)

            # 在主執行緒中關閉進度對話框
            try:
                parent.after(0, progress_dialog.close)
            except Exception:
                # 如果無法在主執行緒中執行，直接關閉
                try:
                    progress_dialog.close()
                except Exception:
                    pass

        # 啟動匯出執行緒
        export_thread_obj = threading.Thread(target=export_thread, daemon=True)
        export_thread_obj.start()

        # 等待執行緒完成
        export_thread_obj.join()

        # 顯示結果
        if task.status == ExportStatus.COMPLETED:
            messagebox.showinfo(
                "匯出成功",
                f"已成功匯出 {len(task.data)} 筆記錄到:\n{task.filename}"
            )
            return True
        elif task.status == ExportStatus.CANCELLED:
            return False
        else:
            messagebox.showerror(
                "匯出失敗",
                f"匯出失敗: {task.error_message or '未知錯誤'}"
            )
            return False

    def _perform_csv_export(self, task: ExportTask, progress_dialog: ExportProgressDialog):
        """執行 CSV 匯出"""
        # 建立欄位映射
        field_map = {field.key: field for field in task.fields}
        selected_field_objects = [field_map[key] for key in task.selected_fields if key in field_map]

        # 準備標題行
        headers = [field.display_name for field in selected_field_objects]

        # 開始寫入檔案
        with open(task.filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # 寫入標題
            writer.writerow(headers)
            progress_dialog.update_progress(5, "寫入標題...")

            # 寫入資料
            total_rows = len(task.data)
            for i, item in enumerate(task.data):
                if progress_dialog.is_cancelled():
                    break

                # 準備資料行
                row = []
                for field in selected_field_objects:
                    try:
                        # 取得屬性值
                        value = getattr(item, field.key, None)

                        # 套用格式化器
                        if field.formatter and value is not None:
                            formatted_value = field.formatter(value)
                        else:
                            formatted_value = str(value) if value is not None else ""

                        row.append(formatted_value)

                    except Exception as e:
                        self.logger.warning(f"格式化欄位 {field.key} 失敗: {e}")
                        row.append("")

                writer.writerow(row)

                # 更新進度
                progress = 5 + (i + 1) / total_rows * 90
                status = f"正在寫入第 {i + 1}/{total_rows} 筆記錄..."
                progress_dialog.update_progress(progress, status)

        if not progress_dialog.is_cancelled():
            progress_dialog.update_progress(100, "匯出完成")

    def get_task_status(self, task_id: str) -> Optional[ExportTask]:
        """取得任務狀態"""
        return self.tasks.get(task_id)

    def clear_completed_tasks(self):
        """清除已完成的任務"""
        completed_tasks = [
            task_id for task_id, task in self.tasks.items()
            if task.status in [ExportStatus.COMPLETED, ExportStatus.FAILED, ExportStatus.CANCELLED]
        ]

        for task_id in completed_tasks:
            del self.tasks[task_id]

        self.logger.info(f"已清除 {len(completed_tasks)} 個已完成的任務")


# 全域匯出管理器實例
_export_manager = None


def get_export_manager() -> ExportManager:
    """取得匯出管理器實例（單例模式）"""
    global _export_manager
    if _export_manager is None:
        _export_manager = ExportManager()
    return _export_manager