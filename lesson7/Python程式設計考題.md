# Python 程式設計考題

## 考題一：Python 基本資料型別應用

### 題目描述
請編寫一個 Python 程式，實現以下功能：

1. 宣告並輸出四種基本資料型別的變數（int, float, str, bool）
2. 使用 `type()` 函數檢查每個變數的資料型別
3. 將整數和浮點數進行運算，並輸出結果及其型別
4. 使用布林值進行邏輯運算

### 預期輸出範例
```
整數值: 100, 型別: <class 'int'>
浮點數值: 3.14, 型別: <class 'float'>
字串值: Hello Python, 型別: <class 'str'>
布林值: True, 型別: <class 'bool'>
運算結果: 103.14, 型別: <class 'float'>
邏輯運算: False
```

### 解答
```python
# 宣告四種基本資料型別的變數
integer_var = 100        # 整數
float_var = 3.14         # 浮點數
string_var = "Hello Python"  # 字串
bool_var = True          # 布林值

# 輸出變數值及其型別
print(f"整數值: {integer_var}, 型別: {type(integer_var)}")
print(f"浮點數值: {float_var}, 型別: {type(float_var)}")
print(f"字串值: {string_var}, 型別: {type(string_var)}")
print(f"布林值: {bool_var}, 型別: {type(bool_var)}")

# 進行數值運算
result = integer_var + float_var
print(f"運算結果: {result}, 型別: {type(result)}")

# 進行邏輯運算
logic_result = bool_var and False
print(f"邏輯運算: {logic_result}")
```

### 解析
- **資料型別轉換**：當整數與浮點數運算時，Python 會自動將結果轉換為浮點數
- **type() 函數**：用於檢查變數的資料型別
- **f-string 格式化**：使用 f"" 語法進行字串格式化，更簡潔易讀

---

## 考題二：字串處理與 SQL 語句生成

### 題目描述
根據課程中的台鐵車站資料，編寫一個 Python 程式：

1. 使用多行字串建立一個 SQL CREATE TABLE 語句
2. 建立一個函數，接受城市名稱作為參數，生成對應的 SELECT 查詢語句
3. 使用字串方法處理和格式化輸出

### 預期功能
- 能夠生成建立台鐵車站資訊表的 SQL 語句
- 根據輸入的城市名稱，生成查詢該城市車站的 SQL 語句
- 正確處理字串中的引號和特殊字元

### 解答
```python
def create_table_sql():
    """建立台鐵車站資訊表的 SQL 語句"""
    sql = """CREATE TABLE 台鐵車站資訊 (
    "stationCode" int4 NOT NULL,
    "stationName" varchar(50) NULL,
    "name" varchar(50) NULL,
    "stationAddrTw" varchar(50) NULL,
    "stationTel" varchar(50) NULL,
    gps varchar(50) NULL,
    "haveBike" varchar(50) NULL,
    CONSTRAINT 台鐵車站資訊_pkey PRIMARY KEY ("stationCode")
);"""
    return sql

def generate_city_query(city_name):
    """根據城市名稱生成查詢 SQL 語句"""
    sql = f"""SELECT
    "stationCode",
    "stationName",
    "stationAddrTw"
FROM
    "台鐵車站資訊"
WHERE
    "stationAddrTw" LIKE '{city_name}%';"""
    return sql

def main():
    # 顯示建表語句
    print("=== 建立資料表 SQL ===")
    print(create_table_sql())
    print()

    # 測試不同城市的查詢
    cities = ["基隆市", "台北市", "新北市"]

    for city in cities:
        print(f"=== {city}車站查詢 ===")
        query = generate_city_query(city)
        print(query)
        print()

# 執行主程式
if __name__ == "__main__":
    main()
```

### 解析
- **多行字串**：使用 `"""` 建立多行字串，適合 SQL 語句
- **字串格式化**：使用 f-string 動態插入城市名稱
- **函數設計**：將功能模組化，提高程式碼重用性
- **SQL 注入防護**：實際應用中應使用參數化查詢防止 SQL 注入

---

## 考題三：資料處理與檔案操作

### 題目描述
設計一個 Python 程式來處理台鐵車站資料：

1. 讀取 CSV 檔案中的車站資訊
2. 根據地址篩選特定縣市的車站
3. 將結果儲存到新的檔案中
4. 提供統計資訊（如車站數量、是否有 YouBike 等）

### 程式需求
- 使用適當的資料結構儲存車站資訊
- 實現資料篩選和統計功能
- 處理檔案讀寫操作
- 提供清晰的使用者介面

