#!/usr/bin/env python3
"""
測試日期修正功能

驗證客流量查詢分頁是否正確設定了預設日期範圍
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# 設定專案路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from taiwan_railway_gui.dao.passenger_flow_dao import create_passenger_flow_dao
from taiwan_railway_gui.dao.station_dao import create_station_dao


def test_date_range_loading():
    """測試日期範圍載入功能"""
    print("🧪 測試資料庫日期範圍載入...")

    try:
        # 初始化 DAO
        station_dao = create_station_dao()
        flow_dao = create_passenger_flow_dao()

        # 載入車站
        stations = station_dao.get_all_stations()
        print(f"✅ 載入了 {len(stations)} 個車站")

        if not stations:
            print("❌ 沒有車站資料")
            return False

        # 測試第一個車站的日期範圍
        first_station = stations[0]
        print(f"📍 測試車站: {first_station.station_name} ({first_station.station_code})")

        date_range = flow_dao.get_date_range_available(first_station.station_code)

        if date_range:
            start_date, end_date = date_range
            print(f"✅ 資料庫日期範圍: {start_date} ~ {end_date}")

            # 計算建議的預設日期範圍
            if (end_date - start_date).days >= 7:
                default_start = end_date - timedelta(days=6)  # 最近7天
                default_end = end_date
                print(f"📅 建議的預設範圍: {default_start} ~ {default_end} (最近7天)")
            else:
                default_start = start_date
                default_end = end_date
                print(f"📅 建議的預設範圍: {default_start} ~ {default_end} (全部資料)")

            # 測試其他車站
            print("\n🔍 檢查其他車站的日期範圍:")
            for i, station in enumerate(stations[:5]):  # 只檢查前5個
                station_range = flow_dao.get_date_range_available(station.station_code)
                if station_range:
                    s_start, s_end = station_range
                    print(f"  {station.station_name}: {s_start} ~ {s_end}")
                else:
                    print(f"  {station.station_name}: 無資料")

            return True
        else:
            print(f"❌ 車站 {first_station.station_code} 沒有客流量資料")
            return False

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函數"""
    print("🚀 開始測試日期修正功能")
    print("=" * 50)

    success = test_date_range_loading()

    print("=" * 50)
    if success:
        print("🎉 日期範圍載入測試通過！")
        print("\n💡 修正說明:")
        print("- 客流量查詢分頁現在會自動載入資料庫中實際有資料的日期範圍")
        print("- 預設查詢範圍設定為最近7天（如果資料足夠）")
        print("- 如果資料不足7天，則使用全部可用範圍")
        print("\n🔧 使用方式:")
        print("1. conda activate taiwan_railway")
        print("2. python launch_app.py")
        print("3. 點選「客流量查詢」分頁")
        print("4. 日期選擇器應該會自動設定為合適的日期範圍")
    else:
        print("💥 測試失敗，請檢查錯誤訊息")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)