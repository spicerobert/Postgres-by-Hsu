"""
非同步管理器

實作資料庫查詢的非同步處理，提供進度追蹤和取消功能。
"""

import logging
import threading
import time
from typing import Callable, Any, Optional, Dict, List
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, Empty
import tkinter as tk
from taiwan_railway_gui.interfaces import AsyncManagerInterface


class AsyncTask:
    """非同步任務類別"""

    def __init__(self, task_id: str, task_func: Callable, callback: Callable = None,
                 error_callback: Callable = None, progress_callback: Callable = None):
        """
        初始化非同步任務

        Args:
            task_id: 任務識別碼
            task_func: 要執行的任務函數
            callback: 成功回調函數
            error_callback: 錯誤回調函數
            progress_callback: 進度回調函數
        """
        self.task_id = task_id
        self.task_func = task_func
        self.callback = callback
        self.error_callback = error_callback
        self.progress_callback = progress_callback

        self.future: Optional[Future] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.cancelled = False
        self.progress = 0.0
        self.status = "pending"  # pending, running, completed, error, cancelled


class AsyncManager(AsyncManagerInterface):
    """
    非同步管理器實作

    提供資料庫查詢的非同步處理，避免 GUI 凍結。
    """

    def __init__(self, max_workers: int = 4):
        """
        初始化非同步管理器

        Args:
            max_workers: 最大工作執行緒數量
        """
        self.logger = logging.getLogger(__name__)
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # 任務管理
        self.active_tasks: Dict[str, AsyncTask] = {}
        self.task_counter = 0

        # 進度更新佇列
        self.progress_queue = Queue()

        # 主執行緒參考（用於 GUI 更新）
        self.main_thread_id = threading.get_ident()

        # 定期檢查進度更新
        self._start_progress_monitor()

    def _start_progress_monitor(self):
        """啟動進度監控"""
        def monitor():
            while True:
                try:
                    # 檢查進度更新
                    try:
                        update = self.progress_queue.get(timeout=0.1)
                        self._handle_progress_update(update)
                    except Empty:
                        pass

                    # 清理完成的任務
                    self._cleanup_completed_tasks()

                    time.sleep(0.1)
                except Exception as e:
                    self.logger.error(f"進度監控錯誤: {e}")

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def _handle_progress_update(self, update: Dict[str, Any]):
        """處理進度更新"""
        task_id = update.get('task_id')
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.progress = update.get('progress', 0.0)
            task.status = update.get('status', task.status)

            if task.progress_callback:
                try:
                    task.progress_callback(task.progress, update.get('message', ''))
                except Exception as e:
                    self.logger.error(f"進度回調錯誤: {e}")

    def _cleanup_completed_tasks(self):
        """清理完成的任務"""
        completed_tasks = []
        for task_id, task in self.active_tasks.items():
            if task.status in ['completed', 'error', 'cancelled']:
                if task.end_time and time.time() - task.end_time > 60:  # 1分鐘後清理
                    completed_tasks.append(task_id)

        for task_id in completed_tasks:
            del self.active_tasks[task_id]

    def submit_task(self, task_func: Callable, callback: Callable = None,
                   error_callback: Callable = None, progress_callback: Callable = None,
                   task_name: str = None) -> str:
        """
        提交非同步任務

        Args:
            task_func: 要執行的任務函數
            callback: 成功回調函數
            error_callback: 錯誤回調函數
            progress_callback: 進度回調函數
            task_name: 任務名稱

        Returns:
            任務識別碼
        """
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{int(time.time())}"

        if task_name:
            task_id = f"{task_name}_{self.task_counter}"

        # 建立任務
        task = AsyncTask(task_id, task_func, callback, error_callback, progress_callback)
        task.start_time = time.time()
        task.status = "running"

        # 包裝任務函數以處理進度和錯誤
        def wrapped_task():
            try:
                # 更新進度
                self.progress_queue.put({
                    'task_id': task_id,
                    'progress': 0.0,
                    'status': 'running',
                    'message': '開始執行任務'
                })

                # 執行任務
                result = task_func()

                # 任務完成
                task.end_time = time.time()
                task.status = "completed"

                self.progress_queue.put({
                    'task_id': task_id,
                    'progress': 100.0,
                    'status': 'completed',
                    'message': '任務完成'
                })

                # 在主執行緒中執行回調
                if callback:
                    self._schedule_callback(lambda: callback(result))

                return result

            except Exception as e:
                task.end_time = time.time()
                task.status = "error"

                self.progress_queue.put({
                    'task_id': task_id,
                    'progress': 0.0,
                    'status': 'error',
                    'message': f'任務失敗: {str(e)}'
                })

                self.logger.error(f"任務 {task_id} 執行失敗: {e}")

                # 在主執行緒中執行錯誤回調
                if error_callback:
                    self._schedule_callback(lambda: error_callback(e))
                else:
                    # 預設錯誤處理
                    self._schedule_callback(lambda: self._default_error_handler(e))

                raise

        # 提交任務到執行緒池
        task.future = self.executor.submit(wrapped_task)
        self.active_tasks[task_id] = task

        self.logger.info(f"已提交任務: {task_id}")
        return task_id

    def _schedule_callback(self, callback: Callable):
        """在主執行緒中排程回調"""
        # 這裡需要根據 GUI 框架來實作
        # 對於 tkinter，可以使用 after 方法
        try:
            # 假設有全域的 root 視窗
            import tkinter as tk
            root = tk._default_root
            if root:
                root.after(0, callback)
            else:
                # 如果沒有 root，直接執行
                callback()
        except:
            # 備用方案：直接執行
            callback()

    def _default_error_handler(self, error: Exception):
        """預設錯誤處理器"""
        import tkinter.messagebox as messagebox
        messagebox.showerror("任務錯誤", f"執行任務時發生錯誤:\n{str(error)}")

    def cancel_task(self, task_id: str) -> bool:
        """
        取消任務

        Args:
            task_id: 任務識別碼

        Returns:
            是否成功取消
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task.future and not task.future.done():
                cancelled = task.future.cancel()
                if cancelled:
                    task.cancelled = True
                    task.status = "cancelled"
                    task.end_time = time.time()

                    self.progress_queue.put({
                        'task_id': task_id,
                        'progress': 0.0,
                        'status': 'cancelled',
                        'message': '任務已取消'
                    })

                    self.logger.info(f"任務已取消: {task_id}")
                    return True

        return False

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        取得任務狀態

        Args:
            task_id: 任務識別碼

        Returns:
            任務狀態資訊
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]

            duration = None
            if task.start_time:
                end_time = task.end_time or time.time()
                duration = end_time - task.start_time

            return {
                'task_id': task_id,
                'status': task.status,
                'progress': task.progress,
                'start_time': task.start_time,
                'end_time': task.end_time,
                'duration': duration,
                'cancelled': task.cancelled
            }

        return None

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """取得所有活動任務的狀態"""
        return [self.get_task_status(task_id) for task_id in self.active_tasks.keys()]

    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        等待任務完成

        Args:
            task_id: 任務識別碼
            timeout: 超時時間（秒）

        Returns:
            任務結果
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task.future:
                try:
                    return task.future.result(timeout=timeout)
                except Exception as e:
                    self.logger.error(f"等待任務 {task_id} 失敗: {e}")
                    raise

        raise ValueError(f"任務不存在: {task_id}")

    def shutdown(self, wait: bool = True):
        """
        關閉非同步管理器

        Args:
            wait: 是否等待所有任務完成
        """
        self.logger.info("正在關閉非同步管理器...")

        # 取消所有活動任務
        for task_id in list(self.active_tasks.keys()):
            self.cancel_task(task_id)

        # 關閉執行緒池
        self.executor.shutdown(wait=wait)

        self.logger.info("非同步管理器已關閉")

    def __del__(self):
        """析構函數"""
        try:
            self.shutdown(wait=False)
        except:
            pass


# 全域非同步管理器實例
_async_manager = None
_async_lock = threading.Lock()


def get_async_manager() -> AsyncManager:
    """
    取得非同步管理器單例

    Returns:
        AsyncManager: 非同步管理器實例
    """
    global _async_manager

    if _async_manager is None:
        with _async_lock:
            if _async_manager is None:
                _async_manager = AsyncManager()

    return _async_manager


def create_progress_updater(task_id: str, async_manager: AsyncManager = None):
    """
    建立進度更新器

    Args:
        task_id: 任務識別碼
        async_manager: 非同步管理器實例

    Returns:
        進度更新函數
    """
    if async_manager is None:
        async_manager = get_async_manager()

    def update_progress(progress: float, message: str = ""):
        """
        更新任務進度

        Args:
            progress: 進度百分比 (0-100)
            message: 進度訊息
        """
        async_manager.progress_queue.put({
            'task_id': task_id,
            'progress': progress,
            'message': message
        })

    return update_progress