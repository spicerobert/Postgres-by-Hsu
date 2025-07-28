"""
DAO 層單元測試

測試資料庫存取物件的功能，使用模擬資料庫連線。
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
from taiwan_railway_gui.dao.database_manager import DatabaseManager, get_database_manager
from taiwan_railway_gui.dao.station_dao import StationDAO
from taiwan_railway_gui.dao.passenger_flow_dao import PassengerFlowDAO
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow, StationStatistics


class TestDatabaseManager(unittest.TestCase):
    """測試資料庫管理器"""

    def setUp(self):
        """設定測試環境"""
        # 重置單例
        DatabaseManager._instance = None

    @patch('taiwan_railway_gui.dao.database_manager.psycopg2')
    def test_singleton_pattern(self, mock_psycopg2):
        """測試單例模式"""
        # 模擬 psycopg2
        mock_psycopg2.pool.ThreadedConnectionPool.return_value = Mock()

        db1 = DatabaseManager()
        db2 = DatabaseManager()

        self.assertIs(db1, db2)

    @patch('taiwan_railway_gui.dao.database_manager.psycopg2')
    def test_connection_pool_initialization(self, mock_psycopg2):
        """測試連線池初始化"""
        # 模擬連線池
        mock_pool = Mock()
        mock_conn = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_psycopg2.pool.ThreadedConnectionPool.return_value = mock_pool

        db = DatabaseManager()
        result = db.initialize_connection_pool()

        self.assertTrue(result)
        self.assertTrue(db.is_connected)

    @patch('taiwan_railway_gui.dao.database_manager.psycopg2')
    def test_execute_query(self, mock_psycopg2):
        """測試查詢執行"""
        # 模擬資料庫連線和游標
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{'test': 1}]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_psycopg2.pool.ThreadedConnectionPool.return_value = mock_pool

        db = DatabaseManager()
        db.initialize_connection_pool()

        result = db.execute_query("SELECT 1 as test")

        self.assertEqual(result, [{'test': 1}])
        mock_cursor.execute.assert_called_once_with("SELECT 1 as test", None)

    @patch('taiwan_railway_gui.dao.database_manager.psycopg2')
    def test_execute_query_with_retry(self, mock_psycopg2):
        """測試查詢重試機制"""
        # 模擬第一次失敗，第二次成功
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.side_effect = [Exception("Connection failed"), [{'test': 1}]]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_psycopg2.pool.ThreadedConnectionPool.return_value = mock_pool

        db = DatabaseManager()
        db.initialize_connection_pool()
        db._retry_delay = 0.01  # 減少測試時間

        result = db.execute_query("SELECT 1 as test")

        self.assertEqual(result, [{'test': 1}])
        self.assertEqual(mock_cursor.execute.call_count, 2)


class TestStationDAO(unittest.TestCase):
    """測試車站 DAO"""

    def setUp(self):
        """設定測試環境"""
        self.station_dao = StationDAO()

        # 模擬資料庫管理器
        self.mock_db_manager = Mock()
        self.station_dao.db_manager = self.mock_db_manager

        # 測試資料
        self.sample_station_data = {
            'station_code': '1000',
            'station_name': '台北車站',
            'address': '台北市中正區北平西路3號',
            'phone': '02-2371-3558',
            'gps_lat': 25.0478,
            'gps_lng': 121.5170,
            'has_bike_rental': True
        }

    def test_get_station_by_code_success(self):
        """測試成功取得車站"""
        # 模擬資料庫回傳
        self.mock_db_manager.execute_query.return_value = self.sample_station_data

        station = self.station_dao.get_station_by_code('1000')

        self.assertIsInstance(station, Station)
        self.assertEqual(station.station_code, '1000')
        self.assertEqual(station.station_name, '台北車站')

    def test_get_station_by_code_not_found(self):
        """測試車站不存在"""
        # 模擬資料庫回傳空結果
        self.mock_db_manager.execute_query.return_value = None

        station = self.station_dao.get_station_by_code('9999')

        self.assertIsNone(station)

    def test_search_stations_by_name(self):
        """測試按名稱搜尋車站"""
        # 模擬資料庫回傳
        self.mock_db_manager.execute_query.return_value = [self.sample_station_data]

        stations = self.station_dao.search_stations('台北')

        self.assertEqual(len(stations), 1)
        self.assertIsInstance(stations[0], Station)
        self.assertEqual(stations[0].station_name, '台北車站')

    def test_search_stations_by_code(self):
        """測試按代碼搜尋車站"""
        # 模擬 get_station_by_code 的行為
        self.mock_db_manager.execute_query.return_value = self.sample_station_data

        stations = self.station_dao.search_stations('1000')

        self.assertEqual(len(stations), 1)
        self.assertEqual(stations[0].station_code, '1000')

    def test_get_all_stations(self):
        """測試取得所有車站"""
        # 模擬資料庫回傳多筆資料
        station_data_2 = self.sample_station_data.copy()
        station_data_2['station_code'] = '1001'
        station_data_2['station_name'] = '板橋車站'

        self.mock_db_manager.execute_query.return_value = [
            self.sample_station_data,
            station_data_2
        ]

        stations = self.station_dao.get_all_stations()

        self.assertEqual(len(stations), 2)
        self.assertEqual(stations[0].station_code, '1000')
        self.assertEqual(stations[1].station_code, '1001')

    def test_station_exists(self):
        """測試檢查車站存在"""
        # 模擬車站存在
        self.mock_db_manager.execute_query.return_value = {'exists': 1}

        exists = self.station_dao.station_exists('1000')
        self.assertTrue(exists)

        # 模擬車站不存在
        self.mock_db_manager.execute_query.return_value = None

        exists = self.station_dao.station_exists('9999')
        self.assertFalse(exists)

    def test_cache_functionality(self):
        """測試快取功能"""
        # 啟用快取
        self.station_dao.enable_cache(True)

        # 第一次查詢
        self.mock_db_manager.execute_query.return_value = self.sample_station_data
        station1 = self.station_dao.get_station_by_code('1000')

        # 第二次查詢應該從快取取得
        station2 = self.station_dao.get_station_by_code('1000')

        # 資料庫只應該被查詢一次
        self.assertEqual(self.mock_db_manager.execute_query.call_count, 1)
        self.assertIs(station1, station2)

        # 檢查快取大小
        self.assertEqual(self.station_dao.cache_size, 1)


class TestPassengerFlowDAO(unittest.TestCase):
    """測試客流量 DAO"""

    def setUp(self):
        """設定測試環境"""
        self.flow_dao = PassengerFlowDAO()

        # 模擬資料庫管理器
        self.mock_db_manager = Mock()
        self.flow_dao.db_manager = self.mock_db_manager

        # 模擬車站 DAO
        self.mock_station_dao = Mock()
        self.flow_dao.station_dao = self.mock_station_dao

        # 測試資料
        self.sample_flow_data = {
            'station_code': '1000',
            'date': date(2024, 1, 15),
            'in_passengers': 5000,
            'out_passengers': 4800
        }

        self.sample_station = Station(
            station_code='1000',
            station_name='台北車站',
            address='台北市中正區北平西路3號',
            phone='02-2371-3558',
            gps_lat=25.0478,
            gps_lng=121.5170,
            has_bike_rental=True
        )

    def test_get_passenger_flow_success(self):
        """測試成功取得客流量資料"""
        # 模擬車站存在
        self.mock_station_dao.station_exists.return_value = True

        # 模擬資料庫回傳
        self.mock_db_manager.execute_query.return_value = [self.sample_flow_data]

        flows = self.flow_dao.get_passenger_flow('1000', date(2024, 1, 1), date(2024, 1, 31))

        self.assertEqual(len(flows), 1)
        self.assertIsInstance(flows[0], PassengerFlow)
        self.assertEqual(flows[0].station_code, '1000')
        self.assertEqual(flows[0].in_passengers, 5000)

    def test_get_passenger_flow_station_not_exists(self):
        """測試車站不存在的情況"""
        # 模擬車站不存在
        self.mock_station_dao.station_exists.return_value = False

        flows = self.flow_dao.get_passenger_flow('9999', date(2024, 1, 1), date(2024, 1, 31))

        self.assertEqual(len(flows), 0)
        # 不應該查詢資料庫
        self.mock_db_manager.execute_query.assert_not_called()

    def test_get_station_statistics_success(self):
        """測試成功取得車站統計"""
        # 模擬車站存在
        self.mock_station_dao.get_station_by_code.return_value = self.sample_station

        # 模擬統計查詢結果
        stats_result = {
            'record_count': 30,
            'total_in': 150000,
            'total_out': 144000,
            'min_date': date(2024, 1, 1),
            'max_date': date(2024, 1, 30)
        }
        self.mock_db_manager.execute_query.return_value = stats_result

        statistics = self.flow_dao.get_station_statistics('1000', date(2024, 1, 1), date(2024, 1, 30))

        self.assertIsInstance(statistics, StationStatistics)
        self.assertEqual(statistics.station_code, '1000')
        self.assertEqual(statistics.station_name, '台北車站')
        self.assertEqual(statistics.total_in, 150000)
        self.assertEqual(statistics.total_out, 144000)
        self.assertEqual(statistics.total_passengers, 294000)
        self.assertEqual(statistics.average_daily, 9800.0)  # 294000 / 30

    def test_get_station_statistics_no_data(self):
        """測試沒有統計資料的情況"""
        # 模擬車站存在
        self.mock_station_dao.get_station_by_code.return_value = self.sample_station

        # 模擬沒有資料
        stats_result = {'record_count': 0}
        self.mock_db_manager.execute_query.return_value = stats_result

        statistics = self.flow_dao.get_station_statistics('1000', date(2024, 1, 1), date(2024, 1, 30))

        self.assertIsNone(statistics)

    def test_get_multiple_station_statistics(self):
        """測試取得多個車站統計"""
        # 模擬車站資料
        stations = [self.sample_station]
        self.mock_station_dao.get_stations_by_codes.return_value = stations

        # 模擬統計查詢結果
        stats_results = [{
            'station_code': '1000',
            'record_count': 30,
            'total_in': 150000,
            'total_out': 144000,
            'min_date': date(2024, 1, 1),
            'max_date': date(2024, 1, 30)
        }]
        self.mock_db_manager.execute_query.return_value = stats_results

        statistics_list = self.flow_dao.get_multiple_station_statistics(
            ['1000'], date(2024, 1, 1), date(2024, 1, 30)
        )

        self.assertEqual(len(statistics_list), 1)
        self.assertIsInstance(statistics_list[0], StationStatistics)
        self.assertEqual(statistics_list[0].station_code, '1000')

    def test_get_date_range_available(self):
        """測試取得可用日期範圍"""
        # 模擬資料庫回傳
        date_result = {
            'min_date': date(2024, 1, 1),
            'max_date': date(2024, 12, 31)
        }
        self.mock_db_manager.execute_query.return_value = date_result

        date_range = self.flow_dao.get_date_range_available('1000')

        self.assertIsNotNone(date_range)
        self.assertEqual(date_range[0], date(2024, 1, 1))
        self.assertEqual(date_range[1], date(2024, 12, 31))

    def test_get_date_range_available_no_data(self):
        """測試沒有資料的日期範圍"""
        # 模擬沒有資料
        self.mock_db_manager.execute_query.return_value = {'min_date': None, 'max_date': None}

        date_range = self.flow_dao.get_date_range_available('9999')

        self.assertIsNone(date_range)


if __name__ == '__main__':
    unittest.main()