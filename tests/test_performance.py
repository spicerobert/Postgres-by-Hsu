"""
效能測試

測試非同步處理、快取機制和分頁功能的效能。
"""

import unittest
import time
import threading
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock
from taiwan_railway_gui.services.async_manager import AsyncManager, get_async_manager
from taiwan_railway_gui.services.cache_manager import CacheManager, get_cache_manager, cache_decorator
from taiwan_railway_gui.services.pagination_manager import PaginationManager, get_pagination_manager
from taiwan_railway_gui.dao.passenger_flow_dao import create_passenger_flow_dao
from taiwan_railway_gui.models.passenger_flow import PassengerFlow


class TestAsyncManager(unittest.TestCase):
    """測試非同步管理器"""

    def setUp(self):
        """設定測試環境"""
        self.async_manager = AsyncManager(max_workers=2)

    def tearDown(self):
        """清理測試環境"""
        self.async_manager.shutdown(wait=True)

    def test_submit_simple_task(self):
        """測試提交簡單任務"""
        result_container = []

        def simple_task():
            time.sleep(0.1)
            return "task_result"

        def callback(result):
            result_container.append(result)

        task_id = self.async_manager.submit_task(simple_task, callback)

        # 等待任務完成
        result = self.async_manager.wait_for_task(task_id, timeout=2.0)

        self.assertEqual(result, "task_result")
        time.sleep(0.2)  # 等待回調執行
        self.assertEqual(len(result_container), 1)
        self.assertEqual(result_container[0], "task_result")

    def test_task_error_handling(self):
        """測試任務錯誤處理"""
        error_container = []

        def failing_task():
            raise ValueError("測試錯誤")

        def error_callback(error):
            error_container.append(error)

        task_id = self.async_manager.submit_task(failing_task, error_callback=error_callback)

        with self.assertRaises(ValueError):
            self.async_manager.wait_for_task(task_id, timeout=2.0)

        time.sleep(0.2)  # 等待錯誤回調執行
        self.assertEqual(len(error_container), 1)
        self.assertIsInstance(error_container[0], ValueError)

    def test_task_cancellation(self):
        """測試任務取消"""
        def long_running_task():
            time.sleep(2.0)
            return "completed"

        task_id = self.async_manager.submit_task(long_running_task)

        # 立即取消任務
        cancelled = self.async_manager.cancel_task(task_id)
        self.assertTrue(cancelled)

        # 檢查任務狀態
        status = self.async_manager.get_task_status(task_id)
        self.assertIsNotNone(status)
        self.assertEqual(status['status'], 'cancelled')

    def test_multiple_concurrent_tasks(self):
        """測試多個並發任務"""
        results = []

        def task_func(task_num):
            time.sleep(0.1)
            return f"task_{task_num}_result"

        def callback(result):
            results.append(result)

        # 提交多個任務
        task_ids = []
        for i in range(5):
            task_id = self.async_manager.submit_task(
                lambda i=i: task_func(i), callback
            )
            task_ids.append(task_id)

        # 等待所有任務完成
        for task_id in task_ids:
            self.async_manager.wait_for_task(task_id, timeout=2.0)

        time.sleep(0.2)  # 等待回調執行
        self.assertEqual(len(results), 5)

    def test_task_progress_tracking(self):
        """測試任務進度追蹤"""
        progress_updates = []

        def progress_callback(progress, message):
            progress_updates.append((progress, message))

        def task_with_progress():
            # 模擬進度更新
            return "completed"

        task_id = self.async_manager.submit_task(
            task_with_progress,
            progress_callback=progress_callback
        )

        result = self.async_manager.wait_for_task(task_id, timeout=2.0)
        self.assertEqual(result, "completed")