### 解答
```python
import csv
from collections import defaultdict

class StationAnalyzer:
    """台鐵車站資料分析器"""

    def __init__(self):
        self.stations = []
        self.city_stats = defaultdict(int)

    def load_stations_from_csv(self, filename):
        """從 CSV 檔案載入車站資料"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.stations.append(row)
                    # 統計各縣市車站數量
                    city = self.extract_city(row.get('stationAddrTw', ''))
                    self.city_stats[city] += 1
            print(f"成功載入 {len(self.stations)} 筆車站資料")
        except FileNotFoundError:
            print(f"找不到檔案: {filename}")
        except Exception as e:
            print(f"讀取檔案時發生錯誤: {e}")

    def extract_city(self, address):
        """從地址中提取縣市名稱"""
        if not address:
            return "未知"

        cities = ["台北市", "新北市", "基隆市", "桃園市", "新竹市", "新竹縣",
                 "苗栗縣", "台中市", "彰化縣", "南投縣", "雲林縣", "嘉義市",
                 "嘉義縣", "台南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "台東縣"]

        for city in cities:
            if city in address:
                return city
        return "其他"

    def filter_by_city(self, target_city):
        """篩選特定縣市的車站"""
        filtered_stations = []
        for station in self.stations:
            address = station.get('stationAddrTw', '')
            if target_city in address:
                filtered_stations.append(station)
        return filtered_stations

    def generate_city_report(self, city):
        """生成城市車站報告"""
        filtered_stations = self.filter_by_city(city)

        if not filtered_stations:
            return f"{city} 沒有找到車站資料"

        # 統計有 YouBike 的車站
        bike_stations = [s for s in filtered_stations
                        if s.get('haveBike', '').lower() == 'y']

        report = f"""
=== {city} 車站分析報告 ===
總車站數: {len(filtered_stations)}
有 YouBike 的車站: {len(bike_stations)}
YouBike 覆蓋率: {len(bike_stations)/len(filtered_stations)*100:.1f}%

車站清單:
"""

        for i, station in enumerate(filtered_stations, 1):
            bike_status = "有YouBike" if station.get('haveBike', '').lower() == 'y' else "無YouBike"
            report += f"{i:2d}. {station.get('stationName', '未知')} - {bike_status}\n"

        return report

    def save_filtered_data(self, city, filename):
        """將篩選後的資料儲存到檔案"""
        filtered_stations = self.filter_by_city(city)

        try:
            with open(filename, 'w', encoding='utf-8', newline='') as file:
                if filtered_stations:
                    fieldnames = filtered_stations[0].keys()
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(filtered_stations)
                print(f"已將 {city} 的 {len(filtered_stations)} 筆資料儲存至 {filename}")
        except Exception as e:
            print(f"儲存檔案時發生錯誤: {e}")

    def show_overall_stats(self):
        """顯示整體統計資訊"""
        print("\n=== 整體統計 ===")
        total_stations = sum(self.city_stats.values())
        print(f"總車站數: {total_stations}")
        print("\n各縣市車站分布:")

        # 按車站數量排序
        sorted_cities = sorted(self.city_stats.items(),
                             key=lambda x: x[1], reverse=True)

        for city, count in sorted_cities:
            percentage = count / total_stations * 100
            print(f"  {city}: {count:3d} 站 ({percentage:5.1f}%)")

def main():
    """主程式"""
    analyzer = StationAnalyzer()

    # 模擬資料載入（實際使用時請替換為真實檔案路徑）
    print("台鐵車站資料分析系統")
    print("=" * 30)

    # 由於沒有實際 CSV 檔案，我們建立一些範例資料
    sample_data = [
        {"stationCode": "1001", "stationName": "基隆站", "stationAddrTw": "基隆市仁愛區港西街206號", "haveBike": "Y"},
        {"stationCode": "1002", "stationName": "三坑站", "stationAddrTw": "基隆市仁愛區", "haveBike": "N"},
        {"stationCode": "1003", "stationName": "台北站", "stationAddrTw": "台北市中正區北平西路3號", "haveBike": "Y"},
        {"stationCode": "1004", "stationName": "萬華站", "stationAddrTw": "台北市萬華區康定路382號", "haveBike": "Y"},
        {"stationCode": "1005", "stationName": "板橋站", "stationAddrTw": "新北市板橋區縣民大道二段7號", "haveBike": "Y"},
    ]

    analyzer.stations = sample_data
    for station in sample_data:
        city = analyzer.extract_city(station.get('stationAddrTw', ''))
        analyzer.city_stats[city] += 1

    # 顯示整體統計
    analyzer.show_overall_stats()

    # 生成特定城市報告
    cities_to_analyze = ["基隆市", "台北市", "新北市"]

    for city in cities_to_analyze:
        print(analyzer.generate_city_report(city))

        # 儲存篩選後的資料
        filename = f"{city}_stations.csv"
        analyzer.save_filtered_data(city, filename)

if __name__ == "__main__":
    main()
```

### 解析
- **物件導向設計**：使用類別封裝資料和方法，提高程式碼組織性
- **檔案處理**：使用 csv 模組處理 CSV 檔案讀寫
- **錯誤處理**：使用 try-except 處理檔案操作可能的錯誤
- **資料結構**：使用 defaultdict 進行統計，list 儲存資料
- **字串處理**：實現地址解析和資料篩選功能

---

## 最佳實踐建議

### 1. 程式碼風格
- 使用有意義的變數名稱
- 適當的註解和文件字串
- 遵循 PEP 8 編碼規範

### 2. 錯誤處理
- 使用 try-except 處理可能的例外
- 提供清晰的錯誤訊息
- 驗證輸入資料的有效性

### 3. 效能考量
- 對於大型資料集，考慮使用 pandas 進行資料處理
- 適當的資料結構選擇
- 避免不必要的重複計算

### 4. 安全性
- 使用參數化查詢防止 SQL 注入
- 驗證使用者輸入
- 適當的檔案權限設定

這些考題涵蓋了 Python 基礎語法、字串處理、檔案操作和物件導向程式設計，同時結合了您的 PostgreSQL 資料庫專案內容，希望對您的學習有所幫助！
