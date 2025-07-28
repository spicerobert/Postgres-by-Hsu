# -*- coding: utf-8 -*-
"""
綜合整合測試

實作完整的整合測試，包含資料庫整合、GUI元件互動、端到端工作流程、錯誤條件和效能測試。
"""

import unittest
import os
import sys
import tempfile
import sqlite3
import time
import threading
from datetime import datetime, timedelta, date
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow, StationStatistics


class IntegrationTestBase(unittest.TestCase):
    """整合測試基礎類別"""

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
                station_code TEXT PRIMARY KEY,
                station_name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                gps_lat REAL,
                gps_lng REAL,
                has_bike_rental BOOLEAN DEFAULT 0
            )
        ''')

        # 建立乘客流量表格
        cursor.execute('''
            CREATE TABLE passenger_flow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_code TEXT,
                date TEXT,
                in_passengers INTEGER,
                out_passengers INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (station_code) REFERENCES stations (station_code)
            )
        ''')

        # 插入測試車站資料
        test_stations = [
            ('1000', '台北', '台北市中正區黎明里北平西路3號', '02-23713558', 25.047924, 121.517081, 1),
            ('1001', '板橋', '新北市板橋區縣民大道二段7號', '02-29603000', 25.013807, 121.464132, 1),
            ('1008', '桃園', '桃園市桃園區中正路1號', '03-3322340', 24.989197, 121.314007, 0),
            ('1025', '新竹', '新竹市東區榮光里中華路二段445號', '03-5323441', 24.801416, 120.971736, 1),
            ('1100', '台中', '台中市中區台灣大道一段1號', '04-22227236', 24.136675, 120.684175, 1),
        ]

        cursor.executemany(
            'INSERT INTO stations VALUES (?, ?, ?, ?, ?, ?, ?)',
            test_stations
        )

        # 插入測試乘客流量資料
        base_date = datetime.now() - timedelta(days=30)
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')

            for station_code, _, _, _, _, _, _ in test_stations:
                in_passengers = 1000 + (i * 50) + int(station_code) % 100
                out_passengers = 950 + (i * 45) + int(station_code) % 90

                cursor.execute(
                    'INSERT INTO passenger_flow (station_code, date, in_passengers, out_passengers) VALUES (?, ?, ?, ?)',
                    (station_code, date_str, in_passengers, out_passengers)
                )

        conn.commit()
        conn.close()

    def setUp(self):
        """設定測試方法"""
        # 建立SQLite連線
        self.conn = sqlite3.connect(self.test_db_path)
        self.conn.row_factory = sqlite3.Row

    def tearDown(self):
        """清理測試方法"""
        if hasattr(self, 'conn'):
            self.conn.close()


class TestDatabaseIntegration(IntegrationTestBase):
    """資料庫整合測試"""

    def test_database_connection_and_query(self):
        """測試資料庫連線和基本查詢"""
        cursor = self.conn.cursor()

        # 測試車站查詢
        cursor.execute('SELECT COUNT(*) as count FROM stations')
        result = cursor.fetchone()
        self.assertEqual(result['count'], 5)

        # 測試客流量查詢
        cursor.execute('SELECT COUNT(*) as count FROM passenger_flow')
        result = cursor.fetchone()
        self.assertEqual(result['count'], 150)  # 5 stations * 30 days

    def test_station_data_integrity(self):
        """測試車站資料完整性"""
        cursor = self.conn.cursor()

        # 測試車站資料完整性
        cursor.execute('''
            SELECT station_code, station_name, gps_lat, gps_lng
            FROM stations
            WHERE station_code = ?
        ''', ('1000',))

        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result['station_name'], '台北')
        self.assertIsInstance(result['gps_lat'], float)
        self.assertIsInstance(result['gps_lng'], float)

    def test_passenger_flow_data_integrity(self):
        """測試客流量資料完整性"""
        cursor = self.conn.cursor()

        # 測試客流量資料完整性
        cursor.execute('''
            SELECT station_code, date, in_passengers, out_passengers
            FROM passenger_flow
            WHERE station_code = ?
            ORDER BY date
            LIMIT 1
        ''', ('1000',))

        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result['station_code'], '1000')
        self.assertIsInstance(result['in_passengers'], int)
        self.assertIsInstance(result['out_passengers'], int)
        self.assertGreater(result['in_passengers'], 0)
        self.assertGreater(result['out_passengers'], 0)

    def test_foreign_key_relationships(self):
        """測試外鍵關聯"""
        cursor = self.conn.cursor()

        # 測試車站和客流量的關聯
        cursor.execute('''
            SELECT s.station_name, COUNT(pf.id) as flow_count
            FROM stations s
            LEFT JOIN passenger_flow pf ON s.station_code = pf.station_code
            GROUP BY s.station_code, s.station_name
            ORDER BY s.station_code
        ''')

        results = cursor.fetchall()
        self.assertEqual(len(results), 5)

        for result in results:
            self.assertEqual(result['flow_count'], 30)  # 每個車站30天的資料


class TestModelIntegration(IntegrationTestBase):
    """模型整合測試"""

    def test_station_model_creation(self):
        """測試車站模型建立"""
        station = Station(
            station_code='1000',
            station_name='台北',
            address='台北市中正區',
            phone='02-23713558',
            gps_lat=25.047924,
            gps_lng=121.517081,
            has_bike_rental=True
        )

        self.assertEqual(station.station_code, '1000')
        self.assertEqual(station.station_name, '台北')
        self.assertEqual(station.coordinates, (25.047924, 121.517081))
        self.assertTrue(station.has_bike_rental)

    def test_passenger_flow_model_creation(self):
        """測試客流量模型建立"""
        flow = PassengerFlow(
            station_code='1000',
            date=date.today(),
            in_passengers=1500,
            out_passengers=1400
        )

        self.assertEqual(flow.station_code, '1000')
        self.assertEqual(flow.in_passengers, 1500)
        self.assertEqual(flow.out_passengers, 1400)
        self.assertEqual(flow.total_passengers, 2900)

    def test_station_statistics_model(self):
        """測試車站統計模型"""
        stats = StationStatistics(
            station_code='1000',
            station_name='台北',
            total_in=45000,
            total_out=43000,
            total_passengers=88000,
            average_daily=2933.33,
            date_range=(date(2024, 1, 1), date(2024, 1, 30))
        )

        self.assertEqual(stats.station_code, '1000')
        self.assertEqual(stats.total_passengers, 88000)
        self.assertEqual(stats.average_daily, 2933.33)


class TestComponentInteraction(IntegrationTestBase):
    """元件互動測試"""

    def test_dao_model_integration(self):
        """測試DAO和模型的整合"""
        # 模擬DAO查詢結果
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT station_code, station_name, address, phone, gps_lat, gps_lng, has_bike_rental
            FROM stations
            WHERE station_code = ?
        ''', ('1000',))

        result = cursor.fetchone()
        self.assertIsNotNone(result)

        # 建立Station模型
        station = Station(
            station_code=result['station_code'],
            station_name=result['station_name'],
            address=result['address'],
            phone=result['phone'],
            gps_lat=result['gps_lat'],
            gps_lng=result['gps_lng'],
            has_bike_rental=bool(result['has_bike_rental'])
        )

        self.assertEqual(station.station_code, '1000')
        self.assertEqual(station.station_name, '台北')

    def test_service_layer_integration(self):
        """測試服務層整合"""
        # 模擬服務層處理
        cursor = self.conn.cursor()

        # 查詢車站列表
        cursor.execute('SELECT station_code, station_name FROM stations ORDER BY station_code')
        stations_data = cursor.fetchall()

        # 轉換為模型
        stations = []
        for row in stations_data:
            # 取得完整車站資訊
            cursor.execute('''
                SELECT station_code, station_name, address, phone, gps_lat, gps_lng, has_bike_rental
                FROM stations WHERE station_code = ?
            ''', (row['station_code'],))

            station_detail = cursor.fetchone()
            station = Station(
                station_code=station_detail['station_code'],
                station_name=station_detail['station_name'],
                address=station_detail['address'],
                phone=station_detail['phone'],
                gps_lat=station_detail['gps_lat'],
                gps_lng=station_detail['gps_lng'],
                has_bike_rental=bool(station_detail['has_bike_rental'])
            )
            stations.append(station)

        self.assertEqual(len(stations), 5)
        self.assertIsInstance(stations[0], Station)


