"""
分頁管理器

實作大型資料集的分頁載入和管理功能。
"""

import logging
import math
from typing import List, Dict, Any, Optional, Callable, Tuple, Generic, TypeVar
from dataclasses import dataclass
from taiwan_railway_gui.interfaces import PaginationManagerInterface

T = TypeVar('T')


@dataclass
class PageInfo:
    """分頁資訊"""
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool
    start_index: int
    end_index: int


@dataclass
class PageResult(Generic[T]):
    """分頁結果"""
    items: List[T]
    page_info: PageInfo
    load_time: float
    cache_hit: bool = False


class PaginationManager(PaginationManagerInterface):
    """
    分頁管理器實作

    提供大型資料集的分頁載入、快取和管理功能。
    """

    def __init__(self, default_page_size: int = 50, max_page_size: int = 1000):
        """
        初始化分頁管理器

        Args:
            default_page_size: 預設頁面大小
            max_page_size: 最大頁面大小
        """
        self.logger = logging.getLogger(__name__)
        self.default_page_size = default_page_size
        self.max_page_size = max_page_size

        # 分頁快取
        self.page_cache: Dict[str, Dict[int, PageResult]] = {}
        self.total_count_cache: Dict[str, int] = {}

        # 統計資訊
        self.stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_items_loaded': 0
        }

    def create_page_info(self, current_page: int, page_size: int, total_items: int) -> PageInfo:
        """
        建立分頁資訊

        Args:
            current_page: 目前頁碼（從1開始）
            page_size: 頁面大小
            total_items: 總項目數

        Returns:
            分頁資訊
        """
        # 驗證參數
        current_page = max(1, current_page)
        page_size = min(max(1, page_size), self.max_page_size)
        total_items = max(0, total_items)

        # 計算分頁資訊
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
        current_page = min(current_page, total_pages)

        start_index = (current_page - 1) * page_size
        end_index = min(start_index + page_size, total_items)

        return PageInfo(
            current_page=current_page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_previous=current_page > 1,
            has_next=current_page < total_pages,
            start_index=start_index,
            end_index=end_index
        )

    def paginate_data(self, data: List[T], page: int = 1, page_size: Optional[int] = None) -> PageResult[T]:
        """
        對資料進行分頁

        Args:
            data: 要分頁的資料
            page: 頁碼（從1開始）
            page_size: 頁面大小

        Returns:
            分頁結果
        """
        import time
        start_time = time.time()

        if page_size is None:
            page_size = self.default_page_size

        # 建立分頁資訊
        page_info = self.create_page_info(page, page_size, len(data))

        # 取得頁面資料
        page_data = data[page_info.start_index:page_info.end_index]

        load_time = time.time() - start_time

        # 更新統計
        self.stats['total_queries'] += 1
        self.stats['total_items_loaded'] += len(page_data)

        return PageResult(
            items=page_data,
            page_info=page_info,
            load_time=load_time
        )

    def paginate_query(self, query_func: Callable[[int, int], Tuple[List[T], int]],
                      page: int = 1, page_size: Optional[int] = None,
                      cache_key: Optional[str] = None) -> PageResult[T]:
        """
        對查詢結果進行分頁

        Args:
            query_func: 查詢函數，接受 (offset, limit) 參數，返回 (items, total_count)
            page: 頁碼（從1開始）
            page_size: 頁面大小
            cache_key: 快取鍵

        Returns:
            分頁結果
        """
        import time
        start_time = time.time()

        if page_size is None:
            page_size = self.default_page_size

        # 檢查快取
        cache_hit = False
        if cache_key:
            cached_result = self._get_cached_page(cache_key, page, page_size)
            if cached_result:
                self.stats['total_queries'] += 1
                self.stats['cache_hits'] += 1
                cached_result.cache_hit = True
                return cached_result

        try:
            # 計算 offset 和 limit
            offset = (page - 1) * page_size
            limit = page_size

            # 執行查詢
            items, total_count = query_func(offset, limit)

            # 建立分頁資訊
            page_info = self.create_page_info(page, page_size, total_count)

            load_time = time.time() - start_time

            # 建立結果
            result = PageResult(
                items=items,
                page_info=page_info,
                load_time=load_time,
                cache_hit=cache_hit
            )

            # 快取結果
            if cache_key:
                self._cache_page(cache_key, page, page_size, result)
                self.total_count_cache[cache_key] = total_count

            # 更新統計
            self.stats['total_queries'] += 1
            self.stats['cache_misses'] += 1
            self.stats['total_items_loaded'] += len(items)

            return result

        except Exception as e:
            self.logger.error(f"分頁查詢失敗: {e}")
            raise

    def _get_cached_page(self, cache_key: str, page: int, page_size: int) -> Optional[PageResult]:
        """取得快取的頁面"""
        if cache_key in self.page_cache:
            page_cache = self.page_cache[cache_key]
            cache_page_key = f"{page}_{page_size}"

            if cache_page_key in page_cache:
                return page_cache[cache_page_key]

        return None

    def _cache_page(self, cache_key: str, page: int, page_size: int, result: PageResult):
        """快取頁面結果"""
        if cache_key not in self.page_cache:
            self.page_cache[cache_key] = {}

        cache_page_key = f"{page}_{page_size}"
        self.page_cache[cache_key][cache_page_key] = result

    def get_total_count(self, cache_key: str) -> Optional[int]:
        """取得總數量（從快取）"""
        return self.total_count_cache.get(cache_key)

    def clear_cache(self, cache_key: Optional[str] = None):
        """
        清除快取

        Args:
            cache_key: 要清除的快取鍵，None 表示清除所有
        """
        if cache_key:
            if cache_key in self.page_cache:
                del self.page_cache[cache_key]
            if cache_key in self.total_count_cache:
                del self.total_count_cache[cache_key]
            self.logger.info(f"已清除快取: {cache_key}")
        else:
            self.page_cache.clear()
            self.total_count_cache.clear()
            self.logger.info("已清除所有分頁快取")

    def preload_pages(self, query_func: Callable[[int, int], Tuple[List[T], int]],
                     cache_key: str, start_page: int = 1, end_page: int = 3,
                     page_size: Optional[int] = None) -> List[PageResult[T]]:
        """
        預載入多個頁面

        Args:
            query_func: 查詢函數
            cache_key: 快取鍵
            start_page: 開始頁碼
            end_page: 結束頁碼
            page_size: 頁面大小

        Returns:
            預載入的頁面結果列表
        """
        if page_size is None:
            page_size = self.default_page_size

        results = []

        for page in range(start_page, end_page + 1):
            try:
                result = self.paginate_query(query_func, page, page_size, cache_key)
                results.append(result)

                # 如果沒有更多頁面，停止預載入
                if not result.page_info.has_next:
                    break

            except Exception as e:
                self.logger.error(f"預載入頁面 {page} 失敗: {e}")
                break

        self.logger.info(f"預載入了 {len(results)} 個頁面")
        return results

    def get_page_navigation_info(self, page_info: PageInfo, window_size: int = 5) -> Dict[str, Any]:
        """
        取得頁面導航資訊

        Args:
            page_info: 分頁資訊
            window_size: 導航視窗大小

        Returns:
            導航資訊
        """
        current_page = page_info.current_page
        total_pages = page_info.total_pages

        # 計算導航視窗
        half_window = window_size // 2
        start_page = max(1, current_page - half_window)
        end_page = min(total_pages, current_page + half_window)

        # 調整視窗以保持固定大小
        if end_page - start_page + 1 < window_size:
            if start_page == 1:
                end_page = min(total_pages, start_page + window_size - 1)
            else:
                start_page = max(1, end_page - window_size + 1)

        # 建立頁碼列表
        page_numbers = list(range(start_page, end_page + 1))

        return {
            'current_page': current_page,
            'total_pages': total_pages,
            'page_numbers': page_numbers,
            'has_previous': page_info.has_previous,
            'has_next': page_info.has_next,
            'previous_page': current_page - 1 if page_info.has_previous else None,
            'next_page': current_page + 1 if page_info.has_next else None,
            'first_page': 1,
            'last_page': total_pages,
            'show_first_ellipsis': start_page > 2,
            'show_last_ellipsis': end_page < total_pages - 1
        }

    def get_stats(self) -> Dict[str, Any]:
        """取得統計資訊"""
        total_queries = self.stats['total_queries']
        cache_hit_rate = self.stats['cache_hits'] / total_queries if total_queries > 0 else 0

        return {
            'total_queries': total_queries,
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': cache_hit_rate,
            'total_items_loaded': self.stats['total_items_loaded'],
            'cached_keys': len(self.page_cache),
            'total_cached_pages': sum(len(pages) for pages in self.page_cache.values())
        }

    def optimize_page_size(self, total_items: int, target_load_time: float = 0.5) -> int:
        """
        根據資料量最佳化頁面大小

        Args:
            total_items: 總項目數
            target_load_time: 目標載入時間（秒）

        Returns:
            建議的頁面大小
        """
        # 基於總項目數的建議
        if total_items <= 100:
            suggested_size = 25
        elif total_items <= 1000:
            suggested_size = 50
        elif total_items <= 10000:
            suggested_size = 100
        else:
            suggested_size = 200

        # 確保在允許範圍內
        return min(max(suggested_size, 10), self.max_page_size)


# 全域分頁管理器實例
_pagination_manager = None


def get_pagination_manager() -> PaginationManager:
    """
    取得分頁管理器單例

    Returns:
        PaginationManager: 分頁管理器實例
    """
    global _pagination_manager

    if _pagination_manager is None:
        _pagination_manager = PaginationManager()

    return _pagination_manager


def paginate_list(data: List[T], page: int = 1, page_size: int = 50) -> PageResult[T]:
    """
    便利函數：對列表進行分頁

    Args:
        data: 要分頁的資料
        page: 頁碼
        page_size: 頁面大小

    Returns:
        分頁結果
    """
    manager = get_pagination_manager()
    return manager.paginate_data(data, page, page_size)