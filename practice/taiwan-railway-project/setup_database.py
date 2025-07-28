#!/usr/bin/env python3
"""
資料庫設定腳本

此腳本負責建立台鐵車站資訊查詢應用程式所需的資料庫表格和初始資料。

功能：
1. 建立 stations 表格（車站資訊）
2. 建立 passenger_flow 表格（客流量資料）
3. 插入基本的車站資料
4. 插入範例客流量資料

使用方式：
    python setup_database.py

作者: Taiwan Railway GUI Team
版本: 1.0.0
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, date, timedelta
import random

# 設定專案路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from taiwan_railway_gui.dao.database_manager import DatabaseManager

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_tables():
    """建立資料庫表格"""
    logger.info("建立資料庫表格...")

    db_manager = DatabaseManager()

    # 建立 stations 表格
    stations_sql = """
    CREATE TABLE IF NOT EXISTS stations (
        station_code VARCHAR(10) PRIMARY KEY,
        station_name VARCHAR(100) NOT NULL,
        address VARCHAR(200),
        phone VARCHAR(20),
        gps_lat DECIMAL(10, 8),
        gps_lng DECIMAL(11, 8),
        has_bike_rental BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # 建立 passenger_flow 表格
    passenger_flow_sql = """
    CREATE TABLE IF NOT EXISTS passenger_flow (
        id SERIAL PRIMARY KEY,
        station_code VARCHAR(10) NOT NULL,
        date DATE NOT NULL,
        in_passengers INTEGER DEFAULT 0,
        out_passengers INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (station_code) REFERENCES stations(station_code),
        UNIQUE(station_code, date)
    );
    """

    # 建立索引
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_stations_name ON stations(station_name);",
        "CREATE INDEX IF NOT EXISTS idx_passenger_flow_station_date ON passenger_flow(station_code, date);",
        "CREATE INDEX IF NOT EXISTS idx_passenger_flow_date ON passenger_flow(date);"
    ]

    try:
        # 執行建表語句
        db_manager.execute_query(stations_sql)
        logger.info("✅ stations 表格建立成功")

        db_manager.execute_query(passenger_flow_sql)
        logger.info("✅ passenger_flow 表格建立成功")

        # 建立索引
        for index_sql in indexes_sql:
            db_manager.execute_query(index_sql)
        logger.info("✅ 索引建立成功")

    except Exception as e:
        logger.error(f"❌ 建立表格失敗: {e}")
        raise


def insert_sample_stations():
    """插入範例車站資料"""
    logger.info("插入範例車站資料...")

    db_manager = DatabaseManager()

    # 範例車站資料
    stations_data = [
        ('1000', '台北', '台北市中正區北平西路3號', '02-23713558', 25.047924, 121.517081, True),
        ('1001', '台中', '台中市中區台灣大道一段1號', '04-22227236', 24.137000, 120.685000, True),
        ('1002', '高雄', '高雄市三民區建國二路318號', '07-2352376', 22.639000, 120.302000, True),
        ('900', '基隆', '基隆市仁愛區港西街5號', '02-24263743', 25.13411, 121.73997, True),
        ('910', '三坑', '基隆市仁愛區德厚里龍安街206號', '02-24230289', 25.12305, 121.74202, True),
        ('920', '八堵', '基隆市暖暖區八南里八堵路142號', '02-24560841', 25.10843, 121.72898, True),
        ('930', '七堵', '基隆市七堵區長興里東新街2號', '02-24553426', 25.09294, 121.71415, True),
        ('940', '百福', '基隆市七堵區堵南里明德三路1之1號', '02-24528372', 25.07795, 121.69379, False),
        ('7361', '海科館', '基隆市中正區長潭里', '02-24972033', 25.13754, 121.79997, False),
        ('7390', '暖暖', '基隆市暖暖區暖暖里暖暖街51號', '02-24972033', 25.10224, 121.74048, False),
        ('1100', '桃園', '桃園市桃園區中正路1號', '03-3322101', 24.989000, 121.315000, True),
        ('1200', '新竹', '新竹市東區中華路二段445號', '03-5323301', 24.801000, 120.971000, True),
        ('1300', '苗栗', '苗栗縣苗栗市為公路玉清里綠苗里車站前', '037-320684', 24.565000, 120.821000, False),
        ('1400', '彰化', '彰化縣彰化市三民路1號', '04-7222105', 24.081000, 120.544000, True),
        ('1500', '嘉義', '嘉義市西區中山路528號', '05-2228904', 23.479000, 120.441000, True),
    ]

    insert_sql = """
    INSERT INTO stations (station_code, station_name, address, phone, gps_lat, gps_lng, has_bike_rental)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (station_code) DO UPDATE SET
        station_name = EXCLUDED.station_name,
        address = EXCLUDED.address,
        phone = EXCLUDED.phone,
        gps_lat = EXCLUDED.gps_lat,
        gps_lng = EXCLUDED.gps_lng,
        has_bike_rental = EXCLUDED.has_bike_rental,
        updated_at = CURRENT_TIMESTAMP;
    """

    try:
        for station_data in stations_data:
            db_manager.execute_query(insert_sql, station_data)

        logger.info(f"✅ 成功插入 {len(stations_data)} 個車站資料")

    except Exception as e:
        logger.error(f"❌ 插入車站資料失敗: {e}")
        raise