class TestCacheManager(unittest.TestCase):
    """測試快取管理器"""

    def setUp(self):
        """設定測試環境"""
        self.cache_manager = CacheManager(max_size=10, default_ttl=1)

    def test_basic_cache_operations(self):
        """測試基本快取操作"""
        # 測試儲存和取得
        self.assertTrue(self.cache_manager.put("key1", "value1"))
        self.assertEqual(self.cache_manager.get("key1"), "value1")

        # 測試不存在的鍵
        self.assertIsNone(self.cache_manager.get("nonexistent"))

        # 測試移除
        self.assertTrue(self.cache_manager.remove("key1"))
        self.assertIsNone(self.cache_manager.get("key1"))

    def test_cache_expiration(self):
        """測試快取過期"""
        # 儲存短期快取項目
        self.cache_manager.put("temp_key", "temp_value", ttl=0.1)
        self.assertEqual(self.cache_manager.get("temp_key"), "temp_value")

        # 等待過期
        time.sleep(0.2)
        self.assertIsNone(self.cache_manager.get("temp_key"))

    def test_lru_eviction(self):
        """測試 LRU 淘汰機制"""
        # 填滿快取
        for i in range(10):
            self.cache_manager.put(f"key_{i}", f"value_{i}")

        # 存取前幾個項目以更新 LRU 順序
        for i in range(5):
            self.cache_manager.get(f"key_{i}")

        # 加入新項目，應該淘汰最少使用的項目
        self.cache_manager.put("new_key", "new_value")

        # 檢查 LRU 項目是否被淘汰
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats['evictions'], 1)

    def test_cache_decorator(self):
        """測試快取裝飾器"""
        call_count = 0

        @cache_decorator(ttl=1, cache_manager=self.cache_manager)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # 第一次呼叫
        result1 = expensive_function(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(call_count, 1)

        # 第二次呼叫（應該從快取取得）
        result2 = expensive_function(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count, 1)  # 沒有增加

        # 不同參數的呼叫
        result3 = expensive_function(2, 3)
        self.assertEqual(result3, 5)
        self.assertEqual(call_count, 2)  # 增加了

    def test_memory_management(self):
        """測試記憶體管理"""
        # 儲存一些資料
        for i in range(5):
            large_data = "x" * 1000  # 1KB 資料
            self.cache_manager.put(f"large_key_{i}", large_data)

        # 檢查記憶體使用量
        memory_usage = self.cache_manager.get_memory_usage()
        self.assertGreater(memory_usage, 0)

        # 清除快取
        self.cache_manager.clear()

        # 檢查記憶體是否釋放
        memory_usage_after = self.cache_manager.get_memory_usage()
        self.assertEqual(memory_usage_after, 0)

    def test_cache_statistics(self):
        """測試快取統計"""
        # 執行一些操作
        self.cache_manager.put("key1", "value1")
        self.cache_manager.get("key1")  # 命中
        self.cache_manager.get("nonexistent")  # 未命中

        stats = self.cache_manager.get_stats()

        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['hit_rate'], 0.5)
        self.assertEqual(stats['size'], 1)


class TestPaginationManager(unittest.TestCase):
    """測試分頁管理器"""

    def setUp(self):
        """設定測試環境"""
        self.pagination_manager = PaginationManager(default_page_size=10)

    def test_paginate_data(self):
        """測試資料分頁"""
        # 建立測試資料
        data = list(range(25))  # 0-24

        # 測試第一頁
        result = self.pagination_manager.paginate_data(data, page=1, page_size=10)

        self.assertEqual(len(result.items), 10)
        self.assertEqual(result.items, list(range(10)))
        self.assertEqual(result.page_info.current_page, 1)
        self.assertEqual(result.page_info.total_pages, 3)
        self.assertTrue(result.page_info.has_next)
        self.assertFalse(result.page_info.has_previous)

        # 測試最後一頁
        result = self.pagination_manager.paginate_data(data, page=3, page_size=10)

        self.assertEqual(len(result.items), 5)  # 最後一頁只有5個項目
        self.assertEqual(result.items, list(range(20, 25)))
        self.assertEqual(result.page_info.current_page, 3)
        self.assertFalse(result.page_info.has_next)
        self.assertTrue(result.page_info.has_previous)

    def test_paginate_query(self):
        """測試查詢分頁"""
        # 模擬查詢函數
        def mock_query(offset, limit):
            total_data = list(range(50))
            return total_data[offset:offset+limit], len(total_data)

        # 測試查詢分頁
        result = self.pagination_manager.paginate_query(
            mock_query, page=2, page_size=10, cache_key="test_query"
        )

        self.assertEqual(len(result.items), 10)
        self.assertEqual(result.items, list(range(10, 20)))
        self.assertEqual(result.page_info.current_page, 2)
        self.assertEqual(result.page_info.total_pages, 5)

    def test_pagination_cache(self):
        """測試分頁快取"""
        call_count = 0

        def mock_query(offset, limit):
            nonlocal call_count
            call_count += 1
            total_data = list(range(30))
            return total_data[offset:offset+limit], len(total_data)

        # 第一次查詢
        result1 = self.pagination_manager.paginate_query(
            mock_query, page=1, page_size=10, cache_key="cached_query"
        )
        self.assertEqual(call_count, 1)
        self.assertFalse(result1.cache_hit)

        # 第二次查詢相同頁面（應該從快取取得）
        result2 = self.pagination_manager.paginate_query(
            mock_query, page=1, page_size=10, cache_key="cached_query"
        )
        self.assertEqual(call_count, 1)  # 沒有增加
        self.assertTrue(result2.cache_hit)

    def test_preload_pages(self):
        """測試預載入頁面"""
        def mock_query(offset, limit):
            total_data = list(range(50))
            return total_data[offset:offset+limit], len(total_data)

        # 預載入前3頁
        results = self.pagination_manager.preload_pages(
            mock_query, "preload_test", start_page=1, end_page=3, page_size=10
        )

        self.assertEqual(len(results), 3)

        # 檢查每頁的資料
        for i, result in enumerate(results):
            expected_start = i * 10
            expected_end = (i + 1) * 10
            self.assertEqual(result.items, list(range(expected_start, expected_end)))

    def test_page_navigation_info(self):
        """測試頁面導航資訊"""
        page_info = self.pagination_manager.create_page_info(5, 10, 100)
        nav_info = self.pagination_manager.get_page_navigation_info(page_info, window_size=5)

        self.assertEqual(nav_info['current_page'], 5)
        self.assertEqual(nav_info['total_pages'], 10)
        self.assertEqual(nav_info['page_numbers'], [3, 4, 5, 6, 7])
        self.assertTrue(nav_info['has_previous'])
        self.assertTrue(nav_info['has_next'])

    def test_optimize_page_size(self):
        """測試頁面大小最佳化"""
        # 小資料集
        size1 = self.pagination_manager.optimize_page_size(50)
        self.assertEqual(size1, 25)

        # 中等資料集
        size2 = self.pagination_manager.optimize_page_size(500)
        self.assertEqual(size2, 50)

        # 大資料集
        size3 = self.pagination_manager.optimize_page_size(50000)
        self.assertEqual(size3, 200)


