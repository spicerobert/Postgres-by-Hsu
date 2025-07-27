# 設計文件 - 台鐵車站資訊查詢 GUI 應用程式

## 概述

本文件描述了一個基於 Python tkinter 建構的桌面 GUI 應用程式設計，提供直觀的介面用於查詢和分析台鐵車站資訊及進出站人數資料。此應用程式既是功能性工具，也是展示 GUI 開發和 PostgreSQL 資料庫整合的教學範例。

應用程式採用模組化架構，在使用者介面、業務邏輯和資料存取層之間有清楚的分離，使其適合教學用途，同時維持專業的開發實踐。

## 架構

### 高階架構

應用程式採用分層架構模式：

```
┌─────────────────────────────────────┐
│           GUI Layer (tkinter)        │
├─────────────────────────────────────┤
│         Business Logic Layer        │
├─────────────────────────────────────┤
│        Data Access Layer (DAO)      │
├─────────────────────────────────────┤
│       PostgreSQL Database           │
└─────────────────────────────────────┘
```

**設計理念**: 此分層方法確保關注點的清楚分離，使程式碼更易於維護和測試。同時也提供了良好的軟體架構教學範例。

### 技術堆疊

- **前端**: Python tkinter 搭配 ttk 現代化元件
- **後端**: Python 搭配 psycopg2 進行 PostgreSQL 連線
- **視覺化**: matplotlib 用於圖表生成
- **資料匯出**: Python csv 模組
- **資料庫**: PostgreSQL 搭配現有台鐵資料

**設計理念**: 選擇 tkinter 是因為其簡單性和 Python 內建可用性，非常適合教學用途。matplotlib 提供強大的圖表功能，同時保持簡單性。

## 元件與介面

### 1. 主應用程式視窗 (MainWindow)

**目的**: 協調所有應用程式功能的中央樞紐

**主要功能**:
- 不同功能區域的分頁介面
- 使用者回饋的狀態列
- 應用程式全域動作的選單列
- 資料庫操作的載入指示器

**介面設計**:
```
┌─────────────────────────────────────────────────────┐
│ File  View  Help                                    │
├─────────────────────────────────────────────────────┤
│ [Station Search] [Passenger Flow] [Comparison] [Charts] │
├─────────────────────────────────────────────────────┤
│                                                     │
│              Tab Content Area                       │
│                                                     │
├─────────────────────────────────────────────────────┤
│ Status: Ready                          [Progress]   │
└─────────────────────────────────────────────────────┘
```

### 2. 車站搜尋元件 (StationSearchTab)

**目的**: 處理車站資訊查詢和顯示

**主要功能**:
- 即時搜尋與自動完成
- 詳細車站資訊顯示
- 搜尋歷史功能

**介面元素**:
- 具驗證功能的搜尋輸入框
- 帶捲軸的結果清單框
- 顯示車站資訊的詳細面板
- 清除/重置功能

### 3. 客流量查詢元件 (PassengerFlowTab)

**目的**: 管理客流量資料查詢和統計

**主要功能**:
- 日期範圍選擇與日曆小工具
- 車站選擇下拉選單
- 統計摘要顯示
- 資料驗證和錯誤處理

**介面元素**:
- 車站選擇組合框
- 日期範圍選擇器（起始/結束日期）
- 帶載入狀態的查詢按鈕
- 具排序功能的結果表格
- 統計摘要面板

### 4. 車站比較元件 (ComparisonTab)

**目的**: 啟用多車站客流量比較

**主要功能**:
- 多車站選擇（最多5個）
- 比較統計顯示
- 排名功能

**介面元素**:
- 多選車站清單框
- 新增/移除車站按鈕
- 比較結果表格
- 帶視覺指示器的排名顯示

### 5. 圖表視覺化元件 (ChartTab)

**目的**: 提供客流量資料的圖形化表示

**主要功能**:
- 互動式圖表生成
- 多種圖表類型（線圖、長條圖）
- 圖表匯出功能
- 縮放和平移功能

**介面元素**:
- 圖表配置面板
- 嵌入式 matplotlib 畫布
- 圖表控制項（縮放、平移、重置）
- 帶格式選項的匯出按鈕

### 6. 資料匯出元件 (ExportManager)

**目的**: 處理所有元件的資料匯出功能

**主要功能**:
- 可自訂欄位的 CSV 匯出
- 檔案對話框整合
- 匯出進度追蹤
- 錯誤處理和使用者回饋

## 資料模型

### Station Model
```python
@dataclass
class Station:
    station_code: str
    station_name: str
    address: str
    phone: str
    gps_lat: float
    gps_lng: float
    has_bike_rental: bool
```

### Passenger Flow Model
```python
@dataclass
class PassengerFlow:
    station_code: str
    date: datetime.date
    in_passengers: int
    out_passengers: int

    @property
    def total_passengers(self) -> int:
        return self.in_passengers + self.out_passengers
```

