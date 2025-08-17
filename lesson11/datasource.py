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