class TestPerformanceIntegration(unittest.TestCase):
    """測試效能整合"""

    def setUp(self):
        """設定測試環境"""
        self.start_date = date(2024, 1, 1)
        self.end_date = date(2024, 1, 31)

    @patch('taiwan_railway_gui.dao.database_manager.get_database_manager')
    def test_passenger_flow_dao_performance(self, mock_db_manager):
        """測試客流量 DAO 效能功能"""
        # 模擬資料庫管理器
        mock_db = Mock()
        mock_db_manager.return_value = mock_db

        # 模擬查詢結果
        mock_results = [
            {'station_code': '1001', 'date': date(2024, 1, 1), 'in_passengers': 100, 'out_passengers': 90},
            {'station_code': '1001', 'date': date(2024, 1, 2), 'in_passengers': 110, 'out_passengers': 95},
        ]
        mock_db.execute_query.return_value = mock_results

        # 建立 DAO
        dao = create_passenger_flow_dao()

        # 測試快取版本
        flows1 = dao.get_passenger_flow_cached('1001', self.start_date, self.end_date)
        flows2 = dao.get_passenger_flow_cached('1001', self.start_date, self.end_date)

        # 第二次呼叫應該從快取取得
        self.assertEqual(len(flows1), 2)
        self.assertEqual(len(flows2), 2)

    @patch('taiwan_railway_gui.dao.database_manager.get_database_manager')
    def test_paginated_query_performance(self, mock_db_manager):
        """測試分頁查詢效能"""
        # 模擬資料庫管理器
        mock_db = Mock()
        mock_db_manager.return_value = mock_db

        # 模擬總數查詢
        mock_db.execute_query.side_effect = [
            [{'total': 100}],  # 總數查詢
            [{'station_code': '1001', 'date': date(2024, 1, 1), 'in_passengers': 100, 'out_passengers': 90}] * 10  # 分頁資料
        ]

        # 建立 DAO
        dao = create_passenger_flow_dao()

        # 測試分頁查詢
        page_result = dao.get_passenger_flow_paginated('1001', self.start_date, self.end_date, page=1, page_size=10)

        self.assertEqual(len(page_result.items), 10)
        self.assertEqual(page_result.page_info.total_items, 100)
        self.assertEqual(page_result.page_info.total_pages, 10)

    def test_memory_usage_monitoring(self):
        """測試記憶體使用監控"""
        cache_manager = get_cache_manager()

        # 儲存一些測試資料
        for i in range(10):
            cache_manager.put(f"test_key_{i}", f"test_value_{i}" * 100)

        # 檢查記憶體使用
        stats = cache_manager.get_stats()
        self.assertGreater(stats['memory_usage_mb'], 0)
        self.assertEqual(stats['size'], 10)

        # 清除快取
        cache_manager.clear()

        # 檢查記憶體釋放
        stats_after = cache_manager.get_stats()
        self.assertEqual(stats_after['memory_usage_mb'], 0)
        self.assertEqual(stats_after['size'], 0)

    def test_concurrent_cache_access(self):
        """測試並發快取存取"""
        cache_manager = get_cache_manager()
        results = []
        errors = []

        def cache_worker(worker_id):
            try:
                for i in range(10):
                    key = f"worker_{worker_id}_key_{i}"
                    value = f"worker_{worker_id}_value_{i}"

                    # 儲存
                    cache_manager.put(key, value)

                    # 取得
                    retrieved = cache_manager.get(key)
                    results.append((key, retrieved))

                    time.sleep(0.01)  # 模擬處理時間
            except Exception as e:
                errors.append(e)

        # 建立多個執行緒
        threads = []
        for i in range(3):
            thread = threading.Thread(target=cache_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有執行緒完成
        for thread in threads:
            thread.join()

        # 檢查結果
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 30)  # 3個工作者 × 10個項目


if __name__ == '__main__':
    unittest.main()