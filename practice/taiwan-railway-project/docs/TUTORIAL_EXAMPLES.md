# 台鐵車站資訊查詢系統 - 教學範例

## 目錄

1. [基礎概念](#基礎概念)
2. [資料模型使用](#資料模型使用)
3. [資料庫操作](#資料庫操作)
4. [GUI 元件開發](#gui-元件開發)
5. [非同步處理](#非同步處理)
6. [錯誤處理](#錯誤處理)
7. [快取機制](#快取機制)
8. [測試撰寫](#測試撰寫)
9. [擴展功能](#擴展功能)

## 基礎概念

### 專案架構理解

本專案採用分層架構，每一層都有明確的職責：

```python
# 範例：理解各層的職責

# 1. Model Layer - 資料模型
from taiwan_railway_gui.models.station import Station

# 建立車站物件
station = Station(
    station_code="1000",
    station_name="台北車站",
    address="台北市中正區北平西路3號",
    phone="02-2371-3558",
    gps_lat=25.0478,
    gps_lng=121.5170,
    has_bike_rental=True
)

# 2. DAO Layer - 資料存取
from taiwan_railway_gui.dao.station_dao import StationDAO

station_dao = StationDAO()
stations = station_dao.search_stations("台北")

# 3. Service Layer - 業務邏輯
from taiwan_railway_gui.services.validation import ValidationService

validator = ValidationService()
is_valid, message = validator.validate_station_code("1000")

# 4. GUI Layer - 使用者介面
from taiwan_railway_gui.gui.station_search_tab import StationSearchTab
```

### 設計模式應用

#### 1. 單例模式 (Singleton Pattern)

```python
# 資料庫管理器使用單例模式
from taiwan_railway_gui.dao.database_manager import get_database_manager

# 無論呼叫多少次，都會返回同一個實例
db1 = get_database_manager()
db2 = get_database_manager()
assert db1 is db2  # True
```

#### 2. 工廠模式 (Factory Pattern)

```python
# 建立不同類型的分頁
def create_tab(tab_type: str, parent, main_window):
    """工廠函數建立不同類型的分頁"""
    if tab_type == "station_search":
        from taiwan_railway_gui.gui.station_search_tab import create_station_search_tab
        return create_station_search_tab(parent, main_window)
    elif tab_type == "passenger_flow":
        from taiwan_railway_gui.gui.passenger_flow_tab import create_passenger_flow_tab
        return create_passenger_flow_tab(parent, main_window)
    # ... 其他分頁類型
```

#### 3. 觀察者模式 (Observer Pattern)

```python
# 錯誤處理器的回調機制
from taiwan_railway_gui.services.error_handler import get_error_handler, ErrorCategory

error_handler = get_error_handler()

def database_error_callback(error_info):
    """資料庫錯誤回調函數"""
    print(f"資料庫錯誤: {error_info.user_message}")

# 註冊觀察者
error_handler.register_error_callback(ErrorCategory.DATABASE, database_error_callback)
```

## 資料模型使用

### Station 模型範例

```python
from taiwan_railway_gui.models.station import Station, create_station_from_dict

# 1. 直接建立車站物件
station = Station(
    station_code="1000",
    station_name="台北車站",
    address="台北市中正區北平西路3號",
    phone="02-2371-3558",
    gps_lat=25.0478,
    gps_lng=121.5170,
    has_bike_rental=True
)

# 2. 從字典建立車站物件
station_data = {
    'station_code': '1001',
    'station_name': '台中車站',
    'address': '台中市中區台灣大道一段1號',
    'phone': '04-2220-6666',
    'gps_lat': 24.1369,
    'gps_lng': 120.6839,
    'has_bike_rental': False
}

station = create_station_from_dict(station_data)

# 3. 使用車站物件的方法
print(f"車站顯示名稱: {station.display_name}")
print(f"GPS 座標: {station.coordinates}")

# 4. 計算兩個車站之間的距離
taipei_station = Station(...)
taichung_station = Station(...)
distance = taipei_station.distance_to(taichung_station)
print(f"台北到台中距離: {distance:.2f} 公里")
```

### PassengerFlow 模型範例

```python
from taiwan_railway_gui.models.passenger_flow import PassengerFlow, StationStatistics
from datetime import date

# 1. 建立客流量資料
flow = PassengerFlow(
    station_code="1000",
    date=date(2024, 1, 15),
    in_passengers=50000,
    out_passengers=48000
)

print(f"總客流量: {flow.total_passengers}")
print(f"淨流入: {flow.net_flow}")

# 2. 建立統計資料
stats = StationStatistics(
    station_code="1000",
    station_name="台北車站",
    total_in=1500000,
    total_out=1480000,
    total_passengers=2980000,
    average_daily=96774.2,
    date_range=(date(2024, 1, 1), date(2024, 1, 31))
)

print(f"平均每日客流量: {stats.average_daily:.0f}")
print(f"客流量等級: {stats.traffic_level}")
```

## 資料庫操作

### 基本資料庫連線

```python
from taiwan_railway_gui.dao.database_manager import get_database_manager

# 取得資料庫管理器
db_manager = get_database_manager()

# 測試連線
if db_manager.test_connection():
    print("資料庫連線成功")
else:
    print("資料庫連線失敗")

# 使用連線上下文管理器
with db_manager.get_connection_context() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM stations")
        count = cursor.fetchone()
        print(f"車站總數: {count[0]}")
```

### StationDAO 使用範例

```python
from taiwan_railway_gui.dao.station_dao import StationDAO

# 建立 DAO 實例
station_dao = StationDAO()

# 1. 搜尋車站
stations = station_dao.search_stations("台北")
for station in stations:
    print(f"{station.station_name} ({station.station_code})")

# 2. 根據代碼取得車站
station = station_dao.get_station_by_code("1000")
if station:
    print(f"找到車站: {station.station_name}")

# 3. 取得所有車站
all_stations = station_dao.get_all_stations()
print(f"總共有 {len(all_stations)} 個車站")

# 4. 使用快取
# 第二次查詢會使用快取，速度更快
cached_stations = station_dao.search_stations("台北")
```

### PassengerFlowDAO 使用範例

```python
from taiwan_railway_gui.dao.passenger_flow_dao import PassengerFlowDAO
from datetime import date

# 建立 DAO 實例
flow_dao = PassengerFlowDAO()

# 1. 取得客流量資料
start_date = date(2024, 1, 1)
end_date = date(2024, 1, 31)
flows = flow_dao.get_passenger_flow("1000", start_date, end_date)

for flow in flows:
    print(f"{flow.date}: 進站 {flow.in_passengers}, 出站 {flow.out_passengers}")

# 2. 取得統計資料
stats = flow_dao.get_station_statistics("1000", start_date, end_date)
print(f"平均每日客流量: {stats.average_daily:.0f}")

# 3. 多車站統計比較
station_codes = ["1000", "1001", "1002"]
multi_stats = flow_dao.get_multiple_station_statistics(station_codes, start_date, end_date)

for stat in multi_stats:
    print(f"{stat.station_name}: {stat.total_passengers:,} 人次")
```

## GUI 元件開發

### 建立自訂分頁

```python
import tkinter as tk
from tkinter import ttk
from taiwan_railway_gui.gui.base_tab import BaseTab

class CustomTab(BaseTab):
    """自訂分頁範例"""

    def __init__(self, parent: tk.Widget, main_window=None):
        super().__init__(parent, main_window)
        self.setup_ui()
        self.setup_events()

    def setup_ui(self):
        """設定使用者介面"""
        # 建立主框架
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 建立標題
        title_label = ttk.Label(
            self.main_frame,
            text="自訂功能分頁",
            font=self.fonts['header']
        )
        title_label.pack(pady=(0, 20))

        # 建立輸入區域
        input_frame = ttk.LabelFrame(self.main_frame, text="輸入區域")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.input_entry = ttk.Entry(input_frame, width=30)
        self.input_entry.pack(side=tk.LEFT, padx=5, pady=5)

        self.search_button = ttk.Button(
            input_frame,
            text="搜尋",
            command=self.on_search
        )
        self.search_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 建立結果區域
        result_frame = ttk.LabelFrame(self.main_frame, text="結果區域")
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(result_frame, height=10)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.config(yscrollcommand=scrollbar.set)

        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_events(self):
        """設定事件處理"""
        # 綁定 Enter 鍵到搜尋功能
        self.input_entry.bind('<Return>', lambda e: self.on_search())

        # 綁定輸入變更事件
        self.input_entry.bind('<KeyRelease>', self.on_input_change)

    def on_search(self):
        """搜尋按鈕點擊事件"""
        query = self.input_entry.get().strip()
        if not query:
            self.show_warning("請輸入搜尋條件")
            return

        # 顯示載入狀態
        self.show_loading("搜尋中...")

        # 執行搜尋（這裡是範例）
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"搜尋結果: {query}\n")

        # 隱藏載入狀態
        self.hide_loading()

    def on_input_change(self, event):
        """輸入變更事件"""
        query = self.input_entry.get()
        # 可以在這裡實作即時搜尋
        pass

    def clear_data(self):
        """清除資料"""
        self.input_entry.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)

    def export_data(self):
        """匯出資料"""
        content = self.result_text.get(1.0, tk.END)
        if not content.strip():
            self.show_warning("沒有資料可匯出")
            return

        # 實作匯出邏輯
        self.show_success("資料匯出成功")
```

### 使用樣式管理器

```python
from taiwan_railway_gui.gui.styles import get_style_manager

# 取得樣式管理器
style_manager = get_style_manager()

# 取得主題配置
theme = style_manager.get_theme()
colors = theme['colors']
fonts = theme['fonts']

# 建立具有一致樣式的元件
label = tk.Label(
    parent,
    text="標題文字",
    foreground=colors['primary'],
    background=colors['background'],
    font=fonts['header']
)

# 套用焦點效果
style_manager.create_focus_effect(label)

# 套用懸停效果
style_manager.create_hover_effect(label, colors['accent'])
```

## 非同步處理

### 基本非同步任務

```python
from taiwan_railway_gui.services.async_manager import get_async_manager
import time

# 取得非同步管理器
async_manager = get_async_manager()

def long_running_task():
    """模擬長時間執行的任務"""
    time.sleep(5)  # 模擬資料庫查詢
    return "任務完成"

def on_success(result):
    """成功回調"""
    print(f"任務結果: {result}")

def on_error(error):
    """錯誤回調"""
    print(f"任務失敗: {error}")

def on_progress(progress, message):
    """進度回調"""
    print(f"進度: {progress}% - {message}")

# 提交任務
task_id = async_manager.submit_task(
    task_func=long_running_task,
    callback=on_success,
    error_callback=on_error,
    progress_callback=on_progress,
    task_name="資料查詢"
)

print(f"任務已提交: {task_id}")
```

### 帶進度更新的任務

```python
from taiwan_railway_gui.services.async_manager import create_progress_updater

def database_query_with_progress():
    """帶進度更新的資料庫查詢"""
    # 建立進度更新器
    update_progress = create_progress_updater("query_task")

    # 模擬查詢步驟
    steps = [
        "連接資料庫",
        "執行查詢",
        "處理結果",
        "格式化資料",
        "完成"
    ]

    results = []
    for i, step in enumerate(steps):
        update_progress((i + 1) / len(steps) * 100, step)
        time.sleep(1)  # 模擬處理時間
        results.append(f"步驟 {i+1} 完成")

    return results

# 提交帶進度的任務
task_id = async_manager.submit_task(
    task_func=database_query_with_progress,
    callback=lambda result: print("查詢完成:", result),
    progress_callback=lambda p, m: print(f"{p:.1f}% - {m}")
)
```

### GUI 中的非同步操作

```python
import tkinter as tk
from tkinter import ttk

class AsyncGUIExample:
    def __init__(self, parent):
        self.parent = parent
        self.async_manager = get_async_manager()
        self.setup_ui()

    def setup_ui(self):
        """設定介面"""
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.parent,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(pady=10)

        self.status_label = ttk.Label(self.parent, text="就緒")
        self.status_label.pack(pady=5)

        self.start_button = ttk.Button(
            self.parent,
            text="開始查詢",
            command=self.start_query
        )
        self.start_button.pack(pady=5)

    def start_query(self):
        """開始非同步查詢"""
        self.start_button.config(state='disabled')
        self.progress_var.set(0)
        self.status_label.config(text="查詢中...")

        def query_task():
            # 模擬資料庫查詢
            for i in range(100):
                time.sleep(0.05)
                # 在主執行緒中更新進度
                self.parent.after(0, lambda p=i+1: self.progress_var.set(p))
            return "查詢完成"

        def on_complete(result):
            self.status_label.config(text=result)
            self.start_button.config(state='normal')

        def on_error(error):
            self.status_label.config(text=f"錯誤: {error}")
            self.start_button.config(state='normal')

        self.async_manager.submit_task(
            task_func=query_task,
            callback=on_complete,
            error_callback=on_error
        )
```

## 錯誤處理

### 基本錯誤處理

```python
from taiwan_railway_gui.services.error_handler import get_error_handler, handle_error
from taiwan_railway_gui.services.error_handler import ErrorCategory, ErrorSeverity

# 取得錯誤處理器
error_handler = get_error_handler()

def risky_database_operation():
    """可能出錯的資料庫操作"""
    try:
        # 模擬資料庫操作
        result = perform_database_query()
        return result
    except ConnectionError as e:
        # 使用統一錯誤處理
        error_info = handle_error(
            error=e,
            context={'operation': 'database_query', 'table': 'stations'},
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH
        )
        # 錯誤已被處理，可以返回預設值或重新拋出
        return None
    except ValueError as e:
        # 處理驗證錯誤
        handle_error(
            error=e,
            context={'input_data': 'station_code'},
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW
        )
        return None
```

### 自訂錯誤回調

```python
def setup_error_callbacks():
    """設定錯誤回調"""
    error_handler = get_error_handler()

    def database_error_callback(error_info):
        """資料庫錯誤處理"""
        if error_info.severity == ErrorSeverity.CRITICAL:
            # 嚴重錯誤：顯示錯誤對話框並建議重啟
            show_critical_error_dialog(error_info)
        elif error_info.severity == ErrorSeverity.HIGH:
            # 高級錯誤：顯示錯誤訊息並提供重試選項
            show_error_with_retry(error_info)
        else:
            # 一般錯誤：在狀態列顯示
            show_status_message(error_info.user_message)

    def validation_error_callback(error_info):
        """驗證錯誤處理"""
        # 在相關輸旁顯示錯誤提示
        highlight_invalid_field(error_info.context.get('field_name'))
        show_field_error(error_info.user_message)

    # 註冊回調
    error_handler.register_error_callback(ErrorCategory.DATABASE, database_error_callback)
    error_handler.register_error_callback(ErrorCategory.VALIDATION, validation_error_callback)
```

### 錯誤恢復機制

```python
class ResilientDatabaseOperation:
    """具有錯誤恢復能力的資料庫操作"""

    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 1

    def execute_with_retry(self, operation, *args, **kwargs):
        """帶重試機制的操作執行"""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_error = e

                if attempt < self.max_retries - 1:
                    # 記錄重試
                    self.logger.warning(f"操作失敗，{self.retry_delay}秒後重試 (嘗試 {attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)

                    # 指數退避
                    self.retry_delay *= 2
                else:
                    # 最後一次嘗試失敗
                    handle_error(
                        error=e,
                        context={'attempts': self.max_retries, 'operation': operation.__name__},
                        category=ErrorCategory.DATABASE,
                        severity=ErrorSeverity.HIGH
                    )

        raise last_error

# 使用範例
resilient_op = ResilientDatabaseOperation()
result = resilient_op.execute_with_retry(database_query, "SELECT * FROM stations")
```

## 快取機制

### 基本快取使用

```python
from taiwan_railway_gui.services.cache_manager import get_cache_manager

# 取得快取管理器
cache_manager = get_cache_manager()

def get_station_data(station_code):
    """取得車站資料（帶快取）"""
    cache_key = f"station_{station_code}"

    # 嘗試從快取取得
    cached_data = cache_manager.get(cache_key)
    if cached_data is not None:
        print("從快取取得資料")
        return cached_data

    # 快取未命中，從資料庫查詢
    print("從資料庫查詢資料")
    station_data = query_database_for_station(station_code)

    # 儲存到快取（TTL 1小時）
    cache_manager.put(cache_key, station_data, ttl=3600)

    return station_data
```

### 快取裝飾器

```python
from functools import wraps

def cached(ttl=3600, key_func=None):
    """快取裝飾器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 產生快取鍵
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"

            # 檢查快取
            cache_manager = get_cache_manager()
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 執行函數
            result = func(*args, **kwargs)

            # 儲存到快取
            cache_manager.put(cache_key, result, ttl=ttl)

            return result
        return wrapper
    return decorator

# 使用範例
@cached(ttl=1800, key_func=lambda code: f"station_search_{code}")
def search_stations_cached(query):
    """帶快取的車站搜尋"""
    return expensive_database_search(query)
```

### 快取統計和管理

```python
def show_cache_statistics():
    """顯示快取統計資訊"""
    cache_manager = get_cache_manager()
    stats = cache_manager.get_stats()

    print("快取統計資訊:")
    print(f"  項目數: {stats['size']}/{stats['max_size']}")
    print(f"  記憶體使用: {stats['memory_usage_mb']:.1f} MB")
    print(f"  命中率: {stats['hit_rate']:.1%}")
    print(f"  命中次數: {stats['hits']}")
    print(f"  未命中次數: {stats['misses']}")

def clear_expired_cache():
    """清除過期快取"""
    cache_manager = get_cache_manager()
    cache_manager.cleanup_expired()
    print("已清除過期快取項目")

def warm_up_cache():
    """預熱快取"""
    print("正在預熱快取...")

    # 預載入常用資料
    common_stations = ["1000", "1001", "1002"]  # 熱門車站
    for station_code in common_stations:
        get_station_data(station_code)

    print("快取預熱完成")
```

## 測試撰寫

### 單元測試範例

```python
import pytest
from unittest.mock import Mock, patch
from taiwan_railway_gui.models.station import Station

class TestStation:
    """車站模型測試"""

    def test_station_creation(self):
        """測試車站建立"""
        station = Station(
            station_code="1000",
            station_name="台北車站",
            address="台北市中正區北平西路3號",
            phone="02-2371-3558",
            gps_lat=25.0478,
            gps_lng=121.5170,
            has_bike_rental=True
        )

        assert station.station_code == "1000"
        assert station.station_name == "台北車站"
        assert station.has_bike_rental is True

    def test_coordinates_property(self):
        """測試座標屬性"""
        station = Station(
            station_code="1000",
            station_name="台北車站",
            address="",
            phone="",
            gps_lat=25.0478,
            gps_lng=121.5170,
            has_bike_rental=False
        )

        coords = station.coordinates
        assert coords == (25.0478, 121.5170)

    def test_distance_calculation(self):
        """測試距離計算"""
        taipei = Station(
            station_code="1000", station_name="台北車站",
            address="", phone="",
            gps_lat=25.0478, gps_lng=121.5170,
            has_bike_rental=False
        )

        taichung = Station(
            station_code="1001", station_name="台中車站",
            address="", phone="",
            gps_lat=24.1369, gps_lng=120.6839,
            has_bike_rental=False
        )

        distance = taipei.distance_to(taichung)
        assert 150 < distance < 200  # 大約距離

    def test_invalid_coordinates(self):
        """測試無效座標"""
        with pytest.raises(ValueError, match="緯度超出台灣範圍"):
            Station(
                station_code="9999",
                station_name="無效車站",
                address="", phone="",
                gps_lat=50.0,  # 無效緯度
                gps_lng=121.5170,
                has_bike_rental=False
            )
```

### 整合測試範例

```python
import pytest
from taiwan_railway_gui.dao.station_dao import StationDAO
from taiwan_railway_gui.dao.database_manager import get_database_manager

class TestStationDAO:
    """車站 DAO 整合測試"""

    @pytest.fixture
    def station_dao(self):
        """建立 StationDAO 實例"""
        return StationDAO()

    @pytest.fixture
    def mock_database(self):
        """模擬資料庫"""
        with patch('taiwan_railway_gui.dao.database_manager.get_database_manager') as mock_db:
            mock_manager = Mock()
            mock_db.return_value = mock_manager

            # 模擬查詢結果
            mock_manager.execute_query.return_value = [
                {
                    'station_code': '1000',
                    'station_name': '台北車站',
                    'address': '台北市中正區北平西路3號',
                    'phone': '02-2371-3558',
                    'gps_lat': 25.0478,
                    'gps_lng': 121.5170,
                    'has_bike_rental': True
                }
            ]

            yield mock_manager

    def test_search_stations(self, station_dao, mock_database):
        """測試車站搜尋"""
        results = station_dao.search_stations("台北")

        assert len(results) == 1
        assert results[0].station_name == "台北車站"
        assert results[0].station_code == "1000"

        # 驗證資料庫查詢被呼叫
        mock_database.execute_query.assert_called_once()

    def test_get_station_by_code(self, station_dao, mock_database):
        """測試根據代碼取得車站"""
        station = station_dao.get_station_by_code("1000")

        assert station is not None
        assert station.station_code == "1000"
        assert station.station_name == "台北車站"

    def test_station_not_found(self, station_dao, mock_database):
        """測試車站不存在的情況"""
        mock_database.execute_query.return_value = []

        station = station_dao.get_station_by_code("9999")
        assert station is None
```

### GUI 測試範例

```python
import tkinter as tk
import pytest
from taiwan_railway_gui.gui.station_search_tab import StationSearchTab

class TestStationSearchTab:
    """車站搜尋分頁測試"""

    @pytest.fixture
    def root(self):
        """建立測試用的 Tkinter 根視窗"""
        root = tk.Tk()
        yield root
        root.destroy()

    @pytest.fixture
    def search_tab(self, root):
        """建立搜尋分頁實例"""
        return StationSearchTab(root)

    def test_initial_state(self, search_tab):
        """測試初始狀態"""
        assert search_tab.search_entry.get() == ""
        assert search_tab.results_listbox.size() == 0

    def test_search_input(self, search_tab):
        """測試搜尋輸入"""
        # 模擬使用者輸入
        search_tab.search_entry.insert(0, "台北")
        assert search_tab.search_entry.get() == "台北"

    @patch('taiwan_railway_gui.dao.station_dao.StationDAO.search_stations')
    def test_search_functionality(self, mock_search, search_tab):
        """測試搜尋功能"""
        # 設定模擬返回值
        mock_stations = [
            Mock(station_name="台北車站", station_code="1000"),
            Mock(station_name="台北橋車站", station_code="1001")
        ]
        mock_search.return_value = mock_stations

        # 執行搜尋
        search_tab.search_entry.insert(0, "台北")
        search_tab.on_search()

        # 驗證結果
        assert search_tab.results_listbox.size() == 2
        mock_search.assert_called_once_with("台北")

    def test_clear_functionality(self, search_tab):
        """測試清除功能"""
        # 先輸入一些資料
        search_tab.search_entry.insert(0, "測試")
        search_tab.results_listbox.insert(tk.END, "測試項目")

        # 執行清除
        search_tab.clear_data()

        # 驗證清除結果
        assert search_tab.search_entry.get() == ""
        assert search_tab.results_listbox.size() == 0
```

## 擴展功能

### 新增自訂分頁

```python
# 1. 建立新的分頁類別
from taiwan_railway_gui.gui.base_tab import BaseTab

class ReportTab(BaseTab):
    """報表分頁"""

    def __init__(self, parent, main_window=None):
        super().__init__(parent, main_window)
        self.setup_ui()

    def setup_ui(self):
        """設定使用者介面"""
        # 實作報表介面
        pass

    def generate_report(self):
        """生成報表"""
        # 實作報表生成邏輯
        pass

# 2. 在主視窗中註冊新分頁
def add_report_tab_to_main_window(main_window):
    """將報表分頁加入主視窗"""
    tab_frame = ttk.Frame(main_window.notebook)
    report_tab = ReportTab(tab_frame, main_window)

    main_window.notebook.add(tab_frame, text="報表")
    main_window.tabs['report'] = report_tab
```

### 新增資料匯出格式

```python
from taiwan_railway_gui.services.export_manager import ExportManager

class CustomExportManager(ExportManager):
    """自訂匯出管理器"""

    def export_to_excel(self, data, filename, headers=None):
        """匯出到 Excel 檔案"""
        try:
            import pandas as pd

            # 轉換資料為 DataFrame
            df = pd.DataFrame(data, columns=headers)

            # 匯出到 Excel
            df.to_excel(filename, index=False)

            return True
        except ImportError:
            raise ImportError("需要安裝 pandas 和 openpyxl 套件")
        except Exception as e:
            self.logger.error(f"Excel 匯出失敗: {e}")
            return False

    def export_to_json(self, data, filename):
        """匯出到 JSON 檔案"""
        import json

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"JSON 匯出失敗: {e}")
            return False
```

### 新增快取策略

```python
from taiwan_railway_gui.services.cache_manager import CacheManager

class SmartCacheManager(CacheManager):
    """智慧快取管理器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_patterns = {}  # 存取模式追蹤

    def get(self, key):
        """取得快取值（帶存取模式追蹤）"""
        result = super().get(key)

        # 記錄存取模式
        if key not in self.access_patterns:
            self.access_patterns[key] = {'count': 0, 'last_access': time.time()}

        self.access_patterns[key]['count'] += 1
        self.access_patterns[key]['last_access'] = time.time()

        return result

    def get_hot_keys(self, limit=10):
        """取得熱門快取鍵"""
        sorted_keys = sorted(
            self.access_patterns.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        return [key for key, _ in sorted_keys[:limit]]

    def preload_hot_data(self):
        """預載入熱門資料"""
        hot_keys = self.get_hot_keys()
        for key in hot_keys:
            if key not in self.cache:
                # 重新載入熱門資料
                self.reload_data(key)
```

### 新增通知系統

```python
import tkinter as tk
from tkinter import ttk
from enum import Enum

class NotificationType(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class NotificationSystem:
    """通知系統"""

    def __init__(self, parent):
        self.parent = parent
        self.notifications = []
        self.setup_notification_area()

    def setup_notification_area(self):
        """設定通知區域"""
        self.notification_frame = ttk.Frame(self.parent)
        self.notification_frame.pack(side=tk.TOP, fill=tk.X)

    def show_notification(self, message, notification_type=NotificationType.INFO, duration=3000):
        """顯示通知"""
        notification = self.create_notification(message, notification_type)
        self.notifications.append(notification)

        # 自動隱藏
        if duration > 0:
            self.parent.after(duration, lambda: self.hide_notification(notification))

    def create_notification(self, message, notification_type):
        """建立通知元件"""
        colors = {
            NotificationType.INFO: "#3498db",
            NotificationType.SUCCESS: "#2ecc71",
            NotificationType.WARNING: "#f39c12",
            NotificationType.ERROR: "#e74c3c"
        }

        notification_frame = ttk.Frame(self.notification_frame)
        notification_frame.pack(fill=tk.X, padx=5, pady=2)

        # 顏色指示器
        indicator = tk.Frame(
            notification_frame,
            bg=colors[notification_type],
            width=4
        )
        indicator.pack(side=tk.LEFT, fill=tk.Y)

        # 訊息標籤
        message_label = ttk.Label(
            notification_frame,
            text=message,
            wraplength=400
        )
        message_label.pack(side=tk.LEFT, padx=10, pady=5)

        # 關閉按鈕
        close_button = ttk.Button(
            notification_frame,
            text="×",
            width=3,
            command=lambda: self.hide_notification(notification_frame)
        )
        close_button.pack(side=tk.RIGHT, padx=5)

        return notification_frame

    def hide_notification(self, notification):
        """隱藏通知"""
        if notification in self.notifications:
            notification.destroy()
            self.notifications.remove(notification)

# 使用範例
notification_system = NotificationSystem(main_window)
notification_system.show_notification("資料載入完成", NotificationType.SUCCESS)
```

## 進階主題

### 效能最佳化技巧

#### 1. 資料庫查詢最佳化

```python
from taiwan_railway_gui.dao.passenger_flow_dao import PassengerFlowDAO
from taiwan_railway_gui.services.pagination_manager import get_pagination_manager

class OptimizedPassengerFlowDAO(PassengerFlowDAO):
    """最佳化的客流量 DAO"""

    def __init__(self):
        super().__init__()
        self.pagination_manager = get_pagination_manager()

    def get_passenger_flow_paginated(self, station_code, start_date, end_date,
                                   page=1, page_size=50):
        """分頁查詢客流量資料"""
        offset = (page - 1) * page_size

        # 使用 LIMIT 和 OFFSET 進行分頁
        sql_query = """
        SELECT station_code, date, in_passengers, out_passengers
        FROM passenger_flows
        WHERE station_code = %s
          AND date BETWEEN %s AND %s
        ORDER BY date
        LIMIT %s OFFSET %s
        """

        params = (station_code, start_date, end_date, page_size, offset)
        results = self.db_manager.execute_query(sql_query, params)

        # 同時取得總數
        count_query = """
        SELECT COUNT(*)
        FROM passenger_flows
        WHERE station_code = %s
          AND date BETWEEN %s AND %s
        """
        count_params = (station_code, start_date, end_date)
        total_count = self.db_manager.execute_query(count_query, count_params, fetch_one=True)[0]

        return {
            'data': [self._create_passenger_flow(row) for row in results],
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }

    def get_aggregated_statistics(self, station_codes, start_date, end_date):
        """聚合統計查詢"""
        # 使用 SQL 聚合函數提升效能
        placeholders = ','.join(['%s'] * len(station_codes))
        sql_query = f"""
        SELECT
            s.station_code,
            s.station_name,
            SUM(pf.in_passengers) as total_in,
            SUM(pf.out_passengers) as total_out,
            AVG(pf.in_passengers + pf.out_passengers) as avg_daily,
            COUNT(*) as data_points
        FROM stations s
        JOIN passenger_flows pf ON s.station_code = pf.station_code
        WHERE s.station_code IN ({placeholders})
          AND pf.date BETWEEN %s AND %s
        GROUP BY s.station_code, s.station_name
        ORDER BY total_in + total_out DESC
        """

        params = tuple(station_codes) + (start_date, end_date)
        results = self.db_manager.execute_query(sql_query, params)

        return [
            {
                'station_code': row[0],
                'station_name': row[1],
                'total_in': row[2],
                'total_out': row[3],
                'total_passengers': row[2] + row[3],
                'average_daily': float(row[4]),
                'data_points': row[5]
            }
            for row in results
        ]
```

#### 2. 記憶體管理最佳化

```python
from taiwan_railway_gui.utils.memory_manager import get_memory_manager
import gc
import weakref

class MemoryOptimizedComponent:
    """記憶體最佳化元件範例"""

    def __init__(self):
        self.memory_manager = get_memory_manager()
        self._data_cache = weakref.WeakValueDictionary()  # 使用弱引用
        self._large_objects = []

    def load_large_dataset(self, dataset_id):
        """載入大型資料集"""
        # 檢查記憶體使用量
        memory_info = self.memory_manager.get_memory_info()
        if memory_info.percent > 80:  # 記憶體使用超過 80%
            self.cleanup_memory()

        # 檢查是否已在快取中
        if dataset_id in self._data_cache:
            return self._data_cache[dataset_id]

        # 載入資料
        data = self._load_data_from_source(dataset_id)

        # 使用生成器處理大型資料
        processed_data = self._process_data_generator(data)

        # 儲存到弱引用快取
        self._data_cache[dataset_id] = processed_data

        return processed_data

    def _process_data_generator(self, raw_data):
        """使用生成器處理資料，節省記憶體"""
        for chunk in self._chunk_data(raw_data, chunk_size=1000):
            # 處理每個資料塊
            processed_chunk = self._process_chunk(chunk)
            yield processed_chunk

            # 定期檢查記憶體
            if len(self._large_objects) % 10 == 0:
                self._check_memory_pressure()

    def _chunk_data(self, data, chunk_size):
        """將資料分塊處理"""
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    def cleanup_memory(self):
        """清理記憶體"""
        # 清除大型物件
        self._large_objects.clear()

        # 清除快取
        self._data_cache.clear()

        # 強制垃圾回收
        gc.collect()

        self.logger.info("記憶體清理完成")

    def _check_memory_pressure(self):
        """檢查記憶體壓力"""
        memory_info = self.memory_manager.get_memory_info()
        if memory_info.percent > 85:
            self.cleanup_memory()
```

#### 3. GUI 效能最佳化

```python
import tkinter as tk
from tkinter import ttk

class VirtualizedListbox:
    """虛擬化清單框，處理大量資料"""

    def __init__(self, parent, data_source, item_height=20):
        self.parent = parent
        self.data_source = data_source
        self.item_height = item_height
        self.visible_items = 20  # 可見項目數
        self.scroll_position = 0

        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        """設定使用者介面"""
        # 建立主框架
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 建立畫布和捲軸
        self.canvas = tk.Canvas(self.main_frame, height=self.visible_items * self.item_height)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.on_scroll)
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 建立項目框架
        self.items_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(0, 0, anchor=tk.NW, window=self.items_frame)

        # 綁定事件
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

    def update_display(self):
        """更新顯示內容"""
        # 清除現有項目
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        # 計算可見範圍
        start_index = max(0, self.scroll_position)
        end_index = min(len(self.data_source), start_index + self.visible_items)

        # 只建立可見項目
        for i in range(start_index, end_index):
            item_data = self.data_source[i]
            self.create_item_widget(item_data, i - start_index)

        # 更新捲軸
        self.update_scrollbar()

    def create_item_widget(self, item_data, row):
        """建立項目元件"""
        item_frame = ttk.Frame(self.items_frame)
        item_frame.grid(row=row, column=0, sticky='ew', padx=2, pady=1)

        # 建立項目內容
        label = ttk.Label(item_frame, text=str(item_data))
        label.pack(side=tk.LEFT, padx=5)

    def on_scroll(self, *args):
        """捲軸滾動事件"""
        if args[0] == 'moveto':
            # 計算新的滾動位置
            fraction = float(args[1])
            max_scroll = max(0, len(self.data_source) - self.visible_items)
            self.scroll_position = int(fraction * max_scroll)
        elif args[0] == 'scroll':
            # 滾動指定步數
            steps = int(args[1])
            self.scroll_position += steps
            self.scroll_position = max(0, min(self.scroll_position,
                                            len(self.data_source) - self.visible_items))

        self.update_display()

    def on_mousewheel(self, event):
        """滑鼠滾輪事件"""
        steps = -1 if event.delta > 0 else 1
        self.scroll_position += steps
        self.scroll_position = max(0, min(self.scroll_position,
                                        len(self.data_source) - self.visible_items))
        self.update_display()

    def update_scrollbar(self):
        """更新捲軸"""
        if len(self.data_source) <= self.visible_items:
            self.scrollbar.set(0, 1)
        else:
            top = self.scroll_position / len(self.data_source)
            bottom = (self.scroll_position + self.visible_items) / len(self.data_source)
            self.scrollbar.set(top, bottom)
```

### 國際化支援

#### 1. 多語言支援架構

```python
import json
import os
from typing import Dict, Optional

class I18nManager:
    """國際化管理器"""

    def __init__(self, default_locale='zh_TW'):
        self.default_locale = default_locale
        self.current_locale = default_locale
        selfons = {}
        self.load_translations()

    def load_translations(self):
        """載入翻譯檔案"""
        translations_dir = os.path.join(os.path.dirname(__file__), 'translations')

        for filename in os.listdir(translations_dir):
            if filename.endswith('.json'):
                locale = filename[:-5]  # 移除 .json 副檔名
                filepath = os.path.join(translations_dir, filename)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.translations[locale] = json.load(f)
                except Exception as e:
                    print(f"載入翻譯檔案失敗 {filename}: {e}")

    def set_locale(self, locale: str):
        """設定語言環境"""
        if locale in self.translations:
            self.current_locale = locale
        else:
            print(f"不支援的語言環境: {locale}")

    def get_text(self, key: str, **kwargs) -> str:
        """取得翻譯文字"""
        # 嘗試從當前語言環境取得
        text = self._get_translation(self.current_locale, key)

        # 如果找不到，嘗試預設語言環境
        if text is None and self.current_locale != self.default_locale:
            text = self._get_translation(self.default_locale, key)

        # 如果還是找不到，返回鍵值
        if text is None:
            text = key

        # 格式化參數
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                print(f"翻譯參數錯誤 {key}: {e}")

        return text

    def _get_translation(self, locale: str, key: str) -> Optional[str]:
        """從指定語言環境取得翻譯"""
        if locale not in self.translations:
            return None

        # 支援巢狀鍵值 (例如: "menu.file.open")
        keys = key.split('.')
        current = self.translations[locale]

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current if isinstance(current, str) else None

# 全域實例
_i18n_manager = None

def get_i18n_manager() -> I18nManager:
    """取得國際化管理器單例"""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
    return _i18n_manager

def _(key: str, **kwargs) -> str:
    """翻譯函數的簡寫"""
    return get_i18n_manager().get_text(key, **kwargs)

# 使用範例
print(_("menu.file.open"))  # 輸出: "開啟檔案"
print(_("error.station_not_found", station="台北"))  # 輸出: "找不到車站: 台北"
```

#### 2. 翻譯檔案範例

```json
// translations/zh_TW.json
{
  "app": {
    "title": "台鐵車站資訊查詢系統",
    "version": "版本 {version}"
  },
  "menu": {
    "file": {
      "title": "檔案",
      "open": "開啟",
      "save": "儲存",
      "export": "匯出",
      "exit": "結束"
    },
    "view": {
      "title": "檢視",
      "refresh": "重新整理",
      "clear_cache": "清除快取"
    },
    "help": {
      "title": "說明",
      "about": "關於",
      "manual": "使用手冊"
    }
  },
  "tabs": {
    "station_search": "車站搜尋",
    "passenger_flow": "客流量查詢",
    "comparison": "車站比較",
    "charts": "圖表視覺化"
  },
  "buttons": {
    "search": "搜尋",
    "clear": "清除",
    "export": "匯出",
    "cancel": "取消",
    "ok": "確定"
  },
  "messages": {
    "loading": "載入中，請稍候...",
    "no_data": "沒有找到資料",
    "export_success": "匯出成功",
    "export_failed": "匯出失敗: {error}"
  },
  "errors": {
    "db_connection_failed": "資料庫連線失敗",
    "station_not_found": "找不到車站: {station}",
    "invalid_date_range": "日期範圍無效"
  }
}
```

```json
// translations/en_US.json
{
  "app": {
    "title": "Taiwan Railway Station Information System",
    "version": "Version {version}"
  },
  "menu": {
    "file": {
      "title": "File",
      "open": "Open",
      "save": "Save",
      "export": "Export",
      "exit": "Exit"
    },
    "view": {
      "title": "View",
      "refresh": "Refresh",
      "clear_cache": "Clear Cache"
    },
    "help": {
      "title": "Help",
      "about": "About",
      "manual": "User Manual"
    }
  },
  "tabs": {
    "station_search": "Station Search",
    "passenger_flow": "Passenger Flow",
    "comparison": "Station Comparison",
    "charts": "Chart Visualization"
  },
  "buttons": {
    "search": "Search",
    "clear": "Clear",
    "export": "Export",
    "cancel": "Cancel",
    "ok": "OK"
  },
  "messages": {
    "loading": "Loading, please wait...",
    "no_data": "No data found",
    "export_success": "Export successful",
    "export_failed": "Export failed: {error}"
  },
  "errors": {
    "db_connection_failed": "Database connection failed",
    "station_not_found": "Station not found: {station}",
    "invalid_date_range": "Invalid date range"
  }
}
```

### 外掛系統架構

#### 1. 外掛介面定義

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class PluginInterface(ABC):
    """外掛介面"""

    @property
    @abstractmethod
    def name(self) -> str:
        """外掛名稱"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """外掛版本"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """外掛描述"""
        pass

    @abstractmethod
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """初始化外掛"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """清理外掛資源"""
        pass

    def get_menu_items(self) -> List[Dict[str, Any]]:
        """取得選單項目"""
        return []

    def get_toolbar_items(self) -> List[Dict[str, Any]]:
        """取得工具列項目"""
        return []

class DataProcessorPlugin(PluginInterface):
    """資料處理外掛介面"""

    @abstractmethod
    def process_data(self, data: Any) -> Any:
        """處理資料"""
        pass

class ExportPlugin(PluginInterface):
    """匯出外掛介面"""

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """取得支援的格式"""
        pass

    @abstractmethod
    def export_data(self, data: Any, filename: str, format: str) -> bool:
        """匯出資料"""
        pass
```

#### 2. 外掛管理器

```python
import os
import importlib.util
import inspect
from typing import Dict, List, Type

class PluginManager:
    """外掛管理器"""

    def __init__(self, plugin_directory: str = "plugins"):
        self.plugin_directory = plugin_directory
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_classes: Dict[str, Type[PluginInterface]] = {}

    def discover_plugins(self):
        """發現外掛"""
        if not os.path.exists(self.plugin_directory):
            return

        for filename in os.listdir(self.plugin_directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                self._load_plugin_file(filename)

    def _load_plugin_file(self, filename: str):
        """載入外掛檔案"""
        filepath = os.path.join(self.plugin_directory, filename)
        module_name = filename[:-3]  # 移除 .py

        try:
            # 動態載入模組
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 尋找外掛類別
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, PluginInterface) and
                    obj != PluginInterface and
                    not inspect.isabstract(obj)):

                    self.plugin_classes[name] = obj
                    print(f"發現外掛類別: {name}")

        except Exception as e:
            print(f"載入外掛檔案失敗 {filename}: {e}")

    def load_plugin(self, plugin_name: str, app_context: Dict[str, Any]) -> bool:
        """載入外掛"""
        if plugin_name not in self.plugin_classes:
            print(f"找不到外掛: {plugin_name}")
            return False

        try:
            plugin_class = self.plugin_classes[plugin_name]
            plugin_instance = plugin_class()

            if plugin_instance.initialize(app_context):
                self.plugins[plugin_name] = plugin_instance
                print(f"外掛載入成功: {plugin_name}")
                return True
            else:
                print(f"外掛初始化失敗: {plugin_name}")
                return False

        except Exception as e:
            print(f"載入外掛失敗 {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str):
        """卸載外掛"""
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].cleanup()
                del self.plugins[plugin_name]
                print(f"外掛卸載成功: {plugin_name}")
            except Exception as e:
                print(f"卸載外掛失敗 {plugin_name}: {e}")

    def get_plugin(self, plugin_name: str) -> PluginInterface:
        """取得外掛實例"""
        return self.plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: Type[PluginInterface]) -> List[PluginInterface]:
        """根據類型取得外掛"""
        return [plugin for plugin in self.plugins.values()
                if isinstance(plugin, plugin_type)]

    def get_all_menu_items(self) -> List[Dict[str, Any]]:
        """取得所有外掛的選單項目"""
        menu_items = []
        for plugin in self.plugins.values():
            menu_items.extend(plugin.get_menu_items())
        return menu_items
```

#### 3. 範例外掛實作

```python
# plugins/excel_export_plugin.py
from taiwan_railway_gui.plugins.interfaces import ExportPlugin
import pandas as pd

class ExcelExportPlugin(ExportPlugin):
    """Excel 匯出外掛"""

    @property
    def name(self) -> str:
        return "Excel Export Plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "提供 Excel 格式的資料匯出功能"

    def initialize(self, app_context) -> bool:
        """初始化外掛"""
        try:
            import pandas as pd
            import openpyxl
            self.app_context = app_context
            return True
        except ImportError:
            print("Excel 外掛需要 pandas 和 openpyxl 套件")
            return False

    def cleanup(self):
        """清理資源"""
        pass

    def get_supported_formats(self) -> List[str]:
        """取得支援的格式"""
        return ['xlsx', 'xls']

    def export_data(self, data, filename: str, format: str) -> bool:
        """匯出資料到 Excel"""
        try:
            if isinstance(data, list) and len(data) > 0:
                # 轉換為 DataFrame
                df = pd.DataFrame(data)

                # 匯出到 Excel
                if format == 'xlsx':
                    df.to_excel(filename, index=False, engine='openpyxl')
                else:
                    df.to_excel(filename, index=False)

                return True
            else:
                print("沒有資料可匯出")
                return False

        except Exception as e:
            print(f"Excel 匯出失敗: {e}")
            return False

    def get_menu_items(self):
        """取得選單項目"""
        return [
            {
                'label': '匯出到 Excel',
                'command': self._show_export_dialog,
                'accelerator': 'Ctrl+E'
            }
        ]

    def _show_export_dialog(self):
        """顯示匯出對話框"""
        from tkinter import filedialog, messagebox

        filename = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel files', '*.xlsx'), ('All files', '*.*')]
        )

        if filename:
            # 取得當前資料
            current_data = self.app_context.get('current_data', [])
            if self.export_data(current_data, filename, 'xlsx'):
                messagebox.showinfo("匯出成功", f"資料已匯出到 {filename}")
            else:
                messagebox.showerror("匯出失敗", "無法匯出資料")
```

### 自動化測試進階技巧

#### 1. 資料驅動測試

```python
import pytest
from taiwan_railway_gui.models.station import Station

class TestStationValidation:
    """車站驗證測試"""

    # 測試資料
    valid_station_data = [
        {
            'station_code': '1000',
            'station_name': '台北車站',
            'gps_lat': 25.0478,
            'gps_lng': 121.5170,
            'expected': True
        },
        {
            'station_code': '1001',
            'station_name': '台中車站',
            'gps_lat': 24.1369,
            'gps_lng': 120.6839,
            'expected': True
        }
    ]

    invalid_station_data = [
        {
            'station_code': '',
            'station_name': '無效車站',
            'gps_lat': 25.0,
            'gps_lng': 121.0,
            'expected_error': 'ValueError'
        },
        {
            'station_code': '9999',
            'station_name': '超出範圍',
            'gps_lat': 50.0,  # 無效緯度
            'gps_lng': 121.0,
            'expected_error': 'ValueError'
        }
    ]

    @pytest.mark.parametrize("data", valid_station_data)
    def test_valid_station_creation(self, data):
        """測試有效車站建立"""
        station = Station(
            station_code=data['station_code'],
            station_name=data['station_name'],
            address="測試地址",
            phone="測試電話",
            gps_lat=data['gps_lat'],
            gps_lng=data['gps_lng'],
            has_bike_rental=False
        )

        assert station.station_code == data['station_code']
        assert station.station_name == data['station_name']

    @pytest.mark.parametrize("data", invalid_station_data)
    def test_invalid_station_creation(self, data):
        """測試無效車站建立"""
        with pytest.raises(ValueError):
            Station(
                station_code=data['station_code'],
                station_name=data['station_name'],
                address="測試地址",
                phone="測試電話",
                gps_lat=data['gps_lat'],
                gps_lng=data['gps_lng'],
                has_bike_rental=False
            )
```

#### 2. 效能測試

```python
import pytest
import time
from taiwan_railway_gui.dao.station_dao import StationDAO

class TestPerformance:
    """效能測試"""

    @pytest.fixture
    def station_dao(self):
        return StationDAO()

    def test_search_performance(self, station_dao):
        """測試搜尋效能"""
        start_time = time.time()

        # 執行搜尋
        results = station_dao.search_stations("台")

        end_time = time.time()
        execution_time = end_time - start_time

        # 驗證效能要求（例如：搜尋應在 1 秒內完成）
        assert execution_time < 1.0, f"搜尋時間過長: {execution_time:.2f}秒"
        assert len(results) > 0, "搜尋應該有結果"

    @pytest.mark.performance
    def test_large_dataset_handling(self, station_dao):
        """測試大型資料集處理"""
        # 模擬大量查詢
        queries = [f"query_{i}" for i in range(100)]

        start_time = time.time()

        for query in queries:
            station_dao.search_stations(query)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / len(queries)

        # 驗證平均查詢時間
        assert avg_time < 0.1, f"平均查詢時間過長: {avg_time:.3f}秒"

    def test_memory_usage(self, station_dao):
        """測試記憶體使用"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 執行記憶體密集操作
        for i in range(1000):
            station_dao.search_stations(f"test_{i}")

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # 驗證記憶體增長不超過 50MB
        assert memory_increase < 50 * 1024 * 1024, f"記憶體增長過多: {memory_increase / 1024 / 1024:.1f}MB"
```

---

這些進階範例展示了如何擴展和最佳化台鐵車站資訊查詢系統。包含效能最佳化、國際化支援、外掛系統架構和進階測試技巧，為開發者提供了完整的學習和實作參考。

**版本**: 1.0.0
**最後更新**: 2024年1月
**文件語言**: 繁體中文