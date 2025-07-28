"""
整合測試配置

定義整合測試的配置參數和設定。
"""

import os
import tempfile
from datetime import datetime, timedelta

# 測試資料庫配置
TEST_DATABASE_CONFIG = {
    'database_type': 'sqlite',
    'database_path': None,  # 將在測試時動態生成
}

# 測試資料配置
TEST_DATA_CONFIG = {
    # 測試車站資料
    'test_stations': [
        {
            'station_id': '1000',
            'station_name': '台北',
            'station_class': '特等',
            'line_name': '縱貫線',
            'address': '台北市中正區黎明里北平西路3號',
            'phone': '02-23713558',
            'coordinates': '25.047924,121.517081'
        },
        {
            'station_id': '1001',
            'station_name': '板橋',
            'station_class': '一等',
            'line_name': '縱貫線',
            'address': '新北市板橋區縣民大道二段7號',
            'phone': '02-29603000',
            'coordinates': '25.013807,121.464132'
        },
        {
            'station_id': '1008',
            'station_name': '桃園',
            'station_class': '一等',
            'line_name': '縱貫線',
            'address': '桃園市桃園區中正路1號',
            'phone': '03-3322340',
            'coordinates': '24.989197,121.314007'
        },
        {
            'station_id': '1025',
            'station_name': '新竹',
            'station_class': '一等',
            'line_name': '縱貫線',
            'address': '新竹市東區榮光里中華路二段445號',
            'phone': '03-5323441',
            'coordinates': '24.801416,120.971736'
        },
        {
            'station_id': '1100',
            'station_name': '台中',
            'station_class': '特等',
            'line_name': '縱貫線',
            'address': '台中市中區台灣大道一段1號',
            'phone': '04-22227236',
            'coordinates': '24.136675,120.684175'
        }
    ],

    # 測試日期範圍
    'test_date_range': {
        'start_date': datetime.now() - timedelta(days=30),
        'end_date': datetime.now(),
        'large_dataset_days': 90
    },

    # 測試乘客流量資料生成參數
    'passenger_flow_params': {
        'base_inbound': 1000,
        'base_outbound': 950,
        'daily_variation': 50,
        'station_variation': 100
    }
}

# GUI測試配置
GUI_TEST_CONFIG = {
    'wait_timeout': 2.0,
    'input_delay': 0.1,
    'update_delay': 0.01,
    'hide_test_windows': True
}

# 效能測試配置
PERFORMANCE_TEST_CONFIG = {
    'max_query_time': 10.0,  # 秒
    'max_memory_increase': 100,  # MB
    'large_dataset_size': 90,  # 天數
    'pagination_size': 50
}

# 錯誤測試配置
ERROR_TEST_CONFIG = {
    'invalid_station_id': '9999',
    'invalid_date_format': '2023-13-45',
    'non_existent_file_path': '/invalid/path/file.txt',
    'permission_denied_path': '/root/test_file.txt'
}

# 測試檔案路徑
TEST_PATHS = {
    'temp_dir': tempfile.gettempdir(),
    'test_export_file': os.path.join(tempfile.gettempdir(), 'test_export.csv'),
    'test_chart_file': os.path.join(tempfile.gettempdir(), 'test_chart.png')
}


def get_test_database_path():
    """取得測試資料庫路徑"""
    return tempfile.mktemp(suffix='.db', prefix='taiwan_railway_test_')


def get_test_config(section=None):
    """取得測試配置"""
    config_map = {
        'database': TEST_DATABASE_CONFIG,
        'data': TEST_DATA_CONFIG,
        'gui': GUI_TEST_CONFIG,
        'performance': PERFORMANCE_TEST_CONFIG,
        'error': ERROR_TEST_CONFIG,
        'paths': TEST_PATHS
    }

    if section:
        return config_map.get(section, {})
    else:
        return config_map


def setup_test_environment():
    """設定測試環境"""
    # 建立測試目錄
    os.makedirs(TEST_PATHS['temp_dir'], exist_ok=True)

    # 設定測試資料庫路徑
    TEST_DATABASE_CONFIG['database_path'] = get_test_database_path()

    return TEST_DATABASE_CONFIG


def cleanup_test_environment(db_path=None):
    """清理測試環境"""
    # 清理測試資料庫
    if db_path and os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except OSError:
            pass

    # 清理測試檔案
    for file_path in [TEST_PATHS['test_export_file'], TEST_PATHS['test_chart_file']]:
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except OSError:
                pass


# 測試資料生成函數
def generate_test_passenger_flow_data(station_id, start_date, days_count):
    """生成測試乘客流量資料"""
    data = []
    params = TEST_DATA_CONFIG['passenger_flow_params']

    for i in range(days_count):
        current_date = start_date + timedelta(days=i)

        # 計算基本數值
        station_num = int(station_id) % 100
        inbound = (params['base_inbound'] +
                  (i * params['daily_variation']) +
                  station_num)
        outbound = (params['base_outbound'] +
                   (i * (params['daily_variation'] - 5)) +
                   station_num - 10)
        total = inbound + outbound

        data.append({
            'station_id': station_id,
            'date': current_date.strftime('%Y-%m-%d'),
            'inbound_passengers': inbound,
            'outbound_passengers': outbound,
            'total_passengers': total
        })

    return data


def get_test_station_by_id(station_id):
    """根據ID取得測試車站資料"""
    for station in TEST_DATA_CONFIG['test_stations']:
        if station['station_id'] == station_id:
            return station
    return None


def get_all_test_stations():
    """取得所有測試車站資料"""
    return TEST_DATA_CONFIG['test_stations'].copy()


# 測試斷言輔助函數
def assert_station_data_valid(test_case, station_data):
    """驗證車站資料的有效性"""
    required_fields = ['station_id', 'station_name', 'station_class', 'line_name']

    for field in required_fields:
        test_case.assertIn(field, station_data, f"車站資料應包含 {field} 欄位")
        test_case.assertIsNotNone(station_data[field], f"{field} 不應為空")


def assert_passenger_flow_data_valid(test_case, flow_data):
    """驗證乘客流量資料的有效性"""
    required_fields = ['station_id', 'date', 'inbound_passengers', 'outbound_passengers']

    for field in required_fields:
        test_case.assertIn(field, flow_data, f"乘客流量資料應包含 {field} 欄位")

    # 檢查數值欄位
    test_case.assertIsInstance(flow_data['inbound_passengers'], int)
    test_case.assertIsInstance(flow_data['outbound_passengers'], int)
    test_case.assertGreaterEqual(flow_data['inbound_passengers'], 0)
    test_case.assertGreaterEqual(flow_data['outbound_passengers'], 0)


def assert_gui_component_exists(test_case, parent, component_name):
    """驗證GUI元件是否存在"""
    test_case.assertTrue(
        hasattr(parent, component_name),
        f"GUI元件 {component_name} 應該存在"
    )

    component = getattr(parent, component_name)
    test_case.assertIsNotNone(component, f"{component_name} 不應為 None")
