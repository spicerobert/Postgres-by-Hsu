"""
統一錯誤處理服務

提供統一的錯誤處理機制，包括錯誤分類、使用者友善訊息轉換、
錯誤記錄和優雅降級功能。
"""

import logging
import traceback
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Union, List
from enum import Enum
from dataclasses import dataclass
from taiwan_railway_gui.interfaces import ErrorHandlerInterface


class ErrorSeverity(Enum):
    """錯誤嚴重程度"""
    LOW = "low"          # 輕微錯誤，不影響主要功能
    MEDIUM = "medium"    # 中等錯誤，影響部分功能
    HIGH = "high"        # 嚴重錯誤，影響主要功能
    CRITICAL = "critical" # 致命錯誤，系統無法正常運作


class ErrorCategory(Enum):
    """錯誤類別"""
    DATABASE = "database"           # 資料庫相關錯誤
    VALIDATION = "validation"       # 輸入驗證錯誤
    NETWORK = "network"            # 網路連線錯誤
    FILE_IO = "file_io"            # 檔案 I/O 錯誤
    GUI = "gui"                    # GUI 相關錯誤
    BUSINESS_LOGIC = "business"    # 業務邏輯錯誤
    SYSTEM = "system"              # 系統錯誤
    UNKNOWN = "unknown"            # 未知錯誤


