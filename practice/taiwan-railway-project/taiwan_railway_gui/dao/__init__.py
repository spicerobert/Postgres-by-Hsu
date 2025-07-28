"""
資料存取物件 (DAO) 模組

包含所有資料庫存取相關的類別，實作 DAO 模式：
- DatabaseManager: 資料庫連線管理
- StationDAO: 車站資料存取
- PassengerFlowDAO: 客流量資料存取
"""

from .database_manager import DatabaseManager, get_database_manager
from .station_dao import StationDAO, create_station_dao
from .passenger_flow_dao import PassengerFlowDAO, create_passenger_flow_dao

__all__ = [
    'DatabaseManager',
    'get_database_manager',
    'StationDAO',
    'create_station_dao',
    'PassengerFlowDAO',
    'create_passenger_flow_dao'
]