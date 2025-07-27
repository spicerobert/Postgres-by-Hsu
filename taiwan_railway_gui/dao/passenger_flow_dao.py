"""
客流量資料存取物件

處理客流量相關的資料庫操作，包括查詢、統計和分析功能。
"""

import logging
from datetime import date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from taiwan_railway_gui.interfaces import PassengerFlowDAOInterface
from taiwan_railway_gui.models.passenger_flow import (
    PassengerFlow, StationStatistics, create_passenger_flow_from_dict, calculate_statistics
)
from taiwan_railway_gui.dao.database_manager import get_database_manager
from taiwan_railway_gui.dao.station_dao import create_station_dao
from taiwan_railway_gui.services.cache_manager import get_cache_manager, cache_decorator
from taiwan_railway_gui.services.pagination_manager import get_pagination_manager, PageResult
from taiwan_railway_gui.config import get_config


class PassengerFlowDAO(PassengerFlowDAOInterface):
    """
    客流量資料存取物件實作

    提供客流量資料的查詢、統計和分析功能。
    """

    def __init__(self):
        """初始化 DAO"""
        self.logger = logging.getLogger(__name__)
        self.db_manager = get_database_manager()
        self.station_dao = create_station_dao()
        self.cache_manager = get_cache_manager()
        self.pagination_manager = get_pagination_manager()

        # 錯誤訊息
        self.error_messages = get_config('errors')

    def get_passenger_flow(self, station_code: str, start_date: date, end_date: date) -> List[PassengerFlow]:
        """
        取得客流量資料

        Args:
            station_code: 車站代碼
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            List[PassengerFlow]: 客流量資料列表
        """
        try:
            # 驗證車站是否存在
            if not self.station_dao.station_exists(station_code):
                self.logger.warning(f"車站不存在: {station_code}")
                return []

            sql_query = """
            SELECT station_code, date, in_passengers, out_passengers
            FROM passenger_flow
            WHERE station_code = %s
              AND date >= %s
              AND date <= %s
            ORDER BY date
            """

            results = self.db_manager.execute_query(sql_query, (station_code, start_date, end_date))

            if not results:
                self.logger.info(f"查詢期間內沒有客流量資料: {station_code} ({start_date} ~ {end_date})")
                return []

            flows = []
            for row in results:
                try:
                    flow = create_passenger_flow_from_dict(dict(row))
                    flows.append(flow)
                except Exception as e:
                    self.logger.warning(f"建立客流量物件失敗: {e}, 資料: {row}")
                    continue

            self.logger.info(f"取得 {len(flows)} 筆客流量資料: {station_code}")
            return flows

        except Exception as e:
            self.logger.error(f"取得客流量資料失敗: {e}")
            return []

    def get_station_statistics(self, station_code: str, start_date: date, end_date: date) -> Optional[StationStatistics]:
        """
        取得車站統計資料

        Args:
            station_code: 車站代碼
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            Optional[StationStatistics]: 統計資料或 None
        """
        try:
            # 取得車站資訊
            station = self.station_dao.get_station_by_code(station_code)
            if not station:
                self.logger.warning(f"車站不存在: {station_code}")
                return None

            # 使用聚合查詢取得統計資料
            sql_query = """
            SELECT
                COUNT(*) as record_count,
                SUM(in_passengers) as total_in,
                SUM(out_passengers) as total_out,
                MIN(date) as min_date,
                MAX(date) as max_date
            FROM passenger_flow
            WHERE station_code = %s
              AND date >= %s
              AND date <= %s
            """

            result = self.db_manager.execute_query(sql_query, (station_code, start_date, end_date), fetch_one=True)

            if not result or result['record_count'] == 0:
                self.logger.info(f"查詢期間內沒有統計資料: {station_code}")
                return None

            total_in = int(result['total_in'] or 0)
            total_out = int(result['total_out'] or 0)
            total_passengers = total_in + total_out

            # 計算平均每日人數
            actual_start = result['min_date']
            actual_end = result['max_date']
            days_count = (actual_end - actual_start).days + 1
            average_daily = total_passengers / days_count if days_count > 0 else 0

            statistics = StationStatistics(
                station_code=station_code,
                station_name=station.station_name,
                total_in=total_in,
                total_out=total_out,
                total_passengers=total_passengers,
                average_daily=round(average_daily, 2),
                date_range=(actual_start, actual_end)
            )

            self.logger.info(f"取得統計資料: {station.station_name}, 總人數: {total_passengers:,}")
            return statistics

        except Exception as e:
            self.logger.error(f"取得車站統計資料失敗: {e}")
            return None

    def get_multiple_station_statistics(self, station_codes: List[str], start_date: date, end_date: date) -> List[StationStatistics]:
        """
        取得多個車站統計資料

        Args:
            station_codes: 車站代碼列表
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            List[StationStatistics]: 統計資料列表
        """
        if not station_codes:
            return []

        try:
            # 取得車站資訊
            stations = self.station_dao.get_stations_by_codes(station_codes)
            station_dict = {s.station_code: s for s in stations}

            # 批次查詢統計資料
            placeholders = ','.join(['%s'] * len(station_codes))
            sql_query = f"""
            SELECT
                station_code,
                COUNT(*) as record_count,
                SUM(in_passengers) as total_in,
                SUM(out_passengers) as total_out,
                MIN(date) as min_date,
                MAX(date) as max_date
            FROM passenger_flow
            WHERE station_code IN ({placeholders})
              AND date >= %s
              AND date <= %s
            GROUP BY station_code
            """

            params = tuple(station_codes) + (start_date, end_date)
            results = self.db_manager.execute_query(sql_query, params)

            if not results:
                self.logger.info("查詢期間內沒有統計資料")
                return []

            statistics_list = []
            for row in results:
                try:
                    station_code = row['station_code']
                    station = station_dict.get(station_code)

                    if not station:
                        self.logger.warning(f"找不到車站資訊: {station_code}")
                        continue

                    total_in = int(row['total_in'] or 0)
                    total_out = int(row['total_out'] or 0)
                    total_passengers = total_in + total_out

                    # 計算平均每日人數
                    actual_start = row['min_date']
                    actual_end = row['max_date']
                    days_count = (actual_end - actual_start).days + 1
                    average_daily = total_passengers / days_count if days_count > 0 else 0

                    statistics = StationStatistics(
                        station_code=station_code,
                        station_name=station.station_name,
                        total_in=total_in,
                        total_out=total_out,
                        total_passengers=total_passengers,
                        average_daily=round(average_daily, 2),
                        date_range=(actual_start, actual_end)
                    )

                    statistics_list.append(statistics)

                except Exception as e:
                    self.logger.warning(f"建立統計物件失敗: {e}, 資料: {row}")
                    continue

            # 按原始順序排序
            station_stats_dict = {s.station_code: s for s in statistics_list}
            ordered_statistics = [station_stats_dict[code] for code in station_codes if code in station_stats_dict]

            self.logger.info(f"取得 {len(ordered_statistics)} 個車站的統計資料")
            return ordered_statistics

        except Exception as e:
            self.logger.error(f"取得多個車站統計資料失敗: {e}")
            return []

    def get_daily_summary(self, start_date: date, end_date: date, limit: int = 10) -> List[Dict[str, Any]]:
        """
        取得每日總客流量摘要

        Args:
            start_date: 開始日期
            end_date: 結束日期
            limit: 限制結果數量

        Returns:
            List[Dict]: 每日摘要列表
        """
        try:
            sql_query = """
            SELECT
                date,
                COUNT(DISTINCT station_code) as station_count,
                SUM(in_passengers) as total_in,
                SUM(out_passengers) as total_out,
                SUM(in_passengers + out_passengers) as total_passengers
            FROM passenger_flow
            WHERE date >= %s AND date <= %s
            GROUP BY date
            ORDER BY date DESC
            LIMIT %s
            """

            results = self.db_manager.execute_query(sql_query, (start_date, end_date, limit))

            if not results:
                return []

            summaries = []
            for row in results:
                summary = {
                    'date': row['date'],
                    'station_count': int(row['station_count']),
                    'total_in': int(row['total_in'] or 0),
                    'total_out': int(row['total_out'] or 0),
                    'total_passengers': int(row['total_passengers'] or 0)
                }
                summaries.append(summary)

            self.logger.info(f"取得 {len(summaries)} 天的每日摘要")
            return summaries

        except Exception as e:
            self.logger.error(f"取得每日摘要失敗: {e}")
            return []

    def get_top_stations(self, start_date: date, end_date: date, limit: int = 10) -> List[StationStatistics]:
        """
        取得客流量最高的車站

        Args:
            start_date: 開始日期
            end_date: 結束日期
            limit: 限制結果數量

        Returns:
            List[StationStatistics]: 排名前幾的車站統計
        """
        try:
            sql_query = """
            SELECT
                pf.station_code,
                s.station_name,
                SUM(pf.in_passengers) as total_in,
                SUM(pf.out_passengers) as total_out,
                SUM(pf.in_passengers + pf.out_passengers) as total_passengers,
                MIN(pf.date) as min_date,
                MAX(pf.date) as max_date
            FROM passenger_flow pf
            JOIN stations s ON pf.station_code = s.station_code
            WHERE pf.date >= %s AND pf.date <= %s
            GROUP BY pf.station_code, s.station_name
            ORDER BY total_passengers DESC
            LIMIT %s
            """

            results = self.db_manager.execute_query(sql_query, (start_date, end_date, limit))

            if not results:
                return []

            top_stations = []
            for row in results:
                try:
                    total_in = int(row['total_in'] or 0)
                    total_out = int(row['total_out'] or 0)
                    total_passengers = int(row['total_passengers'] or 0)

                    # 計算平均每日人數
                    actual_start = row['min_date']
                    actual_end = row['max_date']
                    days_count = (actual_end - actual_start).days + 1
                    average_daily = total_passengers / days_count if days_count > 0 else 0

                    statistics = StationStatistics(
                        station_code=row['station_code'],
                        station_name=row['station_name'],
                        total_in=total_in,
                        total_out=total_out,
                        total_passengers=total_passengers,
                        average_daily=round(average_daily, 2),
                        date_range=(actual_start, actual_end)
                    )

                    top_stations.append(statistics)

                except Exception as e:
                    self.logger.warning(f"建立統計物件失敗: {e}")
                    continue

            self.logger.info(f"取得前 {len(top_stations)} 名車站")
            return top_stations

        except Exception as e:
            self.logger.error(f"取得熱門車站失敗: {e}")
            return []

    def get_date_range_available(self, station_code: str) -> Optional[tuple[date, date]]:
        """
        取得指定車站的可用資料日期範圍

        Args:
            station_code: 車站代碼

        Returns:
            Optional[tuple]: (最早日期, 最晚日期) 或 None
        """
        try:
            sql_query = """
            SELECT MIN(date) as min_date, MAX(date) as max_date
            FROM passenger_flow
            WHERE station_code = %s
            """

            result = self.db_manager.execute_query(sql_query, (station_code,), fetch_one=True)

            if not result or not result['min_date']:
                return None

            return (result['min_date'], result['max_date'])

        except Exception as e:
            self.logger.error(f"取得資料日期範圍失敗: {e}")
            return None

    def get_weekend_vs_weekday_stats(self, station_code: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        取得週末與平日的客流量比較統計

        Args:
            station_code: 車站代碼
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            Dict: 包含週末和平日統計的字典
        """
        try:
            sql_query = """
            SELECT
                CASE
                    WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN 'weekend'
                    ELSE 'weekday'
                END as day_type,
                COUNT(*) as day_count,
                AVG(in_passengers) as avg_in,
                AVG(out_passengers) as avg_out,
                AVG(in_passengers + out_passengers) as avg_total
            FROM passenger_flow
            WHERE station_code = %s
              AND date >= %s
              AND date <= %s
            GROUP BY day_type
            """

            results = self.db_manager.execute_query(sql_query, (station_code, start_date, end_date))

            stats = {
                'weekday': {'day_count': 0, 'avg_in': 0, 'avg_out': 0, 'avg_total': 0},
                'weekend': {'day_count': 0, 'avg_in': 0, 'avg_out': 0, 'avg_total': 0}
            }

            if results:
                for row in results:
                    day_type = row['day_type']
                    stats[day_type] = {
                        'day_count': int(row['day_count']),
                        'avg_in': round(float(row['avg_in'] or 0), 2),
                        'avg_out': round(float(row['avg_out'] or 0), 2),
                        'avg_total': round(float(row['avg_total'] or 0), 2)
                    }

            return stats

        except Exception as e:
            self.logger.error(f"取得週末平日統計失敗: {e}")
            return {}

    @cache_decorator(ttl=1800)  # 快取30分鐘
    def get_passenger_flow_cached(self, station_code: str, start_date: date, end_date: date) -> List[PassengerFlow]:
        """
        取得客流量資料（快取版本）

        Args:
            station_code: 車站代碼
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            List[PassengerFlow]: 客流量資料列表
        """
        return self.get_passenger_flow(station_code, start_date, end_date)

    def get_passenger_flow_paginated(self, station_code: str, start_date: date, end_date: date,
                                   page: int = 1, page_size: int = 50) -> PageResult[PassengerFlow]:
        """
        取得分頁的客流量資料

        Args:
            station_code: 車站代碼
            start_date: 開始日期
            end_date: 結束日期
            page: 頁碼（從1開始）
            page_size: 頁面大小

        Returns:
            PageResult[PassengerFlow]: 分頁結果
        """
        def query_func(offset: int, limit: int) -> Tuple[List[PassengerFlow], int]:
            try:
                # 驗證車站是否存在
                if not self.station_dao.station_exists(station_code):
                    self.logger.warning(f"車站不存在: {station_code}")
                    return [], 0

                # 查詢總數
                count_query = """
                SELECT COUNT(*) as total
                FROM passenger_flow
                WHERE station_code = %s
                  AND date >= %s
                  AND date <= %s
                """

                count_result = self.db_manager.execute_query(
                    count_query, (station_code, start_date, end_date), fetch_one=True
                )
                total_count = int(count_result['total']) if count_result else 0

                if total_count == 0:
                    return [], 0

                # 查詢分頁資料
                data_query = """
                SELECT station_code, date, in_passengers, out_passengers
                FROM passenger_flow
                WHERE station_code = %s
                  AND date >= %s
                  AND date <= %s
                ORDER BY date
                LIMIT %s OFFSET %s
                """

                results = self.db_manager.execute_query(
                    data_query, (station_code, start_date, end_date, limit, offset)
                )

                flows = []
                if results:
                    for row in results:
                        try:
                            flow = create_passenger_flow_from_dict(dict(row))
                            flows.append(flow)
                        except Exception as e:
                            self.logger.warning(f"建立客流量物件失敗: {e}, 資料: {row}")
                            continue

                return flows, total_count

            except Exception as e:
                self.logger.error(f"分頁查詢客流量資料失敗: {e}")
                raise

        # 使用分頁管理器
        cache_key = f"passenger_flow_{station_code}_{start_date}_{end_date}"
        return self.pagination_manager.paginate_query(query_func, page, page_size, cache_key)

    def get_large_dataset_progressive(self, station_code: str, start_date: date, end_date: date,
                                    chunk_size: int = 1000, progress_callback: callable = None) -> List[PassengerFlow]:
        """
        漸進式載入大型資料集

        Args:
            station_code: 車站代碼
            start_date: 開始日期
            end_date: 結束日期
            chunk_size: 每次載入的資料量
            progress_callback: 進度回調函數

        Returns:
            List[PassengerFlow]: 完整的客流量資料列表
        """
        try:
            # 先取得總數
            count_query = """
            SELECT COUNT(*) as total
            FROM passenger_flow
            WHERE station_code = %s
              AND date >= %s
              AND date <= %s
            """

            count_result = self.db_manager.execute_query(
                count_query, (station_code, start_date, end_date), fetch_one=True
            )
            total_count = int(count_result['total']) if count_result else 0

            if total_count == 0:
                return []

            all_flows = []
            offset = 0

            while offset < total_count:
                # 查詢一個區塊的資料
                chunk_query = """
                SELECT station_code, date, in_passengers, out_passengers
                FROM passenger_flow
                WHERE station_code = %s
                  AND date >= %s
                  AND date <= %s
                ORDER BY date
                LIMIT %s OFFSET %s
                """

                results = self.db_manager.execute_query(
                    chunk_query, (station_code, start_date, end_date, chunk_size, offset)
                )

                if not results:
                    break

                # 處理這個區塊的資料
                chunk_flows = []
                for row in results:
                    try:
                        flow = create_passenger_flow_from_dict(dict(row))
                        chunk_flows.append(flow)
                    except Exception as e:
                        self.logger.warning(f"建立客流量物件失敗: {e}")
                        continue

                all_flows.extend(chunk_flows)
                offset += len(results)

                # 更新進度
                if progress_callback:
                    progress = min(100.0, (offset / total_count) * 100)
                    progress_callback(progress, f"已載入 {offset}/{total_count} 筆記錄")

                # 如果這個區塊的資料少於預期，表示已經到達結尾
                if len(results) < chunk_size:
                    break

            self.logger.info(f"漸進式載入完成: {len(all_flows)} 筆記錄")
            return all_flows

        except Exception as e:
            self.logger.error(f"漸進式載入失敗: {e}")
            raise

    def clear_cache(self, station_code: Optional[str] = None):
        """
        清除快取

        Args:
            station_code: 特定車站代碼，None 表示清除所有
        """
        if station_code:
            # 清除特定車站的快取
            cache_keys_to_clear = []
            for key in self.cache_manager.cache.keys():
                if f"passenger_flow_{station_code}" in key:
                    cache_keys_to_clear.append(key)

            for key in cache_keys_to_clear:
                self.cache_manager.remove(key)

            # 清除分頁快取
            pagination_keys_to_clear = []
            for key in self.pagination_manager.page_cache.keys():
                if f"passenger_flow_{station_code}" in key:
                    pagination_keys_to_clear.append(key)

            for key in pagination_keys_to_clear:
                self.pagination_manager.clear_cache(key)

            self.logger.info(f"已清除車站 {station_code} 的快取")
        else:
            # 清除所有快取
            self.cache_manager.clear()
            self.pagination_manager.clear_cache()
            self.logger.info("已清除所有客流量快取")

    def get_memory_usage_info(self) -> Dict[str, Any]:
        """取得記憶體使用資訊"""
        cache_stats = self.cache_manager.get_stats()
        pagination_stats = self.pagination_manager.get_stats()

        return {
            'cache_memory_mb': cache_stats['memory_usage_mb'],
            'cache_items': cache_stats['size'],
            'cache_hit_rate': cache_stats['hit_rate'],
            'pagination_cached_pages': pagination_stats['total_cached_pages'],
            'pagination_hit_rate': pagination_stats['cache_hit_rate']
        }


def create_passenger_flow_dao() -> PassengerFlowDAO:
    """建立客流量 DAO 實例"""
    return PassengerFlowDAO()