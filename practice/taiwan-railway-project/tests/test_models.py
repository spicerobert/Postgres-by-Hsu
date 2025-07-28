"""
資料模型單元測試

測試 Station 和 PassengerFlow 資料模型的功能和驗證邏輯。
"""

import unittest
from datetime import date, datetime
from taiwan_railway_gui.models.station import Station, create_station_from_dict
from taiwan_railway_gui.models.passenger_flow import (
    PassengerFlow, StationStatistics, ComparisonResult,
    create_passenger_flow_from_dict, calculate_statistics
)


class TestStation(unittest.TestCase):
    """測試 Station 模型"""

    def setUp(self):
        """設定測試資料"""
        self.valid_station_data = {
            'station_code': '1000',
            'station_name': '台北車站',
            'address': '台北市中正區北平西路3號',
            'phone': '02-2371-3558',
            'gps_lat': 25.0478,
            'gps_lng': 121.5170,
            'has_bike_rental': True
        }

    def test_valid_station_creation(self):
        """測試有效車站建立"""
        station = Station(**self.valid_station_data)

        self.assertEqual(station.station_code, '1000')
        self.assertEqual(station.station_name, '台北車站')
        self.assertEqual(station.address, '台北市中正區北平西路3號')
        self.assertEqual(station.phone, '02-2371-3558')
        self.assertEqual(station.gps_lat, 25.0478)
        self.assertEqual(station.gps_lng, 121.5170)
        self.assertTrue(station.has_bike_rental)

    def test_invalid_station_code(self):
        """測試無效車站代碼"""
        # 空字串
        with self.assertRaises(ValueError):
            data = self.valid_station_data.copy()
            data['station_code'] = ''
            Station(**data)

        # 非數字格式
        with self.assertRaises(ValueError):
            data = self.valid_station_data.copy()
            data['station_code'] = 'ABC'
            Station(**data)

    def test_invalid_coordinates(self):
        """測試無效座標"""
        # 緯度超出範圍
        with self.assertRaises(ValueError):
            data = self.valid_station_data.copy()
            data['gps_lat'] = 30.0  # 超出台灣範圍
            Station(**data)

        # 經度超出範圍
        with self.assertRaises(ValueError):
            data = self.valid_station_data.copy()
            data['gps_lng'] = 130.0  # 超出台灣範圍
            Station(**data)

    def test_dilay_name_property(self):
        """測試顯示名稱屬性"""
        station = Station(**self.valid_station_data)
        self.assertEqual(station.display_name, '台北車')

        # 測試不以'站'結尾的名稱
        data = self.valid_station_data.copy()
        data['station_name'] = '桃園機場'
        station = Station(**data)
        self.assertEqual(station.display_name, '桃園機場')

    def test_coordinates_property(self):
        """測試座標屬性"""
        station = Station(**self.valid_station_data)
        coords = station.coordinates
        self.assertEqual(coords, (25.0478, 121.5170))

    def test_distance_calculation(self):
        """測試距離計算"""
        station1 = Station(**self.valid_station_data)

        # 建立第二個車站
        data2 = self.valid_station_data.copy()
        data2['station_code'] = '1001'
        data2['station_name'] = '板橋車站'
        data2['gps_lat'] = 25.0138
        data2['gps_lng'] = 121.4627
        station2 = Station(**data2)

        distance = station1.distance_to(station2)
        self.assertIsInstance(distance, float)
        self.assertGreater(distance, 0)
        self.assertLess(distance, 100)  # 台北到板橋應該小於100公里

    def test_create_station_from_dict(self):
        """測試從字典建立車站"""
        station = create_station_from_dict(self.valid_station_data)
        self.assertIsInstance(station, Station)
        self.assertEqual(station.station_name, '台北車站')

        # 測試缺少必要欄位
        with self.assertRaises(ValueError):
            incomplete_data = self.valid_station_data.copy()
            del incomplete_data['station_code']
            create_station_from_dict(incomplete_data)