@dataclass
class ErrorInfo:
    """錯誤資訊"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    original_error: Exception
    user_message: str
    technical_message: str
    suggested_actions: List[str]
    timestamp: datetime
    context: Dict[str, Any]
    stack_trace: str


class ErrorHandler(ErrorHandlerInterface):
    """
    統一錯誤處理器

    提供錯誤分類、使用者友善訊息轉換、錯誤記錄和優雅降級功能。
    """

    def __init__(self):
        """初始化錯誤處理器"""
        self.logger = logging.getLogger(__name__)
        self._error_history: List[ErrorInfo] = []
        self._error_callbacks: Dict[ErrorCategory, List[Callable]] = {}
        self._lock = threading.Lock()

        # 初始化錯誤訊息映射
        self._init_error_messages()

        # 初始化降級策略
        self._init_fallback_strategies()

    def _init_error_messages(self):
        """初始化錯誤訊息映射"""
        self._error_messages = {
            # 資料庫錯誤
            "connection_failed": {
                "user": "無法連接到資料庫，請檢查網路連線或聯絡系統管理員。",
                "actions": ["檢查網路連線", "重新啟動應用程式", "聯絡技術支援"]
            },
            "query_timeout": {
                "user": "資料庫查詢逾時，請稍後再試或縮小查詢範圍。",
                "actions": ["縮小日期範圍", "選擇較少車站", "稍後重試"]
            },
            "data_integrity": {
                "user": "資料完整性錯誤，部分資料可能不正確。",
                "actions": ["重新整理資料", "聯絡技術支援"]
            },

            # 驗證錯誤
            "invalid_date_range": {
                "user": "日期範圍不正確，請檢查開始和結束日期。",
                "actions": ["檢查日期格式", "確認日期順序", "選擇有效的日期範圍"]
            },
            "invalid_station_code": {
                "user": "車站代碼格式不正確，請選擇有效的車站。",
                "actions": ["從下拉選單選擇車站", "檢查車站代碼格式"]
            },
            "invalid_input": {
                "user": "輸入資料格式不正確，請檢查並重新輸入。",
                "actions": ["檢查輸入格式", "參考範例格式", "清除後重新輸入"]
            },

            # 檔案 I/O 錯誤
            "file_not_found": {
                "user": "找不到指定的檔案，請檢查檔案路徑。",
                "actions": ["檢查檔案是否存在", "選擇其他檔案", "重新建立檔案"]
            },
            "permission_denied": {
                "user": "沒有檔案存取權限，請檢查檔案權限設定。",
                "actions": ["檢查檔案權限", "選擇其他位置", "以管理員身分執行"]
            },
            "disk_full": {
                "user": "磁碟空間不足，無法儲存檔案。",
                "actions": ["清理磁碟空間", "選擇其他儲存位置", "刪除不需要的檔案"]
            },

            # GUI 錯誤
            "widget_error": {
                "user": "介面元件發生錯誤，請重新整理頁面。",
                "actions": ["重新整理頁面", "重新啟動應用程式"]
            },
            "display_error": {
                "user": "顯示資料時發生錯誤，請稍後再試。",
                "actions": ["重新載入資料", "檢查資料格式"]
            },

            # 系統錯誤
            "memory_error": {
                "user": "記憶體不足，請關閉其他應用程式或減少資料量。",
                "actions": ["關閉其他應用程式", "減少查詢資料量", "重新啟動應用程式"]
            },
            "unknown_error": {
                "user": "發生未知錯誤，請聯絡技術支援。",
                "actions": ["重新啟動應用程式", "聯絡技術支援", "檢查系統日誌"]
            }
        }

    def _init_fallback_strategies(self):
        """初始化降級策略"""
        self._fallback_strategies = {
            ErrorCategory.DATABASE: self._database_fallback,
            ErrorCategory.VALIDATION: self._validation_fallback,
            ErrorCategory.FILE_IO: self._file_io_fallback,
            ErrorCategory.GUI: self._gui_fallback,
            ErrorCategory.NETWORK: self._network_fallback
        }

    def handle_error(self, error: Exception, context: Dict[str, Any] = None,
                    category: ErrorCategory = None, severity: ErrorSeverity = None) -> ErrorInfo:
        """
        處理錯誤

        Args:
            error: 原始錯誤
            context: 錯誤上下文資訊
            category: 錯誤類別
            severity: 錯誤嚴重程度

        Returns:
            ErrorInfo: 錯誤資訊物件
        """
        try:
            # 自動分類錯誤
            if category is None:
                category = self._classify_error(error)

            # 自動判斷嚴重程度
            if severity is None:
                severity = self._assess_severity(error, category)

            # 生成錯誤 ID
            error_id = self._generate_error_id(error, category)

            # 轉換為使用者友善訊息
            user_message, suggested_actions = self._get_user_friendly_message(error, category)

            # 建立錯誤資訊
            error_info = ErrorInfo(
                error_id=error_id,
                category=category,
                severity=severity,
                original_error=error,
                user_message=user_message,
                technical_message=str(error),
                suggested_actions=suggested_actions,
                timestamp=datetime.now(),
                context=context or {},
                stack_trace=traceback.format_exc()
            )

            # 記錄錯誤
            self._log_error(error_info)

            # 儲存到歷史記錄
            with self._lock:
                self._error_history.append(error_info)
                # 限制歷史記錄數量
                if len(self._error_history) > 1000:
                    self._error_history = self._error_history[-500:]

            # 觸發錯誤回調
            self._trigger_error_callbacks(error_info)

            # 執行降級策略
            self._execute_fallback_strategy(error_info)

            return error_info

        except Exception as handler_error:
            # 錯誤處理器本身發生錯誤
            self.logger.critical(f"錯誤處理器發生錯誤: {handler_error}")
            return self._create_fallback_error_info(error, handler_error)

    def _classify_error(self, error: Exception) -> ErrorCategory:
        """
        自動分類錯誤

        Args:
            error: 錯誤物件

        Returns:
            ErrorCategory: 錯誤類別
        """
        error_type = type(error).__name__
        error_message = str(error).lower()

        # 資料庫錯誤
        if any(keyword in error_message for keyword in
               ['connection', 'database', 'psycopg2', 'sql', 'cursor']):
            return ErrorCategory.DATABASE

        # 驗證錯誤
        if any(keyword in error_message for keyword in
               ['validation', 'invalid', 'format', 'range']):
            return ErrorCategory.VALIDATION

        # 檔案 I/O 錯誤
        if any(keyword in error_message for keyword in
               ['file', 'directory', 'permission', 'not found', 'io']):
            return ErrorCategory.FILE_IO

        # GUI 錯誤
        if any(keyword in error_message for keyword in
               ['tkinter', 'widget', 'gui', 'display']):
            return ErrorCategory.GUI

        # 網路錯誤
        if any(keyword in error_message for keyword in
               ['network', 'timeout', 'connection refused', 'host']):
            return ErrorCategory.NETWORK

        # 系統錯誤
        if error_type in ['MemoryError', 'SystemError', 'OSError']:
            return ErrorCategory.SYSTEM

        return ErrorCategory.UNKNOWN

    def _assess_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """
        評估錯誤嚴重程度

        Args:
            error: 錯誤物件
            category: 錯誤類別

        Returns:
            ErrorSeverity: 錯誤嚴重程度
        """
        error_type = type(error).__name__
        error_message = str(error).lower()

        # 致命錯誤
        if error_type in ['SystemExit', 'KeyboardInterrupt', 'MemoryError']:
            return ErrorSeverity.CRITICAL

        # 嚴重錯誤
        if category == ErrorCategory.DATABASE and 'connection' in error_message:
            return ErrorSeverity.HIGH

        if 'critical' in error_message or 'fatal' in error_message:
            return ErrorSeverity.HIGH

        # 中等錯誤
        if category in [ErrorCategory.FILE_IO, ErrorCategory.NETWORK]:
            return ErrorSeverity.MEDIUM

        # 輕微錯誤
        if category == ErrorCategory.VALIDATION:
            return ErrorSeverity.LOW

        return ErrorSeverity.MEDIUM

    def _generate_error_id(self, error: Exception, category: ErrorCategory) -> str:
        """
        生成錯誤 ID

        Args:
            error: 錯誤物件
            category: 錯誤類別

        Returns:
            str: 錯誤 ID
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        error_hash = hash(str(error)) % 10000
        return f"{category.value}_{timestamp}_{error_hash:04d}"

    def _get_user_friendly_message(self, error: Exception,
                                 category: ErrorCategory) -> tuple[str, List[str]]:
        """
        取得使用者友善的錯誤訊息

        Args:
            error: 錯誤物件
            category: 錯誤類別

        Returns:
            tuple[str, List[str]]: (使用者訊息, 建議動作列表)
        """
        error_message = str(error).lower()

        # 嘗試匹配特定錯誤訊息
        for error_key, message_info in self._error_messages.items():
            if error_key in error_message:
                return message_info["user"], message_info["actions"]

        # 根據錯誤類別提供通用訊息
        category_messages = {
            ErrorCategory.DATABASE: (
                "資料庫操作發生錯誤，請稍後再試。",
                ["檢查網路連線", "重新整理資料", "聯絡技術支援"]
            ),
            ErrorCategory.VALIDATION: (
                "輸入資料不正確，請檢查後重新輸入。",
                ["檢查輸入格式", "參考說明文件", "重新輸入"]
            ),
            ErrorCategory.FILE_IO: (
                "檔案操作發生錯誤，請檢查檔案權限和路徑。",
                ["檢查檔案權限", "確認檔案路徑", "選擇其他位置"]
            ),
            ErrorCategory.GUI: (
                "介面顯示發生錯誤，請重新整理。",
                ["重新整理頁面", "重新啟動應用程式"]
            ),
            ErrorCategory.NETWORK: (
                "網路連線發生錯誤，請檢查網路設定。",
                ["檢查網路連線", "重新連線", "稍後重試"]
            ),
            ErrorCategory.SYSTEM: (
                "系統發生錯誤，請重新啟動應用程式。",
                ["重新啟動應用程式", "檢查系統資源", "聯絡技術支援"]
            ),
            ErrorCategory.UNKNOWN: (
                "發生未知錯誤，請聯絡技術支援。",
                ["重新啟動應用程式", "聯絡技術支援"]
            )
        }

        return category_messages.get(category, category_messages[ErrorCategory.UNKNOWN])

    def _log_error(self, error_info: ErrorInfo):
        """
        記錄錯誤到日誌

        Args:
            error_info: 錯誤資訊
        """
        log_message = (
            f"錯誤 ID: {error_info.error_id}\n"
            f"類別: {error_info.category.value}\n"
            f"嚴重程度: {error_info.severity.value}\n"
            f"技術訊息: {error_info.technical_message}\n"
            f"使用者訊息: {error_info.user_message}\n"
            f"上下文: {error_info.context}\n"
            f"堆疊追蹤: {error_info.stack_trace}"
        )

        # 根據嚴重程度選擇日誌級別
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def _trigger_error_callbacks(self, error_info: ErrorInfo):
        """
        觸發錯誤回調函數

        Args:
            error_info: 錯誤資訊
        """
        callbacks = self._error_callbacks.get(error_info.category, [])
        for callback in callbacks:
            try:
                callback(error_info)
            except Exception as callback_error:
                self.logger.error(f"錯誤回調執行失敗: {callback_error}")

    def _execute_fallback_strategy(self, error_info: ErrorInfo):
        """
        執行降級策略

        Args:
            error_info: 錯誤資訊
        """
        strategy = self._fallback_strategies.get(error_info.category)
        if strategy:
            try:
                strategy(error_info)
            except Exception as fallback_error:
                self.logger.error(f"降級策略執行失敗: {fallback_error}")

    def _database_fallback(self, error_info: ErrorInfo):
        """資料庫錯誤降級策略"""
        self.logger.info("執行資料庫錯誤降級策略")
        # 可以實作快取資料回退、離線模式等

    def _validation_fallback(self, error_info: ErrorInfo):
        """驗證錯誤降級策略"""
        self.logger.info("執行驗證錯誤降級策略")
        # 可以實作預設值設定、格式自動修正等

    def _file_io_fallback(self, error_info: ErrorInfo):
        """檔案 I/O 錯誤降級策略"""
        self.logger.info("執行檔案 I/O 錯誤降級策略")
        # 可以實作臨時檔案、記憶體儲存等

    def _gui_fallback(self, error_info: ErrorInfo):
        """GUI 錯誤降級策略"""
        self.logger.info("執行 GUI 錯誤降級策略")
        # 可以實作簡化介面、文字模式等

    def _network_fallback(self, error_info: ErrorInfo):
        """網路錯誤降級策略"""
        self.logger.info("執行網路錯誤降級策略")
        # 可以實作離線模式、快取資料等

    def _create_fallback_error_info(self, original_error: Exception,
                                  handler_error: Exception) -> ErrorInfo:
        """
        建立降級錯誤資訊

        Args:
            original_error: 原始錯誤
            handler_error: 處理器錯誤

        Returns:
            ErrorInfo: 降級錯誤資訊
        """
        return ErrorInfo(
            error_id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            original_error=original_error,
            user_message="系統發生嚴重錯誤，請重新啟動應用程式。",
            technical_message=f"原始錯誤: {original_error}, 處理器錯誤: {handler_error}",
            suggested_actions=["重新啟動應用程式", "聯絡技術支援"],
            timestamp=datetime.now(),
            context={"handler_error": str(handler_error)},
            stack_trace=traceback.format_exc()
        )

    def register_error_callback(self, category: ErrorCategory, callback: Callable):
        """
        註冊錯誤回調函數

        Args:
            category: 錯誤類別
            callback: 回調函數
        """
        if category not in self._error_callbacks:
            self._error_callbacks[category] = []
        self._error_callbacks[category].append(callback)

    def get_error_history(self, category: ErrorCategory = None,
                         severity: ErrorSeverity = None,
                         limit: int = 100) -> List[ErrorInfo]:
        """
        取得錯誤歷史記錄

        Args:
            category: 錯誤類別篩選
            severity: 嚴重程度篩選
            limit: 記錄數量限制

        Returns:
            List[ErrorInfo]: 錯誤記錄列表
        """
        with self._lock:
            filtered_errors = self._error_history.copy()

        # 篩選條件
        if category:
            filtered_errors = [e for e in filtered_errors if e.category == category]

        if severity:
            filtered_errors = [e for e in filtered_errors if e.severity == severity]

        # 按時間排序並限制數量
        filtered_errors.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered_errors[:limit]

    def clear_error_history(self):
        """清除錯誤歷史記錄"""
        with self._lock:
            self._error_history.clear()
        self.logger.info("錯誤歷史記錄已清除")

    def get_error_statistics(self) -> Dict[str, Any]:
        """
        取得錯誤統計資訊

        Returns:
            Dict[str, Any]: 錯誤統計資訊
        """
        with self._lock:
            errors = self._error_history.copy()

        if not errors:
            return {"total": 0}

        # 按類別統計
        category_stats = {}
        for category in ErrorCategory:
            category_stats[category.value] = len([e for e in errors if e.category == category])

        # 按嚴重程度統計
        severity_stats = {}
        for severity in ErrorSeverity:
            severity_stats[severity.value] = len([e for e in errors if e.severity == severity])

        # 最近錯誤
        recent_errors = sorted(errors, key=lambda x: x.timestamp, reverse=True)[:5]

        return {
            "total": len(errors),
            "by_category": category_stats,
            "by_severity": severity_stats,
            "recent_errors": [
                {
                    "id": e.error_id,
                    "category": e.category.value,
                    "severity": e.severity.value,
                    "message": e.user_message,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in recent_errors
            ]
        }


# 全域錯誤處理器實例
_error_handler = None
_error_handler_lock = threading.Lock()


def get_error_handler() -> ErrorHandler:
    """
    取得錯誤處理器單例

    Returns:
        ErrorHandler: 錯誤處理器實例
    """
    global _error_handler

    if _error_handler is None:
        with _error_handler_lock:
            if _error_handler is None:
                _error_handler = ErrorHandler()

    return _error_handler


def handle_error(error: Exception, context: Dict[str, Any] = None,
                category: ErrorCategory = None, severity: ErrorSeverity = None) -> ErrorInfo:
    """
    便利函數：處理錯誤

    Args:
        error: 錯誤物件
        context: 錯誤上下文
        category: 錯誤類別
        severity: 錯誤嚴重程度

    Returns:
        ErrorInfo: 錯誤資訊
    """
    return get_error_handler().handle_error(error, context, category, severity)