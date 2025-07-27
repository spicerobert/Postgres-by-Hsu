"""
客流量資料模型

定義客流量相關的資料結構和統計計算。
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Tuple, Optional


@dataclass
class PassengerFlow:
    """
    客流量資料模型

    包含特定車站在特定日期的進出站人數資料。
    """
    station_code: str
    date: date
    in_passengers: int
    out_passengers: int

    def __post_init__(self):
        """資料驗證和後處理"""
        self._validate_station_code()
        self._validate_date()
        self._validate_passenger_counts()

    def _validate_station_code(self):
        """驗證車站代碼"""
        if not self.station_code or not isinstance(self.station_code, str):
            raise ValueError("車站代碼不能為空且必須是字串")

        if not self.station_code.isdigit():
            raise ValueError("車站代碼格式不正確，應為數字")

    def _validate_date(self):
        """驗證日期"""
        if not isinstance(self.date, date):
            raise ValueError("日期必須是 date 物件")

        # 檢查日期是否合理（不能是未來日期）
        if self.date > date.today():
            raise ValueError("日期不能是未來日期")

        # 檢查日期是否過於久遠（假設資料從2000年開始）
        if self.date < date(2000, 1, 1):
            raise ValueError("日期過於久遠")

    def _validate_passenger_counts(self):
        """驗證乘客數量"""
        if not isinstance(self.in_passengers, int) or self.in_passengers < 0:
            raise ValueError("進站人數必須是非負整數")

        if not isinstance(self.out_passengers, int) or self.out_passengers < 0:
            raise ValueError("出站人數必須是非負整數")

        # 檢查是否有異常高的數值（可能是資料錯誤）
        max_reasonable_count = 100000  # 單日最大合理人數
        if self.in_passengers > max_reasonable_count:
            raise ValueError(f"進站人數異常高: {self.in_passengers}")

        if self.out_passengers > max_reasonable_count:
            raise ValueError(f"出站人數異常高: {self.out_passengers}")

    @property
    def total_passengers(self) -> int:
        """總乘客數（進站 + 出站）"""
        return self.in_passengers + self.out_passengers

    @property
    def net_flow(self) -> int:
        """淨流量（進站 - 出站）"""
        return self.in_passengers - self.out_passengers

    @property
    def date_str(self) -> str:
        """日期字串表示"""
        return self.date.strftime('%Y-%m-%d')

    @property
    def weekday(self) -> int:
        """星期幾（0=星期一, 6=星期日）"""
        return self.date.weekday()

    @property
    def is_weekend(self) -> bool:
        """是否為週末"""
        return self.weekday >= 5

    def __str__(self) -> str:
        """字串表示"""
        return f"{self.date_str} - 進站: {self.in_passengers}, 出站: {self.out_passengers}"

    def __repr__(self) -> str:
        """詳細字串表示"""
        return (f"PassengerFlow(station='{self.station_code}', date='{self.date_str}', "
                f"in={self.in_passengers}, out={self.out_passengers})")


@dataclass
class StationStatistics:
    """
    車站統計資料模型

    包含特定車站在特定時間範圍內的統計資訊。
    """
    station_code: str
    station_name: str
    total_in: int
    total_out: int
    total_passengers: int
    average_daily: float
    date_range: Tuple[date, date]

    def __post_init__(self):
        """資料驗證和後處理"""
        self._validate_data()

    def _validate_data(self):
        """驗證統計資料"""
        if not self.station_code or not isinstance(self.station_code, str):
            raise ValueError("車站代碼不能為空")

        if not self.station_name or not isinstance(self.station_name, str):
            raise ValueError("車站名稱不能為空")

        if any(count < 0 for count in [self.total_in, self.total_out, self.total_passengers]):
            raise ValueError("乘客數量不能為負數")

        if self.average_daily < 0:
            raise ValueError("平均每日人數不能為負數")

        if not isinstance(self.date_range, tuple) or len(self.date_range) != 2:
            raise ValueError("日期範圍必須是包含兩個日期的元組")

        start_date, end_date = self.date_range
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            raise ValueError("日期範圍必須包含有效的日期物件")

        if start_date > end_date:
            raise ValueError("開始日期不能晚於結束日期")

    @property
    def days_count(self) -> int:
        """統計期間的天數"""
        return (self.date_range[1] - self.date_range[0]).days + 1

    @property
    def net_flow(self) -> int:
        """淨流量（總進站 - 總出站）"""
        return self.total_in - self.total_out

    @property
    def date_range_str(self) -> str:
        """日期範圍字串表示"""
        start_str = self.date_range[0].strftime('%Y-%m-%d')
        end_str = self.date_range[1].strftime('%Y-%m-%d')
        return f"{start_str} ~ {end_str}"

    def __str__(self) -> str:
        """字串表示"""
        return f"{self.station_name} ({self.date_range_str}): 總人數 {self.total_passengers:,}"


@dataclass
class ComparisonResult:
    """
    比較結果模型

    包含多個車站的比較統計資料和排名。
    """
    stations: List[StationStatistics]
    ranking: List[Tuple[str, int]]  # (station_name, total_passengers)

    def __post_init__(self):
        """資料驗證和後處理"""
        self._validate_data()
        self._update_ranking()

    def _validate_data(self):
        """驗證比較資料"""
        if not isinstance(self.stations, list):
            raise ValueError("車站列表必須是 list 類型")

        if len(self.stations) == 0:
            raise ValueError("車站列表不能為空")

        if len(self.stations) > 5:
            raise ValueError("最多只能比較 5 個車站")

        for station in self.stations:
            if not isinstance(station, StationStatistics):
                raise ValueError("車站資料必須是 StationStatistics 類型")

    def _update_ranking(self):
        """更新排名"""
        self.ranking = sorted(
            [(station.station_name, station.total_passengers) for station in self.stations],
            key=lambda x: x[1],
            reverse=True
        )

    @property
    def top_station(self) -> Optional[StationStatistics]:
        """排名第一的車站"""
        return self.stations[0] if self.stations else None

    @property
    def total_passengers_all(self) -> int:
        """所有車站的總乘客數"""
        return sum(station.total_passengers for station in self.stations)

    def get_station_rank(self, station_name: str) -> Optional[int]:
        """取得指定車站的排名（1-based）"""
        for i, (name, _) in enumerate(self.ranking):
            if name == station_name:
                return i + 1
        return None


def create_passenger_flow_from_dict(data: dict) -> PassengerFlow:
    """
    從字典建立 PassengerFlow 物件

    Args:
        data: 包含客流量資料的字典

    Returns:
        PassengerFlow: 客流量物件
    """
    required_fields = ['station_code', 'date', 'in_passengers', 'out_passengers']

    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必要欄位: {field}")

    # 處理日期格式
    flow_date = data['date']
    if isinstance(flow_date, str):
        flow_date = datetime.strptime(flow_date, '%Y-%m-%d').date()
    elif isinstance(flow_date, datetime):
        flow_date = flow_date.date()

    return PassengerFlow(
        station_code=str(data['station_code']),
        date=flow_date,
        in_passengers=int(data['in_passengers']),
        out_passengers=int(data['out_passengers'])
    )


def calculate_statistics(flows: List[PassengerFlow], station_name: str) -> StationStatistics:
    """
    從客流量資料計算統計資訊

    Args:
        flows: 客流量資料列表
        station_name: 車站名稱

    Returns:
        StationStatistics: 統計資料
    """
    if not flows:
        raise ValueError("客流量資料不能為空")

    station_code = flows[0].station_code
    total_in = sum(flow.in_passengers for flow in flows)
    total_out = sum(flow.out_passengers for flow in flows)
    total_passengers = total_in + total_out

    dates = [flow.date for flow in flows]
    date_range = (min(dates), max(dates))
    days_count = (date_range[1] - date_range[0]).days + 1
    average_daily = total_passengers / days_count if days_count > 0 else 0

    return StationStatistics(
        station_code=station_code,
        station_name=station_name,
        total_in=total_in,
        total_out=total_out,
        total_passengers=total_passengers,
        average_daily=round(average_daily, 2),
        date_range=date_range
    )