class TestPassengerFlow(unittest.TestCase):
    """測試 PassengerFlow 模型"""

    def setUp(self):
        """設定測試資料"""
        self.valid_flow_data = {
            'station_code': '1000',
            'date': date(2024, 1, 15),
            'in_passengers': 5000,
            'out_passengers': 4800
        }

    def test_valid_passenger_flow_creation(self):
        """測試有效客流量建立"""
        flow = PassengerFlow(**self.valid_flow_data)

        self.assertEqual(flow.station_code, '1000')
        self.assertEqual(flow.date, date(2024, 1, 15))
        self.assertEqual(flow.in_passengers, 5000)
        self.assertEqual(flow.out_passengers, 4800)

    def test_total_passengers_property(self):
        """測試總乘客數屬性"""
        flow = PassengerFlow(**self.valid_flow_data)
        self.assertEqual(flow.total_passengers, 9800)

    def test_net_flow_property(self):
        """測試淨流量屬性"""
        flow = PassengerFlow(**self.valid_flow_data)
        self.assertEqual(flow.net_flow, 200)  # 5000 - 4800

    def test_date_properties(self):
        """測試日期相關屬性"""
        flow = PassengerFlow(**self.valid_flow_data)

        self.assertEqual(flow.date_str, '2024-01-15')
        self.assertEqual(flow.weekday, 0)  # 2024-01-15 是星期一
        self.assertFalse(flow.is_weekend)

        # 測試週末
        weekend_data = self.valid_flow_data.copy()
        weekend_data['date'] = date(2024, 1, 13)  # 星期六
        weekend_flow = PassengerFlow(**weekend_data)
        self.assertTrue(weekend_flow.is_weekend)

    def test_invalid_passenger_counts(self):
        """測試無效乘客數量"""
        # 負數
        with self.assertRaises(ValueError):
            data = self.valid_flow_data.copy()
            data['in_passengers'] = -100
            PassengerFlow(**data)

        # 異常高的數值
        with self.assertRaises(ValueError):
            data = self.valid_flow_data.copy()
            data['in_passengers'] = 200000
            PassengerFlow(**data)

    def test_invalid_date(self):
        """測試無效日期"""
        # 未來日期
        with self.assertRaises(ValueError):
            data = self.valid_flow_data.copy()
            data['date'] = date(2030, 1, 1)
            PassengerFlow(**data)

        # 過於久遠的日期
        with self.assertRaises(ValueError):
            data = self.valid_flow_data.copy()
            data['date'] = date(1990, 1, 1)
            PassengerFlow(**data)

    def test_create_passenger_flow_from_dict(self):
        """測試從字典建立客流量"""
        # 測試字串日期
        data = self.valid_flow_data.copy()
        data['date'] = '2024-01-15'
        flow = create_passenger_flow_from_dict(data)
        self.assertIsInstance(flow, PassengerFlow)
        self.assertEqual(flow.date, date(2024, 1, 15))

        # 測試 datetime 物件
        data['date'] = datetime(2024, 1, 15, 10, 30)
        flow = create_passenger_flow_from_dict(data)
        self.assertEqual(flow.date, date(2024, 1, 15))


