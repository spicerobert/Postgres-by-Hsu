"""
資料庫整合測試

測試資料庫連線、DAO層與實際資料庫的整合。
"""

import unittest
import os
import sys
import tempfile
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional
from unittest.mock import Mock, patch, MagicMock

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from taiwan_railway_gui.dao.database_manager import DatabaseManager
from taiwan_railway_gui.dao.station_dao import StationDAO
from taiwan_railway_gui.dao.passenger_flow_dao import PassengerFlowDAO
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow
from taiwan_railway_gui.config import get_config


class DatabaseIntegrationTestCase(unittest.TestCase):
    """資料庫整合測試基礎類別"""

    @classmethod
    def setUpClass(cls):
        """設定測試類別"""
        cls.test_db_path = tempfile.mktemp(suffix='.db')
        cls.setup_test_database()

    @classmethod
    def tearDownClass(cls):
        """清理測試類別"""
        if os.path.exists(cls.test_db_path):
            os.unlink(cls.test_db_path)

    @classmethod
    def setup_test_database(cls):
        """建立測試資料庫和測試資料"""
        conn = sqlite3.connect(cls.test_db_path)
        cursor = conn.cursor()

        # 建立車站表格
        cursor.execute('''
            CREATE TABLE stations (
                station_id TEXT PRIMARY KEY,
                station_name TEXT NOT NULL,
                station_class TEXT,
                line_name TEXT,
                address TEXT,
                phone TEXT,
                coordinates TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')

        # 建立乘客流量表格
        cursor.execute('''
            CREATE TABLE passenger_flow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id TEXT,
                date TEXT,
                inbound_passengers INTEGER,
                outbound_passengers INTEGER,
                total_passengers INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (station_id) REFERENCES stations (station_id)
            )
        ''')

        # 插入測試車站資料
        test_stations = [
            ('1000', '台北', '特等', '縱貫線', '台北市中正區黎明里北平西路3號', '02-23713558', '25.047924,121.517081'),
            ('1001', '板橋', '一等', '縱貫線', '新北市板橋區縣民大道二段7號', '02-29603000', '25.013807,121.464132'),
            ('1008', '桃園', '一等', '縱貫線', '桃園市桃園區中正路1號', '03-3322340', '24.989197,121.314007'),
            ('1025', '新竹', '一等', '縱貫線', '新竹市東區榮光里中華路二段445號', '03-5323441', '24.801416,120.971736'),
            ('1100', '台中', '特等', '縱貫線', '台中市中區台灣大道一段1號', '04-22227236', '24.136675,120.684175'),
        ]

        cursor.executemany(
            'INSERT INTO stations VALUES (?, ?, ?, ?, ?, ?, ?, 1)',
            test_stations
        )

        # 插入測試乘客流量資料
        base_date = datetime.now() - timedelta(days=30)
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')

            for station_id, _, _, _, _, _, _ in test_stations:
                inbound = 1000 + (i * 50) + int(station_id) % 100
                outbound = 950 + (i * 45) + int(station_id) % 90
                total = inbound + outbound

                cursor.execute(
                    'INSERT INTO passenger_flow (station_id, date, inbound_passengers, outbound_passengers, total_passengers) VALUES (?, ?, ?, ?, ?)',
                    (station_id, date_str, inbound, outbound, total)
                )

        conn.commit()
        conn.close()

    def setUp(self):
        """設定測試方法"""
        # 重設資料庫管理器
        DatabaseManager._instance = None

        # 模擬配置檔設定
        with patch('taiwan_railway_gui.config.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': '5432',
                'database': 'test_db',
                'user': 'test_user',
                'password': 'test_pass'
            }

            # 模擬 psycopg2 以使用 SQLite 測試資料庫
            with patch('taiwan_railway_gui.dao.database_manager.psycopg2') as mock_psycopg2:
                # 建立模擬的連線池
                mock_pool = Mock()
                mock_psycopg2.pool.ThreadedConnectionPool.return_value = mock_pool

                # 建立真實的 SQLite 連線
                import sqlite3
                sqlite_conn = sqlite3.connect(self.test_db_path)
                sqlite_conn.row_factory = sqlite3.Row  # 模擬 RealDictCursor

                mock_pool.getconn.return_value = sqlite_conn
                mock_pool.putconn.return_value = None

                # 建立DatabaseManager實例
                self.db_manager = DatabaseManager()
                self.db_manager._connection_pool = mock_pool
                self.db_manager._is_connected = True

        # 建立DAO實例（這些會使用模擬的資料庫管理器）
        with patch('taiwan_railway_gui.dao.get_database_manager', return_value=self.db_manager):
            self.station_dao = StationDAO()
            self.passenger_flow_dao = PassengerFlowDAO()

    def tearDown(self):
        """清理測試方法"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close_connection()
        DatabaseManager._instance = None


class TestStationDAOIntegration(DatabaseIntegrationTestCase):
    """車站DAO整合測試"""

    def test_get_all_stations(self):
        """測試取得所有車站"""
        stations = self.station_dao.get_all_stations()

        self.assertIsInstance(stations, list)
        self.assertEqual(len(stations), 5)

        # 檢查第一個車站
        first_station = stations[0]
        self.assertIsInstance(first_station, Station)
        self.assertEqual(first_station.station_id, '1000')
        self.assertEqual(first_station.station_name, '台北')

    def test_search_stations_by_name(self):
        """測試按名稱搜尋車站"""
        # 測試精確搜尋
        stations = self.station_dao.search_stations_by_name('台北')
        self.assertEqual(len(stations), 1)
        self.assertEqual(stations[0].station_name, '台北')

        # 測試模糊搜尋
        stations = self.station_dao.search_stations_by_name('台')
        self.assertGreaterEqual(len(stations), 2)  # 台北、台中

        # 測試找不到的情況
        stations = self.station_dao.search_stations_by_name('不存在的車站')
        self.assertEqual(len(stations), 0)

    def test_get_station_by_id(self):
        """測試根據ID取得車站"""
        # 測試存在的車站
        station = self.station_dao.get_station_by_id('1000')
        self.assertIsNotNone(station)
        self.assertEqual(station.station_name, '台北')

        # 測試不存在的車站
        station = self.station_dao.get_station_by_id('9999')
        self.assertIsNone(station)

    def test_search_stations_by_line(self):
        """測試按路線搜尋車站"""
        stations = self.station_dao.search_stations_by_line('縱貫線')
        self.assertEqual(len(stations), 5)

        # 測試不存在的路線
        stations = self.station_dao.search_stations_by_line('不存在的路線')
        self.assertEqual(len(stations), 0)


class TestPassengerFlowDAOIntegration(DatabaseIntegrationTestCase):
    """乘客流量DAO整合測試"""

    def test_get_passenger_flow_by_station_and_date_range(self):
        """測試按車站和日期範圍取得乘客流量"""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now() - timedelta(days=1)

        flows = self.passenger_flow_dao.get_passenger_flow_by_station_and_date_range(
            '1000', start_date, end_date
        )

        self.assertIsInstance(flows, list)
        self.assertGreater(len(flows), 0)

        # 檢查第一筆資料
        first_flow = flows[0]
        self.assertIsInstance(first_flow, PassengerFlow)
        self.assertEqual(first_flow.station_id, '1000')
        self.assertIsInstance(first_flow.inbound_passengers, int)
        self.assertIsInstance(first_flow.outbound_passengers, int)

    def test_get_passenger_flow_summary(self):
        """測試取得乘客流量摘要"""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now() - timedelta(days=1)

        summary = self.passenger_flow_dao.get_passenger_flow_summary(
            '1000', start_date, end_date
        )

        self.assertIsInstance(summary, dict)
        self.assertIn('total_inbound', summary)
        self.assertIn('total_outbound', summary)
        self.assertIn('daily_average_inbound', summary)
        self.assertIn('daily_average_outbound', summary)

        # 檢查數值類型
        self.assertIsInstance(summary['total_inbound'], (int, float))
        self.assertIsInstance(summary['total_outbound'], (int, float))

    def test_get_top_stations_by_passenger_count(self):
        """測試取得客流量最高的車站"""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now() - timedelta(days=1)

        top_stations = self.passenger_flow_dao.get_top_stations_by_passenger_count(
            start_date, end_date, limit=3
        )

        self.assertIsInstance(top_stations, list)
        self.assertLessEqual(len(top_stations), 3)

        if top_stations:
            # 檢查排序（應該是遞減）
            for i in range(len(top_stations) - 1):
                current_total = top_stations[i].get('total_passengers', 0)
                next_total = top_stations[i + 1].get('total_passengers', 0)
                self.assertGreaterEqual(current_total, next_total)

    def test_compare_stations_passenger_flow(self):
        """測試比較多個車站的客流量"""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now() - timedelta(days=1)
        station_ids = ['1000', '1001', '1008']

        comparison = self.passenger_flow_dao.compare_stations_passenger_flow(
            station_ids, start_date, end_date
        )

        self.assertIsInstance(comparison, list)
        self.assertEqual(len(comparison), 3)

        # 檢查每個車站的資料
        for station_data in comparison:
            self.assertIn('station_id', station_data)
            self.assertIn('station_name', station_data)
            self.assertIn('total_passengers', station_data)
            self.assertIn(station_data['station_id'], station_ids)


class TestDatabaseConnectionIntegration(DatabaseIntegrationTestCase):
    """資料庫連線整合測試"""

    def test_database_connection_singleton(self):
        """測試資料庫連線單例模式"""
        db1 = DatabaseManager(self.test_config)
        db2 = DatabaseManager(self.test_config)

        # 應該是同一個實例
        self.assertIs(db1, db2)

    def test_database_connection_retry(self):
        """測試資料庫連線重試機制"""
        # 使用無效的資料庫配置
        invalid_config = {
            'database_type': 'sqlite',
            'database_path': '/invalid/path/database.db',
        }

        # 重設單例
        DatabaseManager._instance = None

        with self.assertRaises(Exception):
            db_manager = DatabaseManager(invalid_config)
            db_manager.get_connection()

    def test_transaction_handling(self):
        """測試交易處理"""
        connection = self.db_manager.get_connection()
        cursor = connection.cursor()

        try:
            # 開始交易
            cursor.execute('BEGIN TRANSACTION')

            # 插入測試資料
            cursor.execute(
                'INSERT INTO stations VALUES (?, ?, ?, ?, ?, ?, ?, 1)',
                ('9999', '測試車站', '測試等級', '測試路線', '測試地址', '測試電話', '測試座標')
            )

            # 檢查資料是否存在（在交易中）
            cursor.execute('SELECT COUNT(*) FROM stations WHERE station_id = ?', ('9999',))
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)

            # 回滾交易
            cursor.execute('ROLLBACK')

            # 檢查資料是否被回滾
            cursor.execute('SELECT COUNT(*) FROM stations WHERE station_id = ?', ('9999',))
            count = cursor.fetchone()[0]
            self.assertEqual(count, 0)

        finally:
            cursor.close()


if __name__ == '__main__':
    # 建立測試套件
    suite = unittest.TestSuite()

    # 添加資料庫整合測試
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStationDAOIntegration))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPassengerFlowDAOIntegration))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDatabaseConnectionIntegration))

    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 輸出結果
    if result.wasSuccessful():
        print("\n✅ 所有資料庫整合測試通過！")
    else:
        print(f"\n❌ 測試失敗：{len(result.failures)} 個失敗，{len(result.errors)} 個錯誤")

    sys.exit(0 if result.wasSuccessful() else 1)