class TestEndToEndWorkflows(IntegrationTestBase):
    """端到端工作流程測試"""

    def test_station_search_workflow(self):
        """測試車站搜尋工作流程"""
        cursor = self.conn.cursor()

        # 1. 模擬使用者搜尋
        search_term = '台北'

        # 2. 執行搜尋查詢
        cursor.execute('''
            SELECT station_code, station_name, address, phone, gps_lat, gps_lng, has_bike_rental
            FROM stations
            WHERE station_name LIKE ?
            ORDER BY station_name
        ''', (f'%{search_term}%',))

        results = cursor.fetchall()

        # 3. 建立結果模型
        stations = []
        for row in results:
            station = Station(
                station_code=row['station_code'],
                station_name=row['station_name'],
                address=row['address'],
                phone=row['phone'],
                gps_lat=row['gps_lat'],
                gps_lng=row['gps_lng'],
                has_bike_rental=bool(row['has_bike_rental'])
            )
            stations.append(station)

        # 4. 驗證搜尋結果
        self.assertGreater(len(stations), 0)
        self.assertTrue(any(search_term in station.station_name for station in stations))

    def test_passenger_flow_query_workflow(self):
        """測試客流量查詢工作流程"""
        cursor = self.conn.cursor()

        # 1. 模擬使用者選擇參數
        station_code = '1000'
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        # 2. 驗證車站存在
        cursor.execute('SELECT COUNT(*) as count FROM stations WHERE station_code = ?', (station_code,))
        station_exists = cursor.fetchone()['count'] > 0
        self.assertTrue(station_exists)

        # 3. 查詢客流量資料
        cursor.execute('''
            SELECT station_code, date, in_passengers, out_passengers
            FROM passenger_flow
            WHERE station_code = ? AND date >= ? AND date <= ?
            ORDER BY date
        ''', (station_code, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

        flow_data = cursor.fetchall()

        # 4. 計算統計資料
        total_in = sum(row['in_passengers'] for row in flow_data)
        total_out = sum(row['out_passengers'] for row in flow_data)
        total_passengers = total_in + total_out

        # 5. 驗證結果
        self.assertGreater(len(flow_data), 0)
        self.assertGreater(total_passengers, 0)


class TestErrorConditions(IntegrationTestBase):
    """錯誤條件測試"""

    def test_invalid_station_code_handling(self):
        """測試無效車站代碼處理"""
        cursor = self.conn.cursor()

        # 查詢不存在的車站
        cursor.execute('SELECT COUNT(*) as count FROM stations WHERE station_code = ?', ('9999',))
        result = cursor.fetchone()

        # 應該找不到資料
        self.assertEqual(result['count'], 0)

    def test_invalid_date_range_handling(self):
        """測試無效日期範圍處理"""
        cursor = self.conn.cursor()

        # 測試未來日期範圍（應該沒有資料）
        future_start = datetime.now() + timedelta(days=30)
        future_end = datetime.now() + timedelta(days=60)

        cursor.execute('''
            SELECT COUNT(*) as count
            FROM passenger_flow
            WHERE date >= ? AND date <= ?
        ''', (future_start.strftime('%Y-%m-%d'), future_end.strftime('%Y-%m-%d')))

        result = cursor.fetchone()
        self.assertEqual(result['count'], 0)

    def test_empty_search_results_handling(self):
        """測試空搜尋結果處理"""
        cursor = self.conn.cursor()

        # 搜尋不存在的車站名稱
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM stations
            WHERE station_name LIKE ?
        ''', ('%不存在的車站%',))

        result = cursor.fetchone()
        self.assertEqual(result['count'], 0)


class TestPerformanceAndLargeDataset(IntegrationTestBase):
    """效能和大型資料集測試"""

    def test_large_dataset_query_performance(self):
        """測試大型資料集查詢效能"""
        cursor = self.conn.cursor()

        # 測試查詢所有資料的效能
        start_time = time.time()

        cursor.execute('''
            SELECT pf.station_code, s.station_name, pf.date, pf.in_passengers, pf.out_passengers
            FROM passenger_flow pf
            JOIN stations s ON pf.station_code = s.station_code
            ORDER BY pf.date, pf.station_code
        ''')

        results = cursor.fetchall()
        end_time = time.time()

        query_time = end_time - start_time

        # 驗證查詢結果和效能
        self.assertEqual(len(results), 150)  # 5 stations * 30 days
        self.assertLess(query_time, 1.0)  # 查詢時間應該少於1秒

    def test_aggregation_query_performance(self):
        """測試聚合查詢效能"""
        cursor = self.conn.cursor()

        start_time = time.time()

        cursor.execute('''
            SELECT
                s.station_name,
                COUNT(pf.id) as record_count,
                SUM(pf.in_passengers) as total_in,
                SUM(pf.out_passengers) as total_out,
                AVG(pf.in_passengers + pf.out_passengers) as avg_total
            FROM stations s
            LEFT JOIN passenger_flow pf ON s.station_code = pf.station_code
            GROUP BY s.station_code, s.station_name
            ORDER BY total_in DESC
        ''')

        results = cursor.fetchall()
        end_time = time.time()

        query_time = end_time - start_time

        # 驗證聚合結果和效能
        self.assertEqual(len(results), 5)
        self.assertLess(query_time, 0.5)  # 聚合查詢應該很快

        # 檢查聚合結果正確性
        for result in results:
            self.assertEqual(result['record_count'], 30)
            self.assertGreater(result['total_in'], 0)
            self.assertGreater(result['total_out'], 0)

    def test_pagination_simulation(self):
        """測試分頁模擬"""
        cursor = self.conn.cursor()

        page_size = 10
        page = 1
        offset = (page - 1) * page_size

        # 查詢總數
        cursor.execute('SELECT COUNT(*) as total FROM passenger_flow')
        total_count = cursor.fetchone()['total']

        # 查詢分頁資料
        cursor.execute('''
            SELECT station_code, date, in_passengers, out_passengers
            FROM passenger_flow
            ORDER BY date, station_code
            LIMIT ? OFFSET ?
        ''', (page_size, offset))

        page_results = cursor.fetchall()

        # 驗證分頁結果
        self.assertEqual(len(page_results), page_size)
        self.assertEqual(total_count, 150)

        # 計算總頁數
        total_pages = (total_count + page_size - 1) // page_size
        self.assertEqual(total_pages, 15)  # 150 / 10 = 15 頁


if __name__ == '__main__':
    # 建立測試套件
    suite = unittest.TestSuite()

    # 添加所有測試類別
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDatabaseIntegration))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestModelIntegration))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestComponentInteraction))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEndToEndWorkflows))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestErrorConditions))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPerformanceAndLargeDataset))

    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 輸出結果
    if result.wasSuccessful():
        print("\n✅ 所有綜合整合測試通過！")
    else:
        print(f"\n❌ 測試失敗：{len(result.failures)} 個失敗，{len(result.errors)} 個錯誤")

    sys.exit(0 if result.wasSuccessful() else 1)