class TestStationStatistics(unittest.TestCase):
    """測試 StationStatistics 模型"""

    def setUp(self):
        """設定測試資料"""
        self.valid_stats_data = {
            'station_code': '1000',
            'station_name': '台北車站',
            'total_in': 150000,
            'total_out': 148000,
            'total_passengers': 298000,
            'average_daily': 9933.33,
            'date_range': (date(2024, 1, 1), date(2024, 1, 30))
        }

    def test_valid_statistics_creation(self):
        """測試有效統計資料建立"""
        stats = StationStatistics(**self.valid_stats_data)

        self.assertEqual(stats.station_code, '1000')
        self.assertEqual(stats.station_name, '台北車站')
        self.assertEqual(stats.total_passengers, 298000)
        self.assertEqual(stats.average_daily, 9933.33)

    def test_days_count_property(self):
        """測試天數計算屬性"""
        stats = StationStatistics(**self.valid_stats_data)
        self.assertEqual(stats.days_count, 30)

    def test_net_flow_property(self):
        """測試淨流量屬性"""
        stats = StationStatistics(**self.valid_stats_data)
        self.assertEqual(stats.net_flow, 2000)  # 150000 - 148000

    def test_date_range_str_property(self):
        """測試日期範圍字串屬性"""
        stats = StationStatistics(**self.valid_stats_data)
        self.assertEqual(stats.date_range_str, '2024-01-01 ~ 2024-01-30')

    def test_calculate_statistics(self):
        """測試統計計算函數"""
        flows = [
            PassengerFlow('1000', date(2024, 1, 1), 1000, 900),
            PassengerFlow('1000', date(2024, 1, 2), 1200, 1100),
            PassengerFlow('1000', date(2024, 1, 3), 800, 750),
        ]

        stats = calculate_statistics(flows, '台北車站')

        self.assertEqual(stats.station_code, '1000')
        self.assertEqual(stats.station_name, '台北車站')
        self.assertEqual(stats.total_in, 3000)
        self.assertEqual(stats.total_out, 2750)
        self.assertEqual(stats.total_passengers, 5750)
        self.assertEqual(stats.average_daily, 1916.67)


class TestComparisonResult(unittest.TestCase):
    """測試 ComparisonResult 模型"""

    def setUp(self):
        """設定測試資料"""
        self.station1 = StationStatistics(
            '1000', '台北車站', 100000, 95000, 195000, 6500.0,
            (date(2024, 1, 1), date(2024, 1, 30))
        )
        self.station2 = StationStatistics(
            '1001', '板橋車站', 80000, 78000, 158000, 5266.67,
            (date(2024, 1, 1), date(2024, 1, 30))
        )
        self.station3 = StationStatistics(
            '1002', '桃園車站', 60000, 58000, 118000, 3933.33,
            (date(2024, 1, 1), date(2024, 1, 30))
        )

    def test_valid_comparison_result(self):
        """測試有效比較結果"""
        stations = [self.station1, self.station2, self.station3]
        result = ComparisonResult(stations, [])

        self.assertEqual(len(result.stations), 3)
        self.assertEqual(len(result.ranking), 3)

        # 檢查排名順序（按總乘客數降序）
        self.assertEqual(result.ranking[0][0], '台北車站')
        self.assertEqual(result.ranking[1][0], '板橋車站')
        self.assertEqual(result.ranking[2][0], '桃園車站')

    def test_top_station_property(self):
        """測試排名第一車站屬性"""
        stations = [self.station2, self.station1, self.station3]  # 順序打亂
        result = ComparisonResult(stations, [])

        # top_station 應該是原始列表的第一個，不是排名第一的
        self.assertEqual(result.top_station.station_name, '板橋車站')

    def test_total_passengers_all_property(self):
        """測試總乘客數屬性"""
        stations = [self.station1, self.station2, self.station3]
        result = ComparisonResult(stations, [])

        expected_total = 195000 + 158000 + 118000
        self.assertEqual(result.total_passengers_all, expected_total)

    def test_get_station_rank(self):
        """測試取得車站排名"""
        stations = [self.station1, self.station2, self.station3]
        result = ComparisonResult(stations, [])

        self.assertEqual(result.get_station_rank('台北車站'), 1)
        self.assertEqual(result.get_station_rank('板橋車站'), 2)
        self.assertEqual(result.get_station_rank('桃園車站'), 3)
        self.assertIsNone(result.get_station_rank('不存在的車站'))

    def test_too_many_stations(self):
        """測試車站數量限制"""
        stations = [self.station1] * 6  # 6個車站，超過限制

        with self.assertRaises(ValueError):
            ComparisonResult(stations, [])


if __name__ == '__main__':
    unittest.main()