"""
車站資料存取物件

處理車站相關的資料庫操作，包括搜尋、查詢和快取功能。
"""

import logging
from typing import List, Optional, Dict, Any
from taiwan_railway_gui.interfaces import StationDAOInterface
from taiwan_railway_gui.models.station import Station, create_station_from_dict
from taiwan_railway_gui.dao.database_manager import get_database_manager
from taiwan_railway_gui.config import get_config


class StationDAO(StationDAOInterface):
    """
    車站資料存取物件實作

    提供車站資料的查詢、搜尋和快取功能。
    """

    def __init__(self):
        """初始化 DAO"""
        self.logger = logging.getLogger(__name__)
        self.db_manager = get_database_manager()
        self._station_cache = {}  # 簡單的記憶體快取
        self._cache_enabled = True

        # 錯誤訊息
        self.error_messages = get_config('errors')

    def search_stations(self, query: str) -> List[Station]:
        """
        搜尋車站

        Args:
            query: 搜尋查詢（車站名稱或代碼）

        Returns:
            List[Station]: 匹配的車站列表
        """
        try:
            if not query:
                # 空查詢回傳所有車站（限制數量）
                return self.get_all_stations()[:50]

            query = query.strip()

            # 檢查是否為車站代碼（純數字）
            if query.isdigit():
                station = self.get_station_by_code(query)
                return [station] if station else []

            # 車站名稱搜尋
            sql_query = """
            SELECT station_code, station_name, address, phone,
                   gps_lat, gps_lng, has_bike_rental
            FROM stations
            WHERE station_name ILIKE %s
               OR station_name ILIKE %s
            ORDER BY
                CASE
                    WHEN station_name = %s THEN 1
                    WHEN station_name ILIKE %s THEN 2
                    ELSE 3
                END,
                station_name
            LIMIT 20
            """

            # 準備搜尋參數
            exact_match = query
            starts_with = f"{query}%"
            contains = f"%{query}%"

            params = (starts_with, contains, exact_match, starts_with)

            results = self.db_manager.execute_query(sql_query, params)

            if not results:
                self.logger.info(f"搜尋查詢 '{query}' 沒有找到結果")
                return []

            stations = []
            for row in results:
                try:
                    station = create_station_from_dict(dict(row))
                    stations.append(station)

                    # 加入快取
                    if self._cache_enabled:
                        self._station_cache[station.station_code] = station

                except Exception as e:
                    self.logger.warning(f"建立車站物件失敗: {e}, 資料: {row}")
                    continue

            self.logger.info(f"搜尋查詢 '{query}' 找到 {len(stations)} 個結果")
            return stations

        except Exception as e:
            self.logger.error(f"搜尋車站失敗: {e}")
            return []

    def get_station_by_code(self, code: str) -> Optional[Station]:
        """
        根據代碼取得車站

        Args:
            code: 車站代碼

        Returns:
            Optional[Station]: 車站物件或 None
        """
        try:
            # 檢查快取
            if self._cache_enabled and code in self._station_cache:
                self.logger.debug(f"從快取取得車站: {code}")
                return self._station_cache[code]

            sql_query = """
            SELECT station_code, station_name, address, phone,
                   gps_lat, gps_lng, has_bike_rental
            FROM stations
            WHERE station_code = %s
            """

            result = self.db_manager.execute_query(sql_query, (code,), fetch_one=True)

            if not result:
                self.logger.info(f"找不到車站代碼: {code}")
                return None

            station = create_station_from_dict(dict(result))

            # 加入快取
            if self._cache_enabled:
                self._station_cache[code] = station

            self.logger.debug(f"取得車站: {station.station_name} ({code})")
            return station

        except Exception as e:
            self.logger.error(f"取得車站失敗 (代碼: {code}): {e}")
            return None

    def get_all_stations(self) -> List[Station]:
        """
        取得所有車站

        Returns:
            List[Station]: 所有車站列表
        """
        try:
            sql_query = """
            SELECT station_code, station_name, address, phone,
                   gps_lat, gps_lng, has_bike_rental
            FROM stations
            ORDER BY station_code
            """

            results = self.db_manager.execute_query(sql_query)

            if not results:
                self.logger.warning("資料庫中沒有車站資料")
                return []

            stations = []
            for row in results:
                try:
                    station = create_station_from_dict(dict(row))
                    stations.append(station)

                    # 加入快取
                    if self._cache_enabled:
                        self._station_cache[station.station_code] = station

                except Exception as e:
                    self.logger.warning(f"建立車站物件失敗: {e}, 資料: {row}")
                    continue

            self.logger.info(f"取得 {len(stations)} 個車站")
            return stations

        except Exception as e:
            self.logger.error(f"取得所有車站失敗: {e}")
            return []

    def get_stations_by_codes(self, codes: List[str]) -> List[Station]:
        """
        根據代碼列表取得多個車站

        Args:
            codes: 車站代碼列表

        Returns:
            List[Station]: 車站列表
        """
        if not codes:
            return []

        try:
            # 先從快取取得
            stations = []
            missing_codes = []

            if self._cache_enabled:
                for code in codes:
                    if code in self._station_cache:
                        stations.append(self._station_cache[code])
                    else:
                        missing_codes.append(code)
            else:
                missing_codes = codes

            # 查詢缺少的車站
            if missing_codes:
                placeholders = ','.join(['%s'] * len(missing_codes))
                sql_query = f"""
                SELECT station_code, station_name, address, phone,
                       gps_lat, gps_lng, has_bike_rental
                FROM stations
                WHERE station_code IN ({placeholders})
                ORDER BY station_code
                """

                results = self.db_manager.execute_query(sql_query, tuple(missing_codes))

                if results:
                    for row in results:
                        try:
                            station = create_station_from_dict(dict(row))
                            stations.append(station)

                            # 加入快取
                            if self._cache_enabled:
                                self._station_cache[station.station_code] = station

                        except Exception as e:
                            self.logger.warning(f"建立車站物件失敗: {e}")
                            continue

            # 按原始順序排序
            station_dict = {s.station_code: s for s in stations}
            ordered_stations = [station_dict[code] for code in codes if code in station_dict]

            self.logger.info(f"取得 {len(ordered_stations)}/{len(codes)} 個車站")
            return ordered_stations

        except Exception as e:
            self.logger.error(f"取得多個車站失敗: {e}")
            return []

    def station_exists(self, code: str) -> bool:
        """
        檢查車站是否存在

        Args:
            code: 車站代碼

        Returns:
            bool: 車站是否存在
        """
        try:
            # 檢查快取
            if self._cache_enabled and code in self._station_cache:
                return True

            sql_query = "SELECT 1 FROM stations WHERE station_code = %s"
            result = self.db_manager.execute_query(sql_query, (code,), fetch_one=True)

            exists = result is not None
            self.logger.debug(f"車站 {code} 存在: {exists}")
            return exists

        except Exception as e:
            self.logger.error(f"檢查車站存在失敗: {e}")
            return False

    def get_stations_with_bike_rental(self) -> List[Station]:
        """
        取得有自行車租借服務的車站

        Returns:
            List[Station]: 有自行車租借的車站列表
        """
        try:
            sql_query = """
            SELECT station_code, station_name, address, phone,
                   gps_lat, gps_lng, has_bike_rental
            FROM stations
            WHERE has_bike_rental = true
            ORDER BY station_name
            """

            results = self.db_manager.execute_query(sql_query)

            if not results:
                return []

            stations = []
            for row in results:
                try:
                    station = create_station_from_dict(dict(row))
                    stations.append(station)
                except Exception as e:
                    self.logger.warning(f"建立車站物件失敗: {e}")
                    continue

            self.logger.info(f"找到 {len(stations)} 個有自行車租借的車站")
            return stations

        except Exception as e:
            self.logger.error(f"取得自行車租借車站失敗: {e}")
            return []

    def clear_cache(self):
        """清除快取"""
        self._station_cache.clear()
        self.logger.info("車站快取已清除")

    def enable_cache(self, enabled: bool = True):
        """
        啟用或停用快取

        Args:
            enabled: 是否啟用快取
        """
        self._cache_enabled = enabled
        if not enabled:
            self.clear_cache()
        self.logger.info(f"車站快取已{'啟用' if enabled else '停用'}")

    @property
    def cache_size(self) -> int:
        """取得快取大小"""
        return len(self._station_cache)


def create_station_dao() -> StationDAO:
    """建立車站 DAO 實例"""
    return StationDAO()