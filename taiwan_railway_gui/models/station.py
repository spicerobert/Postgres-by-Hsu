"""
車站資料模型

定義車站相關的資料結構和驗證邏輯。
"""

from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class Station:
    """
    車站資料模型

    包含車站的基本資訊，包括代碼、名稱、地址、電話、GPS座標和自行車租借資訊。
    """
    station_code: str
    station_name: str
    address: str
    phone: str
    gps_lat: float
    gps_lng: float
    has_bike_rental: bool

    def __post_init__(self):
        """資料驗證和後處理"""
        self._validate_station_code()
        self._validate_station_name()
        self._validate_coordinates()
        self._validate_phone()

    def _validate_station_code(self):
        """驗證車站代碼格式"""
        if not self.station_code or not isinstance(self.station_code, str):
            raise ValueError("車站代碼不能為空且必須是字串")

        # 車站代碼通常是數字格式
        if not self.station_code.isdigit():
            raise ValueError("車站代碼格式不正確，應為數字")

    def _validate_station_name(self):
        """驗證車站名稱"""
        if not self.station_name or not isinstance(self.station_name, str):
            raise ValueError("車站名稱不能為空且必須是字串")

        if len(self.station_name.strip()) == 0:
            raise ValueError("車站名稱不能為空白")

    def _validate_coordinates(self):
        """驗證GPS座標"""
        # 台灣的經緯度範圍驗證
        if not isinstance(self.gps_lat, (int, float)):
            raise ValueError("緯度必須是數字")

        if not isinstance(self.gps_lng, (int, float)):
            raise ValueError("經度必須是數字")

        # 台灣緯度範圍約 21.9-25.3
        if not (21.0 <= self.gps_lat <= 26.0):
            raise ValueError("緯度超出台灣範圍")

        # 台灣經度範圍約 119.3-122.0
        if not (119.0 <= self.gps_lng <= 123.0):
            raise ValueError("經度超出台灣範圍")

    def _validate_phone(self):
        """驗證電話號碼格式"""
        if not isinstance(self.phone, str):
            raise ValueError("電話號碼必須是字串")

        # 允許空字串（某些車站可能沒有電話）
        if self.phone and not re.match(r'^[\d\-\(\)\s]+$', self.phone):
            raise ValueError("電話號碼格式不正確")

    @property
    def display_name(self) -> str:
        """取得顯示用的車站名稱（去除'站'字）"""
        return self.station_name.replace('站', '') if self.station_name.endswith('站') else self.station_name

    @property
    def coordinates(self) -> tuple[float, float]:
        """取得座標元組 (緯度, 經度)"""
        return (self.gps_lat, self.gps_lng)

    def distance_to(self, other_station: 'Station') -> float:
        """
        計算到另一個車站的直線距離（公里）
        使用 Haversine 公式
        """
        import math

        # 轉換為弧度
        lat1, lng1 = math.radians(self.gps_lat), math.radians(self.gps_lng)
        lat2, lng2 = math.radians(other_station.gps_lat), math.radians(other_station.gps_lng)

        # Haversine 公式
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # 地球半徑（公里）
        earth_radius = 6371
        return earth_radius * c

    def __str__(self) -> str:
        """字串表示"""
        return f"{self.station_name} ({self.station_code})"

    def __repr__(self) -> str:
        """詳細字串表示"""
        return (f"Station(code='{self.station_code}', name='{self.station_name}', "
                f"lat={self.gps_lat}, lng={self.gps_lng})")


def create_station_from_dict(data: dict) -> Station:
    """
    從字典建立 Station 物件

    Args:
        data: 包含車站資料的字典

    Returns:
        Station: 車站物件

    Raises:
        ValueError: 當資料格式不正確時
    """
    required_fields = ['station_code', 'station_name', 'address', 'phone',
                      'gps_lat', 'gps_lng', 'has_bike_rental']

    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必要欄位: {field}")

    return Station(
        station_code=str(data['station_code']),
        station_name=str(data['station_name']),
        address=str(data['address']),
        phone=str(data['phone']),
        gps_lat=float(data['gps_lat']),
        gps_lng=float(data['gps_lng']),
        has_bike_rental=bool(data['has_bike_rental'])
    )