"""
快取管理器

實作資料快取機制，提升查詢效能和減少資料庫負載。
"""

import logging
import threading
import time
import hashlib
import pickle
from typing import Any, Optional, Dict, List, Callable, Tuple
from datetime import datetime, timedelta
from taiwan_railway_gui.interfaces import CacheManagerInterface


class CacheEntry:
    """快取項目類別"""

    def __init__(self, key: str, value: Any, ttl: int = 3600):
        """
        初始化快取項目

        Args:
            key: 快取鍵
            value: 快取值
            ttl: 存活時間（秒）
        """
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at

    @property
    def is_expired(self) -> bool:
        """檢查是否已過期"""
        return time.time() - self.created_at > self.ttl

    @property
    def age(self) -> float:
        """取得快取項目年齡（秒）"""
        return time.time() - self.created_at

    def access(self) -> Any:
        """存取快取項目"""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value

    def size_estimate(self) -> int:
        """估算快取項目大小（位元組）"""
        try:
            return len(pickle.dumps(self.value))
        except:
            return 1024  # 預設估算值


class CacheManager(CacheManagerInterface):
    """
    快取管理器實作

    提供多層級快取機制，支援 TTL、LRU 淘汰和記憶體管理。
    """

    def __init__(self, max_size: int = 100, default_ttl: int = 3600, max_memory_mb: int = 50):
        """
        初始化快取管理器

        Args:
            max_size: 最大快取項目數量
            default_ttl: 預設存活時間（秒）
            max_memory_mb: 最大記憶體使用量（MB）
        """
        self.logger = logging.getLogger(__name__)
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.max_memory_bytes = max_memory_mb * 1024 * 1024

        # 快取儲存
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # LRU 順序

        # 統計資訊
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired_removals': 0
        }

        # 執行緒安全
        self.lock = threading.RLock()

        # 啟動清理執行緒
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """啟動定期清理執行緒"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # 每5分鐘清理一次
                    self._cleanup_expired()
                    self._enforce_memory_limit()
                except Exception as e:
                    self.logger.error(f"快取清理錯誤: {e}")

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

    def _generate_key(self, *args, **kwargs) -> str:
        """
        產生快取鍵

        Args:
            *args: 位置參數
            **kwargs: 關鍵字參數

        Returns:
            快取鍵字串
        """
        # 建立可序列化的資料
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }

        # 產生雜湊
        key_str = str(key_data)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        取得快取值

        Args:
            key: 快取鍵

        Returns:
            快取值或 None
        """
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]

                # 檢查是否過期
                if entry.is_expired:
                    self._remove_entry(key)
                    self.stats['expired_removals'] += 1
                    self.stats['misses'] += 1
                    return None

                # 更新 LRU 順序
                self._update_access_order(key)

                # 統計命中
                self.stats['hits'] += 1

                return entry.access()

            # 統計未命中
            self.stats['misses'] += 1
            return None

    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        儲存快取值

        Args:
            key: 快取鍵
            value: 快取值
            ttl: 存活時間（秒），None 使用預設值

        Returns:
            是否成功儲存
        """
        if ttl is None:
            ttl = self.default_ttl

        with self.lock:
            try:
                # 建立快取項目
                entry = CacheEntry(key, value, ttl)

                # 檢查記憶體限制
                if self._would_exceed_memory_limit(entry):
                    self._enforce_memory_limit()

                    # 再次檢查
                    if self._would_exceed_memory_limit(entry):
                        self.logger.warning(f"快取項目太大，無法儲存: {key}")
                        return False

                # 如果鍵已存在，移除舊項目
                if key in self.cache:
                    self._remove_entry(key)

                # 檢查大小限制
                if len(self.cache) >= self.max_size:
                    self._evict_lru()

                # 儲存新項目
                self.cache[key] = entry
                self.access_order.append(key)

                self.logger.debug(f"快取已儲存: {key}, TTL: {ttl}s")
                return True

            except Exception as e:
                self.logger.error(f"儲存快取失敗: {e}")
                return False

    def remove(self, key: str) -> bool:
        """
        移除快取項目

        Args:
            key: 快取鍵

        Returns:
            是否成功移除
        """
        with self.lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False

    def clear(self):
        """清除所有快取"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.logger.info("快取已清除")

    def _remove_entry(self, key: str):
        """移除快取項目（內部方法）"""
        if key in self.cache:
            del self.cache[key]

        if key in self.access_order:
            self.access_order.remove(key)

    def _update_access_order(self, key: str):
        """更新存取順序"""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)

    def _evict_lru(self):
        """淘汰最少使用的項目"""
        if self.access_order:
            lru_key = self.access_order[0]
            self._remove_entry(lru_key)
            self.stats['evictions'] += 1
            self.logger.debug(f"LRU 淘汰: {lru_key}")

    def _cleanup_expired(self):
        """清理過期項目"""
        with self.lock:
            expired_keys = []
            for key, entry in self.cache.items():
                if entry.is_expired:
                    expired_keys.append(key)

            for key in expired_keys:
                self._remove_entry(key)
                self.stats['expired_removals'] += 1

            if expired_keys:
                self.logger.info(f"清理了 {len(expired_keys)} 個過期快取項目")

    def _would_exceed_memory_limit(self, entry: CacheEntry) -> bool:
        """檢查是否會超過記憶體限制"""
        current_memory = self.get_memory_usage()
        entry_size = entry.size_estimate()
        return current_memory + entry_size > self.max_memory_bytes

    def _enforce_memory_limit(self):
        """強制執行記憶體限制"""
        with self.lock:
            while self.get_memory_usage() > self.max_memory_bytes and self.cache:
                self._evict_lru()

    def get_memory_usage(self) -> int:
        """取得目前記憶體使用量（位元組）"""
        total_size = 0
        for entry in self.cache.values():
            total_size += entry.size_estimate()
        return total_size

    def get_stats(self) -> Dict[str, Any]:
        """取得快取統計資訊"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0

            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'memory_usage_mb': self.get_memory_usage() / (1024 * 1024),
                'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': hit_rate,
                'evictions': self.stats['evictions'],
                'expired_removals': self.stats['expired_removals']
            }

    def get_cache_info(self) -> List[Dict[str, Any]]:
        """取得快取項目資訊"""
        with self.lock:
            info = []
            for key, entry in self.cache.items():
                info.append({
                    'key': key,
                    'size_bytes': entry.size_estimate(),
                    'age_seconds': entry.age,
                    'ttl_seconds': entry.ttl,
                    'access_count': entry.access_count,
                    'last_accessed': entry.last_accessed,
                    'is_expired': entry.is_expired
                })

            # 按存取時間排序
            info.sort(key=lambda x: x['last_accessed'], reverse=True)
            return info

    def cached_call(self, func: Callable, *args, ttl: Optional[int] = None, **kwargs) -> Any:
        """
        快取函數呼叫結果

        Args:
            func: 要快取的函數
            *args: 函數參數
            ttl: 快取存活時間
            **kwargs: 函數關鍵字參數

        Returns:
            函數結果
        """
        # 產生快取鍵
        cache_key = f"{func.__name__}_{self._generate_key(*args, **kwargs)}"

        # 嘗試從快取取得
        cached_result = self.get(cache_key)
        if cached_result is not None:
            self.logger.debug(f"快取命中: {func.__name__}")
            return cached_result

        # 執行函數
        try:
            result = func(*args, **kwargs)

            # 儲存到快取
            self.put(cache_key, result, ttl)
            self.logger.debug(f"快取儲存: {func.__name__}")

            return result

        except Exception as e:
            self.logger.error(f"快取函數呼叫失敗: {func.__name__}, 錯誤: {e}")
            raise


def cache_decorator(ttl: int = 3600, cache_manager: Optional[CacheManager] = None):
    """
    快取裝飾器

    Args:
        ttl: 快取存活時間（秒）
        cache_manager: 快取管理器實例

    Returns:
        裝飾器函數
    """
    if cache_manager is None:
        cache_manager = get_cache_manager()

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            return cache_manager.cached_call(func, *args, ttl=ttl, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


# 全域快取管理器實例
_cache_manager = None
_cache_lock = threading.Lock()


def get_cache_manager() -> CacheManager:
    """
    取得快取管理器單例

    Returns:
        CacheManager: 快取管理器實例
    """
    global _cache_manager

    if _cache_manager is None:
        with _cache_lock:
            if _cache_manager is None:
                _cache_manager = CacheManager()

    return _cache_manager


def clear_all_caches():
    """清除所有快取"""
    cache_manager = get_cache_manager()
    cache_manager.clear()


def get_cache_stats() -> Dict[str, Any]:
    """取得快取統計資訊"""
    cache_manager = get_cache_manager()
    return cache_manager.get_stats()