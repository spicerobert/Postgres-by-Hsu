import psycopg2


def create_connection():
    conn = psycopg2.connect(
        host="host.docker.internal",
        database="postgres",
        user="postgres",
        password="raspberry",
        port="5432"
    )
    return conn

#建立一個function,功能是取得所有台鐵車站資訊的站點名稱
def get_all_stations():
    """
    取得所有台鐵車站的名稱。

    此函式會連接至資料庫，查詢「台鐵車站資訊」資料表中的所有車站名稱，並以列表形式回傳查詢結果。

    回傳值:
        list: 包含所有車站名稱的查詢結果，每個元素為一個元組(tuple)。
    """
    conn = create_connection()
    cursor = conn.cursor()
    query = """
    SELECT "name"
    FROM "台鐵車站資訊";
    """
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def main():
    stations = get_all_stations()
    print("所有台鐵車站資訊的站點名稱：", stations)


if __name__ == "__main__":
    main()