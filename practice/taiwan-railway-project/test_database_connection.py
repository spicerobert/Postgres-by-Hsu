#!/usr/bin/env python3
"""
資料庫連線測試腳本

測試資料庫連線和基本查詢功能。
"""

import sys
import os
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
from taiwan_railway_gui.dao.database_manager import get_database_manager
from taiwan_railway_gui.dao.station_dao import create_station_dao
from taiwan_railway_gui.dao.passenger_flow_dao import create_passenger_flow_dao

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database_connection():
    """測試資料庫連線"""
    print("=== 測試資料庫連線 ===")

    try:
        db_manager = get_database_manager()

        # 測試連線
        if db_manager.test_connection():
            print("✅ 資料庫連線成功")
            return True
        else:
            print("❌ 資料庫連線失敗")
            return False

    except Exception as e:
        print(f"❌ 資料庫連線錯誤: {e}")
        return False


def test_station_dao():
    """測試車站 DAO"""
    print("\n=== 測試車站 DAO ===")

    try:
        station_dao = create_station_dao()

        # 測試取得所有車站（限制前5個）
        stations = station_dao.get_all_stations()[:5]
        if stations:
            print(f"✅ 成功取得 {len(stations)} 個車站:")
            for station in stations:
                print(f"  - {station.station_name} ({station.station_code})")
        else:
            print("⚠️  沒有找到車站資料")

        # 測試搜尋功能
        if stations:
            first_station = stations[0]
            search_results = station_dao.search_stations(first_station.station_name[:2])
            print(f"✅ 搜尋 '{first_station.station_name[:2]}' 找到 {len(search_results)} 個結果")

        return True

    except Exception as e:
        print(f"❌ 車站 DAO 測試失敗: {e}")
        return False


def test_passenger_flow_dao():
    """測試客流量 DAO"""
    print("\n=== 測試客流量 DAO ===")

    try:
        flow_dao = create_passenger_flow_dao()
        station_dao = create_station_dao()

        # 取得一個車站進行測試
        stations = station_dao.get_all_stations()[:1]
        if not stations:
            print("⚠️  沒有車站資料，跳過客流量測試")
            return True

        test_station = stations[0]
        print(f"使用測試車站: {test_station.station_name}")

        # 測試取得可用日期範圍
        date_range = flow_dao.get_date_range_available(test_station.station_code)
        if date_range:
            print(f"✅ 可用日期範圍: {date_range[0]} ~ {date_range[1]}")

            # 測試取得統計資料
            statistics = flow_dao.get_station_statistics(
                test_station.station_code,
                date_range[0],
                min(date_range[1], date_range[0] + timedelta(days=30))
            )

            if statistics:
                print(f"✅ 統計資料: 總人數 {statistics.total_passengers:,}, 平均每日 {statistics.average_daily:.0f}")
            else:
                print("⚠️  沒有統計資料")
        else:
            print("⚠️  沒有客流量資料")

        return True

    except Exception as e:
        print(f"❌ 客流量 DAO 測試失敗: {e}")
        return False


def main():
    """主函數"""
    print("台鐵 GUI 應用程式 - 資料庫連線測試")
    print("=" * 50)

    # 檢查必要套件
    try:
        import psycopg2
        print("✅ psycopg2 套件已安裝")
    except ImportError:
        print("❌ psycopg2 套件未安裝，請執行: pip install psycopg2-binary")
        return False

    # 測試資料庫連線
    if not test_database_connection():
        print("\n請檢查資料庫設定和連線資訊")
        return False

    # 測試 DAO 功能
    station_success = test_station_dao()
    flow_success = test_passenger_flow_dao()

    print("\n" + "=" * 50)
    if station_success and flow_success:
        print("✅ 所有測試通過！資料庫連線和 DAO 層運作正常")
        return True
    else:
        print("❌ 部分測試失敗，請檢查資料庫結構和資料")
        return False


if __name__ == "__main__":
    from datetime import timedelta
    success = main()
    sys.exit(0 if success else 1)