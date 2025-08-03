import db

def main():
    stations = db.get_all_stations()
    print("所有台鐵車站資訊的站點名稱：", stations)


if __name__ == "__main__":
    main()