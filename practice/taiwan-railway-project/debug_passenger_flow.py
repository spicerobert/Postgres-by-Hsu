#!/usr/bin/env python3
"""
客流量查詢功能診斷腳本

此腳本專門用於診斷客流量查詢功能的問題
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, date, timedelta

# 設定專案路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from taiwan_railway_gui.dao.station_dao import StationDAO
from taiwan_railway_gui.dao.passenger_flow_dao import PassengerFlowDAO

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_passenger_flow_query():
    """測試客流量查詢功能"""
    logger.info("🧪 開始診斷客流量查詢功能...")

    try:
        # 1. 測試車站 DAO
        logger.info("1. 測試車站資料...")
        station_dao = StationDAO()
        stations = station_dao.get_all_stations()
        logger.info(f"✅ 找到 {len(stations)} 個車站")

        if not stations:
            logger.error("❌ 沒有車站資料！")
            return False

        # 顯示前5個車站
        logger.info("前5個車站:")
        for i, station in enumerate(stations[:5]):
            logger.info(f"  {i+1}. {station.station_name} ({station.station_code})")

        # 2. 測試客流量 DAO
        logger.info("\n2. 測試客流量資料...")
        flow_dao = PassengerFlowDAO()

        # 使用第一個車站進行測試
        test_station = stations[0]
        logger.info(f"使用測試車站: {test_station.station_name} ({test_station.station_code})")

        # 3. 檢查可用日期範圍
        date_range = flow_dao.get_date_range_available(test_station.station_code)
        if date_range:
            start_date, end_date = date_range
            logger.info(f"✅ 可用日期範圍: {start_date} ~ {end_date}")
        else:
            logger.error(f"❌ 車站 {test_station.station_code} 沒有客流量資料！")
            return False

        # 4. 測試基本查詢
        logger.info("\n3. 測試基本客流量查詢...")

        # 查詢最近7天的資料
        query_end_date = end_date
        query_start_date = max(start_date, query_end_date - timedelta(days=6))

        logger.info(f"查詢日期範圍: {query_start_date} ~ {query_end_date}")

        flows = flow_dao.get_passenger_flow(
            test_station.station_code,
            query_start_date,
            query_end_date
        )

        logger.info(f"✅ 找到 {len(flows)} 筆客流量記錄")

        if flows:
            logger.info("前3筆記錄:")
            for i, flow in enumerate(flows[:3]):
                logger.info(f"  {i+1}. {flow.date}: 進站 {flow.in_passengers:,}, 出站 {flow.out_passengers:,}")
        else:
            logger.warning("⚠️  查詢結果為空")

        # 5. 測試統計資料
        logger.info("\n4. 測試統計資料查詢...")
        stats = flow_dao.get_station_statistics(
            test_station.station_code,
            query_start_date,
            query_end_date
        )

        if stats:
            logger.info(f"✅ 統計資料:")
            logger.info(f"  車站: {stats.station_name}")
            logger.info(f"  總進站人數: {stats.total_in:,}")
            logger.info(f"  總出站人數: {stats.total_out:,}")
            logger.info(f"  總人數: {stats.total_passengers:,}")
            logger.info(f"  平均每日: {stats.average_daily:,.1f}")
        else:
            logger.warning("⚠️  沒有統計資料")

        # 6. 測試所有車站的資料可用性
        logger.info("\n5. 檢查所有車站的資料可用性...")
        stations_with_data = 0
        stations_without_data = []

        for station in stations:
            station_date_range = flow_dao.get_date_range_available(station.station_code)
            if station_date_range:
                stations_with_data += 1
            else:
                stations_without_data.append(station.station_name)

        logger.info(f"✅ {stations_with_data} 個車站有客流量資料")
        if stations_without_data:
            logger.warning(f"⚠️  {len(stations_without_data)} 個車站沒有資料: {', '.join(stations_without_data)}")

        # 7. 測試日期格式
        logger.info("\n6. 測試日期格式...")
        if flows:
            sample_flow = flows[0]
            logger.info(f"範例日期物件: {sample_flow.date} (類型: {type(sample_flow.date)})")

            # 檢查是否有 date_str 屬性
            if hasattr(sample_flow, 'date_str'):
                logger.info(f"日期字串: {sample_flow.date_str}")
            else:
                logger.warning("⚠️  PassengerFlow 物件沒有 date_str 屬性")

            # 檢查是否有其他必要屬性
            required_attrs = ['total_passengers', 'net_flow']
            for attr in required_attrs:
                if hasattr(sample_flow, attr):
                    logger.info(f"✅ 有 {attr} 屬性: {getattr(sample_flow, attr)}")
                else:
                    logger.warning(f"⚠️  沒有 {attr} 屬性")

        logger.info("\n🎉 客流量查詢功能診斷完成！")
        return True

    except Exception as e:
        logger.error(f"❌ 診斷過程中發生錯誤: {e}")
        import traceback
        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return False


def test_gui_integration():
    """測試 GUI 整合"""
    logger.info("\n🖥️  測試 GUI 整合...")

    try:
        # 測試是否可以匯入 GUI 元件
        from taiwan_railway_gui.gui.passenger_flow_tab import PassengerFlowTab
        logger.info("✅ PassengerFlowTab 匯入成功")

        # 測試相關的工具函數
        try:
            from taiwan_railway_gui.utils.formatters import format_number
            logger.info("✅ format_number 函數可用")

            # 測試格式化
            test_number = 12345
            formatted = format_number(test_number)
            logger.info(f"格式化測試: {test_number} -> {formatted}")

        except ImportError:
            logger.warning("⚠️  format_number 函數不可用，可能影響顯示")

        return True

    except Exception as e:
        logger.error(f"❌ GUI 整合測試失敗: {e}")
        return False


def main():
    """主函數"""
    logger.info("🚀 開始客流量查詢功能診斷")
    logger.info("=" * 60)

    success = True

    # 測試資料層
    if not test_passenger_flow_query():
        success = False

    # 測試 GUI 整合
    if not test_gui_integration():
        success = False

    logger.info("=" * 60)
    if success:
        logger.info("🎉 所有診斷測試通過！")
        logger.info("\n💡 如果 GUI 中仍然沒有顯示資料，可能的原因:")
        logger.info("1. 日期選擇器的日期範圍不正確")
        logger.info("2. 車站選擇沒有正確傳遞")
        logger.info("3. GUI 更新邏輯有問題")
        logger.info("4. 錯誤處理掩蓋了實際問題")
        logger.info("\n🔧 建議檢查:")
        logger.info("- 檢查應用程式日誌檔案 taiwan_railway_gui.log")
        logger.info("- 確認選擇的日期範圍在可用範圍內")
        logger.info("- 嘗試選擇不同的車站")
    else:
        logger.error("💥 診斷發現問題，請檢查上述錯誤訊息")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)