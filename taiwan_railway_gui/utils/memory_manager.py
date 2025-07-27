"""
記憶體管理工具

提供記憶體使用監控、清理和最佳化功能。
"""

import gc
import logging
import psutil
import threading
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from taiwan_railway_gui.services.cache_manager import get_cache_manager
from taiwan_railway_gui.services.pagination_manager import get_pagination_manager


@dataclass
class MemoryInfo:
    """記憶體資訊"""
    total_mb: float
    available_mb: float
    used_mb: float
    percent: float
    process_mb: float


@dataclass
class MemoryAlert:
    """記憶體警告"""
    timestamp: float
    level: str  # 'warning', 'critical'
    message: str
    memory_info: MemoryInfo


class MemoryManager:
    """
    記憶體管理器

    監控記憶體使用量，提供自動清理和警告功能。
    """

    def __init__(self, warning_threshold: float = 80.0, critical_threshold: float = 90.0):
        """
        初始化記憶體管理器

        Args:
            warning_threshold: 警告閾值（百分比）
            critical_threshold: 嚴重警告閾值（百分比）
        """
        self.logger = logging.getLogger(__name__)
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

        # 記憶體監控
        self.monitoring_enabled = False
        self.monitor_interval = 30  # 秒
        self.monitor_thread = None

        # 警告處理
        self.alert_callbacks: List[Callable[[MemoryAlert], None]] = []
        self.recent_alerts: List[MemoryAlert] = []
        self.max_alerts_history = 100

        # 自動清理
        self.auto_cleanup_enabled = True
        self.cleanup_callbacks: List[Callable[[], None]] = []

        # 統計資訊
        self.stats = {
            'cleanup_count': 0,
            'alerts_count': 0,
            'max_memory_used': 0.0
        }

        # 執行緒安全
        self.lock = threading.RLock()

    def get_memory_info(self) -> MemoryInfo:
        """取得目前記憶體資訊"""
        try:
            # 系統記憶體資訊
            memory = psutil.virtual_memory()

            # 目前程序記憶體資訊
            process = psutil.Process()
            process_memory = process.memory_info()

            return MemoryInfo(
                total_mb=memory.total / (1024 * 1024),
                available_mb=memory.available / (1024 * 1024),
                used_mb=memory.used / (1024 * 1024),
                percent=memory.percent,
                process_mb=process_memory.rss / (1024 * 1024)
            )
        except Exception as e:
            self.logger.error(f"取得記憶體資訊失敗: {e}")
            return MemoryInfo(0, 0, 0, 0, 0)

    def start_monitoring(self):
        """開始記憶體監控"""
        if self.monitoring_enabled:
            return

        self.monitoring_enabled = True

        def monitor_worker():
            while self.monitoring_enabled:
                try:
                    self._check_memory_usage()
                    time.sleep(self.monitor_interval)
                except Exception as e:
                    self.logger.error(f"記憶體監控錯誤: {e}")

        self.monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        self.monitor_thread.start()

        self.logger.info("記憶體監控已啟動")

    def stop_monitoring(self):
        """停止記憶體監控"""
        self.monitoring_enabled = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self.logger.info("記憶體監控已停止")

    def _check_memory_usage(self):
        """檢查記憶體使用量"""
        memory_info = self.get_memory_info()

        with self.lock:
            # 更新最大記憶體使用量
            if memory_info.percent > self.stats['max_memory_used']:
                self.stats['max_memory_used'] = memory_info.percent

            # 檢查是否需要警告
            if memory_info.percent >= self.critical_threshold:
                self._trigger_alert('critical', f"記憶體使用量達到嚴重水準: {memory_info.percent:.1f}%", memory_info)

                if self.auto_cleanup_enabled:
                    self._perform_cleanup()

            elif memory_info.percent >= self.warning_threshold:
                self._trigger_alert('warning', f"記憶體使用量偏高: {memory_info.percent:.1f}%", memory_info)

    def _trigger_alert(self, level: str, message: str, memory_info: MemoryInfo):
        """觸發記憶體警告"""
        alert = MemoryAlert(
            timestamp=time.time(),
            level=level,
            message=message,
            memory_info=memory_info
        )

        # 記錄警告
        self.recent_alerts.append(alert)
        if len(self.recent_alerts) > self.max_alerts_history:
            self.recent_alerts.pop(0)

        self.stats['alerts_count'] += 1

        # 記錄日誌
        if level == 'critical':
            self.logger.critical(message)
        else:
            self.logger.warning(message)

        # 呼叫警告回調
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"警告回調執行失敗: {e}")

    def _perform_cleanup(self):
        """執行記憶體清理"""
        self.logger.info("開始執行記憶體清理")

        try:
            # 清理快取
            cache_manager = get_cache_manager()
            cache_stats_before = cache_manager.get_stats()
            cache_manager.clear()

            # 清理分頁快取
            pagination_manager = get_pagination_manager()
            pagination_stats_before = pagination_manager.get_stats()
            pagination_manager.clear_cache()

            # 執行自訂清理回調
            for callback in self.cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"清理回調執行失敗: {e}")

            # 強制垃圾回收
            collected = gc.collect()

            self.stats['cleanup_count'] += 1

            self.logger.info(f"記憶體清理完成 - 快取項目: {cache_stats_before['size']}, "
                           f"分頁快取: {pagination_stats_before['total_cached_pages']}, "
                           f"垃圾回收: {collected} 個物件")

        except Exception as e:
            self.logger.error(f"記憶體清理失敗: {e}")

    def force_cleanup(self):
        """強制執行記憶體清理"""
        with self.lock:
            self._perform_cleanup()

    def register_alert_callback(self, callback: Callable[[MemoryAlert], None]):
        """
        註冊警告回調

        Args:
            callback: 警告回調函數
        """
        self.alert_callbacks.append(callback)

    def register_cleanup_callback(self, callback: Callable[[], None]):
        """
        註冊清理回調

        Args:
            callback: 清理回調函數
        """
        self.cleanup_callbacks.append(callback)

    def get_detailed_memory_usage(self) -> Dict[str, Any]:
        """取得詳細記憶體使用資訊"""
        memory_info = self.get_memory_info()

        # 快取記憶體使用
        cache_manager = get_cache_manager()
        cache_stats = cache_manager.get_stats()

        # 分頁記憶體使用
        pagination_manager = get_pagination_manager()
        pagination_stats = pagination_manager.get_stats()

        return {
            'system': {
                'total_mb': memory_info.total_mb,
                'available_mb': memory_info.available_mb,
                'used_mb': memory_info.used_mb,
                'percent': memory_info.percent
            },
            'process': {
                'memory_mb': memory_info.process_mb,
                'percent_of_system': (memory_info.process_mb / memory_info.total_mb) * 100
            },
            'cache': {
                'memory_mb': cache_stats['memory_usage_mb'],
                'items': cache_stats['size'],
                'hit_rate': cache_stats['hit_rate']
            },
            'pagination': {
                'cached_pages': pagination_stats['total_cached_pages'],
                'hit_rate': pagination_stats['cache_hit_rate']
            },
            'thresholds': {
                'warning': self.warning_threshold,
                'critical': self.critical_threshold
            },
            'monitoring': {
                'enabled': self.monitoring_enabled,
                'interval': self.monitor_interval
            }
        }

    def get_memory_recommendations(self) -> List[str]:
        """取得記憶體最佳化建議"""
        memory_info = self.get_memory_info()
        recommendations = []

        if memory_info.percent > self.critical_threshold:
            recommendations.extend([
                "記憶體使用量過高，建議立即清理快取",
                "考慮減少同時載入的資料量",
                "關閉不必要的功能或分頁"
            ])
        elif memory_info.percent > self.warning_threshold:
            recommendations.extend([
                "記憶體使用量偏高，建議定期清理快取",
                "考慮使用分頁載入大型資料集"
            ])

        # 快取相關建議
        cache_stats = get_cache_manager().get_stats()
        if cache_stats['memory_usage_mb'] > 20:  # 超過20MB
            recommendations.append("快取使用量較高，考慮調整快取大小限制")

        if cache_stats['hit_rate'] < 0.5:  # 命中率低於50%
            recommendations.append("快取命中率較低，考慮調整快取策略")

        return recommendations

    def get_stats(self) -> Dict[str, Any]:
        """取得記憶體管理統計資訊"""
        with self.lock:
            return {
                'cleanup_count': self.stats['cleanup_count'],
                'alerts_count': self.stats['alerts_count'],
                'max_memory_used': self.stats['max_memory_used'],
                'recent_alerts_count': len(self.recent_alerts),
                'monitoring_enabled': self.monitoring_enabled,
                'auto_cleanup_enabled': self.auto_cleanup_enabled
            }

    def get_recent_alerts(self, limit: int = 10) -> List[MemoryAlert]:
        """取得最近的記憶體警告"""
        with self.lock:
            return self.recent_alerts[-limit:] if self.recent_alerts else []

    def set_thresholds(self, warning: float, critical: float):
        """
        設定記憶體警告閾值

        Args:
            warning: 警告閾值（百分比）
            critical: 嚴重警告閾值（百分比）
        """
        if warning >= critical:
            raise ValueError("警告閾值必須小於嚴重警告閾值")

        self.warning_threshold = warning
        self.critical_threshold = critical

        self.logger.info(f"記憶體閾值已更新 - 警告: {warning}%, 嚴重: {critical}%")

    def enable_auto_cleanup(self, enabled: bool = True):
        """
        啟用或停用自動清理

        Args:
            enabled: 是否啟用自動清理
        """
        self.auto_cleanup_enabled = enabled
        self.logger.info(f"自動記憶體清理已{'啟用' if enabled else '停用'}")


# 全域記憶體管理器實例
_memory_manager = None
_memory_lock = threading.Lock()


def get_memory_manager() -> MemoryManager:
    """
    取得記憶體管理器單例

    Returns:
        MemoryManager: 記憶體管理器實例
    """
    global _memory_manager

    if _memory_manager is None:
        with _memory_lock:
            if _memory_manager is None:
                _memory_manager = MemoryManager()

    return _memory_manager


def cleanup_memory():
    """便利函數：執行記憶體清理"""
    memory_manager = get_memory_manager()
    memory_manager.force_cleanup()


def get_memory_usage() -> MemoryInfo:
    """便利函數：取得記憶體使用資訊"""
    memory_manager = get_memory_manager()
    return memory_manager.get_memory_info()


def start_memory_monitoring():
    """便利函數：開始記憶體監控"""
    memory_manager = get_memory_manager()
    memory_manager.start_monitoring()


def stop_memory_monitoring():
    """便利函數：停止記憶體監控"""
    memory_manager = get_memory_manager()
    memory_manager.stop_monitoring()