### Query Result Models
```python
@dataclass
class StationStatistics:
    station_code: str
    station_name: str
    total_in: int
    total_out: int
    total_passengers: int
    average_daily: float
    date_range: tuple[datetime.date, datetime.date]

@dataclass
class ComparisonResult:
    stations: List[StationStatistics]
    ranking: List[tuple[str, int]]  # (station_name, total_passengers)
```

**設計理念**: 使用 dataclasses 提供乾淨、型別安全的資料模型，易於理解和維護。模型包含常用計算的計算屬性。

## 資料庫整合

### Database Access Object (DAO) Pattern

**StationDAO**:
- `search_stations(query: str) -> List[Station]`
- `get_station_by_code(code: str) -> Optional[Station]`
- `get_all_stations() -> List[Station]`

**PassengerFlowDAO**:
- `get_passenger_flow(station_code: str, start_date: date, end_date: date) -> List[PassengerFlow]`
- `get_station_statistics(station_code: str, start_date: date, end_date: date) -> StationStatistics`
- `get_multiple_station_statistics(station_codes: List[str], start_date: date, end_date: date) -> List[StationStatistics]`

### 連線管理

**DatabaseManager**:
- 連線池的單例模式
- 自動連線重試邏輯
- 交易管理
- 適當的資源清理

**設計理念**: DAO 模式抽象化資料庫操作，使程式碼更易於測試和維護。連線池提升效能和資源管理。

## 錯誤處理

### 錯誤類別

1. **資料庫錯誤**:
   - 連線失敗
   - 查詢逾時
   - 資料完整性問題

2. **使用者輸入錯誤**:
   - 無效的日期範圍
   - 不存在的車站代碼
   - 格式錯誤的搜尋查詢

3. **系統錯誤**:
   - 匯出時的檔案 I/O 錯誤
   - 大型資料集的記憶體問題
   - 圖表渲染失敗

### 錯誤處理策略

**使用者友善訊息**: 所有技術錯誤都會轉換為使用者友善的訊息，並提供建議的解決方案。

**優雅降級**: 在可能的情況下，應用程式會以降低的功能繼續運作，而不是當機。

**錯誤記錄**: 所有錯誤都會記錄以供除錯使用，同時向使用者顯示簡化的訊息。

**驗證**: 輸入驗證在多個層級進行：
- GUI 層級（即時回饋）
- 業務邏輯層級（資料一致性）
- 資料庫層級（資料完整性）

## 使用者介面設計

### 設計原則

1. **簡潔性**: 乾淨、不雜亂的介面，適合教學使用
2. **一致性**: 所有元件的統一樣式和行為
3. **回應性**: 對所有使用者動作提供即時回饋
4. **可存取性**: 清楚的標籤、邏輯分頁順序、鍵盤導航

### 視覺設計

**色彩配置**:
- 主色: 藍色 (#2E86AB) 用於標題和活動元素
- 次色: 灰色 (#F5F5F5) 用於背景
- 強調色: 綠色 (#28A745) 用於成功狀態
- 警告色: 橙色 (#FFC107) 用於警告
- 錯誤色: 紅色 (#DC3545) 用於錯誤

**字體設計**:
- 標題: 12pt 粗體
- 內文: 10pt 一般
- 等寬字體: 9pt 用於資料顯示

**版面配置**:
- 全程一致的 10px 內距
- 基於網格的對齊
- 具最小視窗尺寸的回應式調整

## 測試策略

### 單元測試

**測試元件**:
- 資料模型及其方法
- DAO 類別和資料庫操作
- 業務邏輯函數
- 工具函數

**測試框架**: Python unittest 搭配模擬物件進行資料庫操作

### 整合測試

**資料庫整合**:
- 測試實際資料庫連線
- 使用已知資料驗證查詢結果
- 測試交易處理

**GUI 整合**:
- 測試元件互動
- 驗證分頁間的資料流
- 測試 GUI 環境中的錯誤處理

### 使用者驗收測試

**測試情境**:
- 每個需求的完整使用者工作流程
- 錯誤條件處理
- 大型資料集的效能
- 跨平台相容性

**設計理念**: 全面的測試確保可靠性，並為教學使用提供信心。測試策略涵蓋應用程式的所有層級。

## 效能考量

### 資料庫最佳化

- **查詢最佳化**: 使用適當的索引和查詢模式
- **連線池**: 重複使用資料庫連線
- **延遲載入**: 僅在需要時載入資料
- **快取**: 快取經常存取的車站資料

### GUI 效能

- **非同步操作**: 使用執行緒進行資料庫操作以防止 GUI 凍結
- **漸進式載入**: 分塊載入大型資料集
- **記憶體管理**: 適當清理 matplotlib 圖形
- **回應式設計**: 為長時間操作顯示進度指示器

### 資料處理

- **分頁**: 限制大型查詢的結果集
- **資料驗證**: 在資料庫查詢前驗證輸入
- **記憶體效率**: 使用生成器處理大型資料

**設計理念**: 效能考量確保應用程式保持回應性和教學性，即使面對鐵路系統典型的大型資料集也是如此。