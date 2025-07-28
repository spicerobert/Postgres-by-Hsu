"""
核心介面定義

定義應用程式中各層之間的介面契約，確保系統邊界清楚分離。
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from taiwan_railway_gui.models.station import Station
    from taiwan_railway_gui.models.passenger_flow import PassengerFlow, StationStatistics


class DatabaseManagerInterface(ABC):
    """資料庫管理介面"""

    @abstractmethod
    def get_connection(self):
        """取得資料庫連線"""
        pass

    @abstractmethod
    def close_connection(self):
        """關閉資料庫連線"""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: tuple = None):
        """執行查詢"""
        pass


class StationDAOInterface(ABC):
    """車站資料存取介面"""

    @abstractmethod
    def search_stations(self, query: str) -> List['Station']:
        """搜尋車站"""
        pass

    @abstractmethod
    def get_station_by_code(self, code: str) -> Optional['Station']:
        """根據代碼取得車站"""
        pass

    @abstractmethod
    def get_all_stations(self) -> List['Station']:
        """取得所有車站"""
        pass


class PassengerFlowDAOInterface(ABC):
    """客流量資料存取介面"""

    @abstractmethod
    def get_passenger_flow(self, station_code: str, start_date: date, end_date: date) -> List['PassengerFlow']:
        """取得客流量資料"""
        pass

    @abstractmethod
    def get_station_statistics(self, station_code: str, start_date: date, end_date: date) -> 'StationStatistics':
        """取得車站統計資料"""
        pass

    @abstractmethod
    def get_multiple_station_statistics(self, station_codes: List[str], start_date: date, end_date: date) -> List['StationStatistics']:
        """取得多個車站統計資料"""
        pass


class ExportManagerInterface(ABC):
    """資料匯出管理介面"""

    @abstractmethod
    def export_to_csv(self, data: List, filename: str, headers: List[str]) -> bool:
        """匯出資料到 CSV 檔案"""
        pass

    @abstractmethod
    def export_chart(self, chart, filename: str, format: str = 'png') -> bool:
        """匯出圖表"""
        pass


class ValidationServiceInterface(ABC):
    """資料驗證服務介面"""

    @abstractmethod
    def validate_date_range(self, start_date: date, end_date: date) -> Tuple[bool, str]:
        """驗證日期範圍"""
        pass

    @abstractmethod
    def validate_station_code(self, station_code: str) -> Tuple[bool, str]:
        """驗證車站代碼"""
        pass

    @abstractmethod
    def validate_search_query(self, query: str) -> Tuple[bool, str]:
        """驗證搜尋查詢"""
        pass


class ErrorHandlerInterface(ABC):
    """錯誤處理服務介面"""

    @abstractmethod
    def handle_error(self, error: Exception, context: dict = None):
        """處理錯誤"""
        pass

    @abstractmethod
    def register_error_callback(self, category: str, callback):
        """註冊錯誤回調"""
        pass

    @abstractmethod
    def get_error_history(self, limit: int = 100):
        """取得錯誤歷史"""
        pass


class AsyncManagerInterface(ABC):
    """非同步管理器介面"""

    @abstractmethod
    def submit_task(self, task_func, callback=None, error_callback=None, progress_callback=None, task_name=None) -> str:
        """提交非同步任務"""
        pass

    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """取消任務"""
        pass

    @abstractmethod
    def get_task_status(self, task_id: str):
        """取得任務狀態"""
        pass

    @abstractmethod
    def wait_for_task(self, task_id: str, timeout=None):
        """等待任務完成"""
        pass


class CacheManagerInterface(ABC):
    """快取管理器介面"""

    @abstractmethod
    def get(self, key: str):
        """取得快取值"""
        pass

    @abstractmethod
    def put(self, key: str, value, ttl=None) -> bool:
        """儲存快取值"""
        pass

    @abstractmethod
    def remove(self, key: str) -> bool:
        """移除快取項目"""
        pass

    @abstractmethod
    def clear(self):
        """清除所有快取"""
        pass

    @abstractmethod
    def get_stats(self):
        """取得快取統計資訊"""
        pass


class PaginationManagerInterface(ABC):
    """分頁管理器介面"""

    @abstractmethod
    def paginate_data(self, data: List, page: int = 1, page_size: int = None):
        """對資料進行分頁"""
        pass

    @abstractmethod
    def paginate_query(self, query_func, page: int = 1, page_size: int = None, cache_key: str = None):
        """對查詢結果進行分頁"""
        pass

    @abstractmethod
    def clear_cache(self, cache_key: str = None):
        """清除分頁快取"""
        pass

    @abstractmethod
    def get_stats(self):
        """取得分頁統計資訊"""
        pass