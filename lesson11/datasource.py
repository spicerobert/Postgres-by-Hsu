import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_stations_names():
    """
    取得台鐵車站名稱列表
    :return: 台鐵車站名稱列表，連線失敗時回傳 None
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("HOST"),
            database=os.getenv("DATABASE"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            port="5432"
        )

        cursor = conn.cursor()
        query = """
        SELECT name
        FROM "台鐵車站資訊";
        """
        cursor.execute(query)
        result = cursor.fetchall()

        # 使用 list comprehension 簡化程式碼
        result_list = [station[0] for station in result]

        return result_list

    except psycopg2.Error as e:
        print(f"資料庫連線或查詢失敗：{e}")
        return None
    except Exception as e:
        print(f"發生未預期的錯誤：{e}")
        return None
    finally:
        # 確保資源正確釋放
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_min_and_max_date():
    """
    取得資料表中的最小和最大日期
    :return: (最小日期, 最大日期)，連線失敗時回傳 None
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("HOST"),
            database=os.getenv("DATABASE"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            port="5432"
        )

        cursor = conn.cursor()
        query = """
        SELECT MIN("日期") AS min_date, MAX("日期") AS max_date
        FROM public."每日各站進出站人數";
        """
        cursor.execute(query)
        result = cursor.fetchone()

        return result

    except psycopg2.Error as e:
        print(f"資料庫連線或查詢失敗：{e}")
        return None
    except Exception as e:
        print(f"發生未預期的錯誤：{e}")
        return None
    finally:
        # 確保資源正確釋放
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_station_data_by_date(station_name, start_date, end_date):
    """
    取得指定車站在特定日期範圍內的進出人數資料
    :param station_name: 車站名稱
    :param start_date: 起始日期
    :param end_date: 結束日期
    :return: 車站資料列表，連線失敗時回傳 None
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("HOST"),
            database=os.getenv("DATABASE"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            port="5432"
        )

        cursor = conn.cursor()
        query = """
        SELECT p."日期",
               t."stationName" AS 車站,
               p."進站人數",
               p."出站人數"
        FROM public."每日各站進出站人數" p
        JOIN public."台鐵車站資訊" t
          ON p."車站代碼" = t."stationCode"
        WHERE p."日期" BETWEEN %s AND %s
          AND t."stationName" = %s
        ORDER BY p."日期";
        """
        # 使用參數化查詢避免 SQL 注入，並使用提供的函式參數
        cursor.execute(query, (start_date, end_date, station_name))
        result = cursor.fetchall()

        return result

    except psycopg2.Error as e:
        print(f"資料庫連線或查詢失敗：{e}")
        return None
    except Exception as e:
        print(f"發生未預期的錯誤：{e}")
        return None
    finally:
        # 確保資源正確釋放
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

