#請幫我自訂一個function
#連線至postgres DB
#建立連線環境參數的樣版
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


def main():
    conn = create_connection()
    if conn:
        print("成功連接到資料庫！")
        conn.close()
    else:
        print("無法連接到資料庫！")

if __name__ == "__main__":
    main()