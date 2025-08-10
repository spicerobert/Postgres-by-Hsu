import datasource

def main():
    results = datasource.get_stations_names()
    if results:
        for station in results:
            print(station)
    else:
        print("無法取得車站資料")

if __name__ == "__main__":
    main()