def insert_sample_passenger_flow():
    """插入範例客流量資料"""
    logger.info("插入範例客流量資料...")

    db_manager = DatabaseManager()

    # 取得所有車站代碼
    stations_query = "SELECT station_code FROM stations;"
    stations_result = db_manager.execute_query(stations_query)

    if not stations_result:
        logger.warning("沒有找到車站資料，跳過客流量資料插入")
        return

    station_codes = [row['station_code'] for row in stations_result]

    # 生成過去30天的資料
    end_date = date.today() - timedelta(days=1)  # 昨天
    start_date = end_date - timedelta(days=29)   # 30天前

    insert_sql = """
    INSERT INTO passenger_flow (station_code, date, in_passengers, out_passengers)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (station_code, date) DO UPDATE SET
        in_passengers = EXCLUDED.in_passengers,
        out_passengers = EXCLUDED.out_passengers;
    """

    try:
        total_records = 0
        current_date = start_date

        while current_date <= end_date:
            for station_code in station_codes:
                # 根據車站規模生成不同範圍的客流量
                if station_code in ['1000', '1001', '1002']:  # 大站
                    base_in = random.randint(8000, 15000)
                    base_out = random.randint(7500, 14500)
                elif station_code in ['1100', '1200', '1400', '1500']:  # 中站
                    base_in = random.randint(3000, 8000)
                    base_out = random.randint(2800, 7800)
                else:  # 小站
                    base_in = random.randint(500, 3000)
                    base_out = random.randint(450, 2900)

                # 週末調整（週六日客流量可能不同）
                if current_date.weekday() >= 5:  # 週末
                    base_in = int(base_in * random.uniform(0.7, 1.3))
                    base_out = int(base_out * random.uniform(0.7, 1.3))

                db_manager.execute_query(insert_sql, (station_code, current_date, base_in, base_out))
                total_records += 1

            current_date += timedelta(days=1)

        logger.info(f"✅ 成功插入 {total_records} 筆客流量資料")

    except Exception as e:
        logger.error(f"❌ 插入客流量資料失敗: {e}")
        raise


def verify_setup():
    """驗證資料庫設定"""
    logger.info("驗證資料庫設定...")

    db_manager = DatabaseManager()

    try:
        # 檢查車站數量
        stations_count_query = "SELECT COUNT(*) as count FROM stations;"
        stations_result = db_manager.execute_query(stations_count_query, fetch_one=True)
        stations_count = stations_result['count'] if stations_result else 0

        # 檢查客流量資料數量
        flow_count_query = "SELECT COUNT(*) as count FROM passenger_flow;"
        flow_result = db_manager.execute_query(flow_count_query, fetch_one=True)
        flow_count = flow_result['count'] if flow_result else 0

        # 檢查日期範圍
        date_range_query = """
        SELECT MIN(date) as min_date, MAX(date) as max_date
        FROM passenger_flow;
        """
        date_result = db_manager.execute_query(date_range_query, fetch_one=True)

        logger.info("=" * 50)
        logger.info("📊 資料庫設定驗證結果")
        logger.info("=" * 50)
        logger.info(f"🚉 車站數量: {stations_count}")
        logger.info(f"📈 客流量記錄數: {flow_count}")

        if date_result and date_result['min_date'] and date_result['max_date']:
            logger.info(f"📅 資料日期範圍: {date_result['min_date']} 到 {date_result['max_date']}")

        # 顯示一些範例資料
        sample_query = """
        SELECT s.station_name, pf.date, pf.in_passengers, pf.out_passengers
        FROM passenger_flow pf
        JOIN stations s ON pf.station_code = s.station_code
        ORDER BY pf.date DESC, pf.in_passengers DESC
        LIMIT 5;
        """
        sample_result = db_manager.execute_query(sample_query)

        if sample_result:
            logger.info("\n📋 範例客流量資料:")
            for row in sample_result:
                logger.info(f"  {row['station_name']} ({row['date']}): 進站 {row['in_passengers']}, 出站 {row['out_passengers']}")

        logger.info("=" * 50)
        logger.info("✅ 資料庫設定驗證完成")

    except Exception as e:
        logger.error(f"❌ 資料庫驗證失敗: {e}")
        raise


def main():
    """主函數"""
    logger.info("🚀 開始設定台鐵車站資訊查詢應用程式資料庫")
    logger.info("=" * 60)

    try:
        # 1. 建立表格
        create_tables()

        # 2. 插入車站資料
        insert_sample_stations()

        # 3. 插入客流量資料
        insert_sample_passenger_flow()

        # 4. 驗證設定
        verify_setup()

        logger.info("=" * 60)
        logger.info("🎉 資料庫設定完成！應用程式已準備好使用。")

    except Exception as e:
        logger.error(f"💥 資料庫設定失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()