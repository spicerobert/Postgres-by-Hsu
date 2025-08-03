import psycopg2

def execute_query(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

def create_connection():
    conn = psycopg2.connect(
        host="host.docker.internal",
        database="postgres",
        user="postgres",
        password="raspberry",
        port="5432"
    )
    return conn


def main():
    conn = create_connection()
    if conn:
        print("成功連接到資料庫！")
        query = """
        SELECT count(*) AS "筆數"
        FROM "台鐵車站資訊";
        """
        result = execute_query(conn, query)
        print("台鐵車站資訊：", result)
        conn.close()
    else:
        print("無法連接到資料庫，請檢查設定。")
        return

if __name__ == "__main__":
    main()