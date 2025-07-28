# 台鐵車站資訊查詢系統 - 程式碼文件

## 目錄

1. [程式碼規範](#程式碼規範)
2. [文件字串標準](#文件字串標準)
3. [註解規範](#註解規範)
4. [型別提示](#型別提示)
5. [錯誤處理](#錯誤處理)
6. [程式碼範例](#程式碼範例)
7. [最佳實踐](#最佳實踐)

## 程式碼規範

本專案遵循 PEP 8 編碼規範，並加入了一些專案特定的規範。

### 命名規範

#### 1. 類別命名 (PascalCase)

```python
class StationDAO:
    """車站資料存取物件"""
    pass

class PassengerFlowManager:
    """客流量管理器"""
    pass
```

#### 2. 函數和變數命名 (snake_case)

```python
def get_station_by_code(station_code: str) -> Optional[Station]:
    """根據代碼取得車站"""
    pass

def calculate_average_daily_flow(flows: List[PassengerFlow]) -> float:
    """計算平均每日客流量"""
    pass

# 變數命名
station_name = "台北車站"
passenger_count = 50000
is_weekend = True
```

#### 3. 常數命名 (UPPER_SNAKE_CASE)

```python
# config.py
MAX_COMPARISON_STATIONS = 5
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DATABASE_TIMEOUT_SECONDS = 30

# 錯誤訊息常數
ERROR_STATION_NOT_FOUND = "找不到指定的車站"
ERROR_INVALID_DATE_RANGE = "日期範圍無效"
```

#### 4. 私有成員命名

```python
class DatabaseManager:
    def __init__(self):
        self._connection_pool = None  # 受保護成員
        self.__secret_key = "secret"  # 私有成員

    def _initialize_pool(self):  # 受保護方法
        """初始化連線池"""
        pass

    def __validate_credentials(self):  # 私有方法
        """驗證憑證"""
        pass
```

### 程式碼結構

#### 1. 檔案結構

```python
"""
模組文件字串

簡短描述模組的功能和用途。
"""

# 標準函式庫匯入
import os
import sys
from datetime import date, datetime

# 第三方函式庫匯入
import psycopg2
import tkinter as tk
from tkinter import ttk

# 本地模組匯入
from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.dao.database_manager import get_database_manager

# 常數定義
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# 類別定義
class MyClass:
    pass

# 函數定義
def my_function():
    pass

# 主程式區塊
if __name__ == "__main__":
    main()
```

#### 2. 類別結構

```python
class StationDAO:
    """
    車站資料存取物件

    提供車站資料的查詢、新增、更新和刪除功能。
    """

    # 類別變數
    DEFAULT_CACHE_TTL = 3600

    def __init__(self, db_manager: DatabaseManager):
        """
        初始化車站 DAO

        Args:
            db_manager: 資料庫管理器實例
        """
        # 實例變數初始化
        self.db_manager = db_manager
        self.cache = {}
        self.logger = logging.getLogger(__name__)

    # 公開方法
    def search_stations(self, query: str) -> List[Station]:
        """搜尋車站"""
        pass

    # 受保護方法
    def _build_search_query(self, query: str) -> str:
        """建立搜尋查詢語句"""
        pass

    # 私有方法
    def __validate_query(self, query: str) -> bool:
        """驗證查詢參數"""
        pass

    # 屬性
    @property
    def cache_size(self) -> int:
        """取得快取大小"""
        return len(self.cache)

    # 特殊方法
    def __str__(self) -> str:
        """字串表示"""
        return f"StationDAO(cache_size={self.cache_size})"
```

## 文件字串標準

### 模組文件字串

```python
"""
車站資料存取模組

本模組提供車站資料的查詢和管理功能，包括：
- 車站搜尋
- 車站資訊查詢
- 車站資料快取

範例:
    from taiwan_railway_gui.dao.station_dao import StationDAO

    dao = StationDAO()
    stations = dao.search_stations("台北")

作者: Taiwan Railway GUI Team
版本: 1.0.0
"""
```

### 類別文件字串

```python
class StationDAO:
    """
    車站資料存取物件

    提供車站資料的查詢、新增、更新和刪除功能。
    支援快取機制以提升查詢效能。

    Attributes:
        db_manager (DatabaseManager): 資料庫管理器
        cache (dict): 查詢結果快取
        logger (Logger): 日誌記錄器

    Example:
        >>> dao = StationDAO(db_manager)
        >>> stations = dao.search_stations("台北")
        >>> print(len(stations))
        3

    Note:
        此類別使用單例模式，確保整個應用程式只有一個實例。
    """
```

### 函數文件字串

```python
def search_stations(self, query: str, limit: int = 100) -> List[Station]:
    """
    搜尋車站

    根據提供的查詢字串搜尋匹配的車站。支援車站名稱和代碼的模糊搜尋。

    Args:
        query (str): 搜尋查詢字串，可以是車站名稱或代碼的一部分
        limit (int, optional): 最大返回結果數量。預設為 100。

    Returns:
        List[Station]: 匹配的車站清單，按相關性排序

    Raises:
        ValueError: 當查詢字串為空或格式不正確時
        DatabaseError: 當資料庫查詢失敗時
        ConnectionError: 當資料庫連線失敗時

    Example:
        >>> stations = dao.search_stations("台北")
        >>> for station in stations:
        ...     print(station.station_name)
        台北車站
        台北橋車站

        >>> station = dao.search_stations("1000")[0]
        >>> print(station.station_name)
        台北車站

    Note:
        - 搜尋不區分大小寫
        - 結果會被快取以提升後續查詢效能
        - 查詢字串長度至少需要 2 個字元
    """
```

### 屬性文件字串

```python
@property
def total_passengers(self) -> int:
    """
    總乘客數

    計算進站和出站乘客的總數。

    Returns:
        int: 總乘客數（進站 + 出站）

    Example:
        >>> flow = PassengerFlow("1000", date.today(), 1000, 800)
        >>> print(flow.total_passengers)
        1800
    """
    return self.in_passengers + self.out_passengers
```

## 註解規範

### 1. 行內註解

```python
def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """計算兩點間的距離"""
    # 轉換為弧度
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)

    # 使用 Haversine 公式計算距離
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad

    a = (math.sin(dlat/2)**2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2)

    c = 2 * math.asin(math.sqrt(a))

    # 地球半徑（公里）
    earth_radius = 6371

    return earth_radius * c
```

### 2. 區塊註解

```python
def process_passenger_data(data: List[Dict]) -> List[PassengerFlow]:
    """處理客流量資料"""
    results = []

    # ==========================================
    # 第一階段：資料驗證和清理
    # ==========================================

    validated_data = []
    for record in data:
        # 檢查必要欄位
        if not all(key in record for key in ['station_code', 'date', 'in_passengers', 'out_passengers']):
            continue

        # 驗證資料格式
        try:
            station_code = str(record['station_code'])
            date_obj = datetime.strptime(record['date'], '%Y-%m-%d').date()
            in_passengers = int(record['in_passengers'])
            out_passengers = int(record['out_passengers'])
        except (ValueError, TypeError):
            continue

        validated_data.append({
            'station_code': station_code,
            'date': date_obj,
            'in_passengers': in_passengers,
            'out_passengers': out_passengers
        })

    # ==========================================
    # 第二階段：建立 PassengerFlow 物件
    # ==========================================

    for record in validated_data:
        try:
            flow = PassengerFlow(
                station_code=record['station_code'],
                date=record['date'],
                in_passengers=record['in_passengers'],
                out_passengers=record['out_passengers']
            )
            results.append(flow)
        except ValueError as e:
            # 記錄無效資料但繼續處理
            logging.warning(f"跳過無效資料: {record}, 錯誤: {e}")

    return results
```

### 3. TODO 和 FIXME 註解

```python
def advanced_search(self, query: str, filters: Dict[str, Any]) -> List[Station]:
    """進階搜尋功能"""
    # TODO: 實作地理位置篩選
    # TODO: 加入模糊搜尋評分機制
    # FIXME: 處理特殊字元的搜尋問題
    # HACK: 暫時使用簡單字串匹配，之後需要改用全文搜尋

    results = []

    # NOTE: 目前只支援基本的名稱搜尋
    for station in self.get_all_stations():
        if query.lower() in station.station_name.lower():
            results.append(station)

    # WARNING: 這個實作效能不佳，大量資料時會很慢
    return results
```

## 型別提示

### 1. 基本型別

```python
from typing import List, Dict, Optional, Union, Tuple, Any

def process_station_data(
    station_code: str,
    passenger_counts: List[int],
    metadata: Dict[str, Any],
    is_active: bool = True
) -> Optional[Station]:
    """處理車站資料"""
    pass
```

### 2. 複雜型別

```python
from typing import List, Dict, Optional, Union, Callable, TypeVar, Generic

# 型別變數
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# 泛型類別
class Cache(Generic[K, V]):
    """泛型快取類別"""

    def __init__(self) -> None:
        self._data: Dict[K, V] = {}

    def get(self, key: K) -> Optional[V]:
        """取得快取值"""
        return self._data.get(key)

    def put(self, key: K, value: V) -> None:
        """儲存快取值"""
        self._data[key] = value

# 回調函數型別
ErrorCallback = Callable[[Exception], None]
ProgressCallback = Callable[[float, str], None]

def async_operation(
    task: Callable[[], T],
    on_success: Optional[Callable[[T], None]] = None,
    on_error: Optional[ErrorCallback] = None,
    on_progress: Optional[ProgressCallback] = None
) -> str:
    """非同步操作"""
    pass
```

### 3. 協議和抽象基類

```python
from typing import Protocol
from abc import ABC, abstractmethod

class Drawable(Protocol):
    """可繪製物件協議"""

    def draw(self, canvas: Any) -> None:
        """繪製物件"""
        ...

class DataProcessor(ABC):
    """資料處理器抽象基類"""

    @abstractmethod
  def process(self, data: Any) -> Any:
        """處理資料"""
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """驗證資料"""
        pass
```

## 錯誤處理

### 1. 異常定義

```python
class TaiwanRailwayError(Exception):
    """台鐵系統基礎異常"""
    pass

class DatabaseError(TaiwanRailwayError):
    """資料庫相關異常"""

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code

class ValidationError(TaiwanRailwayError):
    """資料驗證異常"""

    def __init__(self, message: str, field_name: Optional[str] = None):
        super().__init__(message)
        self.field_name = field_name
```

### 2. 異常處理模式

```python
def get_station_by_code(self, station_code: str) -> Optional[Station]:
    """
    根據代碼取得車站

    Args:
        station_code: 車站代碼

    Returns:
        Station 物件或 None

    Raises:
        ValidationError: 當車站代碼格式不正確時
        DatabaseError: 當資料庫查詢失敗時
    """
    # 輸入驗證
    if not station_code or not isinstance(station_code, str):
        raise ValidationError("車站代碼不能為空且必須是字串", "station_code")

    if not station_code.isdigit():
        raise ValidationError("車站代碼格式不正確，應為數字", "station_code")

    try:
        # 資料庫查詢
        query = "SELECT * FROM stations WHERE station_code = %s"
        result = self.db_manager.execute_query(query, (station_code,), fetch_one=True)

        if result:
            return Station(**result)
        else:
            return None

    except psycopg2.Error as e:
        # 資料庫錯誤處理
        error_msg = f"查詢車站資料失敗: {e}"
        self.logger.error(error_msg)
        raise DatabaseError(error_msg, error_code=e.pgcode)

    except Exception as e:
        # 其他未預期的錯誤
        error_msg = f"取得車站資料時發生未知錯誤: {e}"
        self.logger.error(error_msg)
        raise TaiwanRailwayError(error_msg)
```

## 程式碼範例

### 1. 完整的類別範例

```python
"""
車站統計服務

提供車站相關的統計計算功能。
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import date, timedelta
from dataclasses import dataclass

from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow
from taiwan_railway_gui.dao.passenger_flow_dao import PassengerFlowDAO
from taiwan_railway_gui.services.cache_manager import get_cache_manager


@dataclass
class StationRanking:
    """車站排名資料"""
    station_code: str
    station_name: str
    total_passengers: int
    rank: int
    percentage: float


class StationStatisticsService:
    """
    車站統計服務

    提供車站客流量統計、排名和趨勢分析功能。

    Attributes:
        flow_dao (PassengerFlowDAO): 客流量資料存取物件
        cache_manager (CacheManager): 快取管理器
        logger (Logger): 日誌記錄器

    Example:
        >>> service = StationStatisticsService()
        >>> ranking = service.get_station_ranking(
        ...     date(2024, 1, 1),
        ...     date(2024, 1, 31)
        ... )
        >>> print(f"第一名: {ranking[0].station_name}")
    """

    def __init__(self, flow_dao: Optional[PassengerFlowDAO] = None):
        """
        初始化統計服務

        Args:
            flow_dao: 客流量資料存取物件，如果為 None 則建立新實例
        """
        self.flow_dao = flow_dao or PassengerFlowDAO()
        self.cache_manager = get_cache_manager()
        self.logger = logging.getLogger(__name__)

        # 統計設定
        self.default_cache_ttl = 3600  # 1小時
        self.max_ranking_size = 50

    def get_station_ranking(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> List[StationRanking]:
        """
        取得車站客流量排名

        計算指定日期範圍內各車站的總客流量並進行排名。

        Args:
            start_date: 開始日期
            end_date: 結束日期
            limit: 返回的排名數量，預設為 10

        Returns:
            List[StationRanking]: 車站排名清單，按客流量降序排列

        Raises:
            ValueError: 當日期範圍無效時
            DatabaseError: 當資料庫查詢失敗時

        Example:
            >>> ranking = service.get_station_ranking(
            ...     date(2024, 1, 1),
            ...     date(2024, 1, 31),
            ...     limit=5
            ... )
            >>> for rank in ranking:
            ...     print(f"{rank.rank}. {rank.station_name}: {rank.total_passengers:,}")
        """
        # 輸入驗證
        self._validate_date_range(start_date, end_date)

        if limit <= 0 or limit > self.max_ranking_size:
            raise ValueError(f"排名數量必須在 1 到 {self.max_ranking_size} 之間")

        # 檢查快取
        cache_key = f"ranking_{start_date}_{end_date}_{limit}"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result:
            self.logger.debug(f"從快取取得排名資料: {cache_key}")
            return cached_result

        try:
            # 查詢所有車站的統計資料
            self.logger.info(f"計算車站排名: {start_date} 到 {end_date}")

            all_stats = self.flow_dao.get_all_station_statistics(start_date, end_date)

            # 按總客流量排序
            sorted_stats = sorted(
                all_stats,
                key=lambda x: x.total_passengers,
                reverse=True
            )

            # 建立排名清單
            total_passengers_sum = sum(stat.total_passengers for stat in sorted_stats)
            rankings = []

            for i, stat in enumerate(sorted_stats[:limit], 1):
                percentage = (stat.total_passengers / total_passengers_sum * 100
                            if total_passengers_sum > 0 else 0)

                ranking = StationRanking(
                    station_code=stat.station_code,
                    station_name=stat.station_name,
                    total_passengers=stat.total_passengers,
                    rank=i,
                    percentage=percentage
                )
                rankings.append(ranking)

            # 儲存到快取
            self.cache_manager.put(cache_key, rankings, ttl=self.default_cache_ttl)

            self.logger.info(f"完成排名計算，共 {len(rankings)} 個車站")
            return rankings

        except Exception as e:
            self.logger.error(f"計算車站排名失敗: {e}")
            raise

    def get_trend_analysis(
        self,
        station_code: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, float]:
        """
        取得車站客流量趨勢分析

        分析指定車站在指定期間的客流量趨勢，包括成長率、波動性等指標。

        Args:
            station_code: 車站代碼
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            Dict[str, float]: 趨勢分析結果，包含以下鍵值：
                - growth_rate: 成長率（百分比）
                - volatility: 波動性
                - average_daily: 平均每日客流量
                - peak_day_passengers: 尖峰日客流量
                - low_day_passengers: 低峰日客流量

        Raises:
            ValueError: 當參數無效時
            DatabaseError: 當資料庫查詢失敗時
        """
        # 輸入驗證
        if not station_code:
            raise ValueError("車站代碼不能為空")

        self._validate_date_range(start_date, end_date)

        # 檢查快取
        cache_key = f"trend_{station_code}_{start_date}_{end_date}"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result

        try:
            # 取得客流量資料
            flows = self.flow_dao.get_passenger_flow(station_code, start_date, end_date)

            if not flows:
                raise ValueError(f"車站 {station_code} 在指定期間沒有資料")

            # 計算趨勢指標
            daily_totals = [flow.total_passengers for flow in flows]

            # 基本統計
            total_days = len(daily_totals)
            average_daily = sum(daily_totals) / total_days
            peak_day = max(daily_totals)
            low_day = min(daily_totals)

            # 成長率計算（比較前後期間）
            mid_point = total_days // 2
            first_half_avg = sum(daily_totals[:mid_point]) / mid_point
            second_half_avg = sum(daily_totals[mid_point:]) / (total_days - mid_point)

            growth_rate = ((second_half_avg - first_half_avg) / first_half_avg * 100
                          if first_half_avg > 0 else 0)

            # 波動性計算（標準差）
            variance = sum((x - average_daily) ** 2 for x in daily_totals) / total_days
            volatility = variance ** 0.5

            result = {
                'growth_rate': round(growth_rate, 2),
                'volatility': round(volatility, 2),
                'average_daily': round(average_daily, 2),
                'peak_day_passengers': peak_day,
                'low_day_passengers': low_day
            }

            # 儲存到快取
            self.cache_manager.put(cache_key, result, ttl=self.default_cache_ttl)

            return result

        except Exception as e:
            self.logger.error(f"趨勢分析失敗: {e}")
            raise

    def _validate_date_range(self, start_date: date, end_date: date) -> None:
        """
        驗證日期範圍

        Args:
            start_date: 開始日期
            end_date: 結束日期

        Raises:
            ValueError: 當日期範圍無效時
        """
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            raise ValueError("日期必須是 date 物件")

        if start_date > end_date:
            raise ValueError("開始日期不能晚於結束日期")

        if end_date > date.today():
            raise ValueError("結束日期不能是未來日期")

        # 檢查日期範圍是否過大（避免效能問題）
        max_days = 365
        if (end_date - start_date).days > max_days:
            raise ValueError(f"日期範圍不能超過 {max_days} 天")

    def clear_cache(self) -> None:
        """清除統計服務的快取"""
        # 這裡可以實作更精確的快取清理邏輯
        self.cache_manager.clear()
        self.logger.info("統計服務快取已清除")
```

## 最佳實踐

### 1. 程式碼組織

- **單一職責原則**: 每個類別和函數只負責一個明確的功能
- **開放封閉原則**: 對擴展開放，對修改封閉
- **依賴注入**: 通過建構函數注入依賴，便於測試和維護
- **介面隔離**: 定義清楚的介面，避免不必要的依賴

### 2. 效能考量

```python
# 好的做法：使用生成器處理大量資料
def process_large_dataset(data_source):
    """處理大型資料集"""
    for batch in data_source.get_batches(batch_size=1000):
        for item in batch:
            yield process_item(item)

# 避免：一次載入所有資料到記憶體
def process_large_dataset_bad(data_source):
    """不好的做法"""
    all_data = data_source.get_all_data()  # 可能消耗大量記憶體
    return [process_item(item) for item in all_data]
```

### 3. 錯誤處理

```python
# 好的做法：具體的異常處理
def get_station_data(station_code: str) -> Station:
    """取得車站資料"""
    try:
        return self.dao.get_station_by_code(station_code)
    except ValidationError:
        # 重新拋出驗證錯誤
        raise
    except DatabaseError as e:
        # 記錄資料庫錯誤並轉換為使用者友善的訊息
        self.logger.error(f"資料庫查詢失敗: {e}")
        raise TaiwanRailwayError("無法取得車站資料，請稍後再試")
    except Exception as e:
        # 處理未預期的錯誤
        self.logger.error(f"未知錯誤: {e}")
        raise TaiwanRailwayError("系統發生錯誤")

# 避免：過於寬泛的異常處理
def get_station_data_bad(station_code: str) -> Station:
    """不好的做法"""
    try:
        return self.dao.get_station_by_code(station_code)
    except Exception:
        return None  # 隱藏了所有錯誤資訊
```

### 4. 測試友善的設計

```python
class StationService:
    """車站服務"""

    def __init__(self, dao: StationDAO, validator: ValidationService):
        """依賴注入，便於測試"""
        self.dao = dao
        self.validator = validator

    def search_stations(self, query: str) -> List[Station]:
        """搜尋車站"""
        # 驗證輸入
        if not self.validator.validate_search_query(query):
            raise ValidationError("搜尋查詢格式不正確")

        # 執行搜尋
        return self.dao.search_stations(query)

# 測試範例
def test_search_stations():
    """測試車站搜尋"""
    # 建立模擬物件
    mock_dao = Mock()
    mock_validator = Mock()

    # 設定模擬行為
    mock_validator.validate_search_query.return_value = True
    mock_dao.search_stations.return_value = [Mock()]

    # 建立服務實例
    service = StationService(mock_dao, mock_validator)

    # 執行測試
    result = service.search_stations("台北")

    # 驗證結果
    assert len(result) == 1
    mock_validator.validate_search_query.assert_called_once_with("台北")
    mock_dao.search_stations.assert_called_once_with("台北")
```

---

**版本**: 1.0.0
**最後更新**: 2024年1月
**文件語言**: 繁體中文

這份文件提供了完整的程式碼文件標準和範例，幫助開發者撰寫高品質、易維護的程式碼。