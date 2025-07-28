"""
資料庫管理器

實作資料庫連線管理，包括連線池、重試邏輯和交易管理。
使用單例模式確保整個應用程式只有一個資料庫管理實例。
"""

import logging
import time
from typing import Optional, Any, Dict, List, Tuple
from contextlib import contextmanager
import threading
from taiwan_railway_gui.interfaces import DatabaseManagerInterface
from taiwan_railway_gui.config import get_config

try:
    import psycopg2
    from psycopg2 import pool, sql
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    pool = None
    sql = None
    RealDictCursor = None


class DatabaseManager(DatabaseManagerInterface):
    """
    資料庫管理器單例類別

    負責管理 PostgreSQL 資料庫連線，提供連線池、自動重試和交易管理功能。
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """單例模式實作"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化資料庫管理器"""
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.logger = logging.getLogger(__name__)
        self._connection_pool = None
        self._config = get_config('database')
        self._is_connected = False

        # 連線重試設定
        self._max_retries = 3
        self._retry_delay = 1  # 秒

        # 檢查 psycopg2 是否可用
        if psycopg2 is None:
            raise ImportError("psycopg2 套件未安裝，請執行: pip install psycopg2-binary")

    def initialize_connection_pool(self) -> bool:
        """
        初始化連線池

        Returns:
            bool: 初始化是否成功
        """
        try:
            if self._connection_pool is not None:
                self.logger.info("連線池已存在，跳過初始化")
                return True

            self.logger.info("正在初始化資料庫連線池...")

            # 建立連線池
            self._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=self._config['host'],
                port=self._config['port'],
                database=self._config['database'],
                user=self._config['user'],
                password=self._config['password'],
                cursor_factory=RealDictCursor
            )

            # 測試連線
            test_conn = self._connection_pool.getconn()
            if test_conn:
                test_conn.close()
                self._connection_pool.putconn(test_conn)
                self._is_connected = True
                self.logger.info("資料庫連線池初始化成功")
                return True

        except Exception as e:
            self.logger.error(f"資料庫連線池初始化失敗: {e}")
            self._is_connected = False
            return False

        return False

    def get_connection(self):
        """
        取得資料庫連線

        Returns:
            連線物件或 None
        """
        if not self._is_connected:
            if not self.initialize_connection_pool():
                return None

        try:
            if self._connection_pool:
                return self._connection_pool.getconn()
        except Exception as e:
            self.logger.error(f"取得資料庫連線失敗: {e}")
            return None

    def return_connection(self, connection):
        """
        歸還資料庫連線到連線池

        Args:
            connection: 要歸還的連線
        """
        if connection and self._connection_pool:
            try:
                self._connection_pool.putconn(connection)
            except Exception as e:
                self.logger.error(f"歸還資料庫連線失敗: {e}")

    def close_connection(self):
        """關閉所有資料庫連線"""
        if self._connection_pool:
            try:
                self._connection_pool.closeall()
                self._connection_pool = None
                self._is_connected = False
                self.logger.info("資料庫連線池已關閉")
            except Exception as e:
                self.logger.error(f"關閉資料庫連線池失敗: {e}")

    @contextmanager
    def get_connection_context(self):
        """
        連線上下文管理器

        使用方式:
            with db_manager.get_connection_context() as conn:
                # 使用連線
                pass
        """
        connection = None
        try:
            connection = self.get_connection()
            if connection is None:
                raise Exception("無法取得資料庫連線")
            yield connection
        finally:
            if connection:
                self.return_connection(connection)

    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False) -> Optional[Any]:
        """
        執行查詢

        Args:
            query: SQL 查詢語句
            params: 查詢參數
            fetch_one: 是否只取得一筆結果

        Returns:
            查詢結果或 None
        """
        for attempt in range(self._max_retries):
            try:
                with self.get_connection_context() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query, params)

                        if fetch_one:
                            return cursor.fetchone()
                        else:
                            return cursor.fetchall()

            except Exception as e:
                self.logger.warning(f"查詢執行失敗 (嘗試 {attempt + 1}/{self._max_retries}): {e}")

                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay)
                    # 重新初始化連線池
                    self._is_connected = False
                else:
                    self.logger.error(f"查詢執行最終失敗: {e}")
                    raise

        return None

    def execute_transaction(self, queries: List[Tuple[str, tuple]]) -> bool:
        """
        執行交易（多個查詢作為一個原子操作）

        Args:
            queries: 查詢列表，每個元素為 (query, params) 元組

        Returns:
            bool: 交易是否成功
        """
        for attempt in range(self._max_retries):
            try:
                with self.get_connection_context() as conn:
                    with conn.cursor() as cursor:
                        # 開始交易
                        for query, params in queries:
                            cursor.execute(query, params)

                        # 提交交易
                        conn.commit()
                        self.logger.info(f"交易執行成功，包含 {len(queries)} 個查詢")
                        return True

            except Exception as e:
                self.logger.warning(f"交易執行失敗 (嘗試 {attempt + 1}/{self._max_retries}): {e}")

                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay)
                    self._is_connected = False
                else:
                    self.logger.error(f"交易執行最終失敗: {e}")
                    return False

        return False

    def test_connection(self) -> bool:
        """
        測試資料庫連線

        Returns:
            bool: 連線是否正常
        """
        try:
            result = self.execute_query("SELECT 1 as test", fetch_one=True)
            return result is not None and result['test'] == 1
        except Exception as e:
            self.logger.error(f"資料庫連線測試失敗: {e}")
            return False

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        取得資料表資訊

        Args:
            table_name: 資料表名稱

        Returns:
            資料表欄位資訊列表
        """
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
        """

        try:
            return self.execute_query(query, (table_name,)) or []
        except Exception as e:
            self.logger.error(f"取得資料表資訊失敗: {e}")
            return []

    @property
    def is_connected(self) -> bool:
        """檢查是否已連線"""
        return self._is_connected and self.test_connection()

    def __del__(self):
        """析構函數，確保連線被正確關閉"""
        self.close_connection()


# 全域資料庫管理器實例
_db_manager = None
_db_lock = threading.Lock()


def get_database_manager() -> DatabaseManager:
    """
    取得資料庫管理器單例

    Returns:
        DatabaseManager: 資料庫管理器實例
    """
    global _db_manager

    if _db_manager is None:
        with _db_lock:
            if _db_manager is None:
                _db_manager = DatabaseManager()

    return _db_manager