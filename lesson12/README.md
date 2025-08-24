# 台鐵車站進出站人數視覺化分析系統

這是一個基於 Streamlit 的 Web 應用程式，用於分析和視覺化台鐵車站的進出站人數數據。系統連接 PostgreSQL 資料庫，提供互動式的資料查詢、圖表展示和統計分析功能。

## 功能特色

- 🚂 **台鐵車站資料分析**: 支援所有台鐵車站的進出站人數查詢
- 📊 **互動式圖表**: 美觀的進出站人數比較圖表，包含差異填充區域
- 📅 **彈性日期範圍**: 可自訂查詢的開始和結束日期
- 📈 **統計摘要**: 自動計算平均值、最大值、總計等關鍵指標
- 💾 **資料匯出**: 支援 CSV 格式下載查詢結果
- 🎯 **快速選擇**: 常用車站快速選擇功能

## 系統架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │───▶│   datasource    │───▶│   PostgreSQL    │
│   Web UI        │    │   模組          │    │   資料庫        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │
        ▼
┌─────────────────┐
│   matplotlib    │
│   圖表視覺化    │
└─────────────────┘
```

## 系統需求

本專案在 **conda pydev** 工作環境下執行，依賴套件請參考 `requirements.txt`：

```
psycopg2-binary
python-dotenv
streamlit
matplotlib
seaborn
numpy
```

### 安裝指令

```bash
# 啟用 conda 環境
conda activate pydev

# 安裝相依套件
pip install -r requirements.txt
```

## 檔案結構

```
lesson12/
├── main.py              # Streamlit 主應用程式
├── datasource.py        # 資料庫連接和查詢模組
├── requirements.txt     # Python 套件依賴清單
├── README.md           # 本說明文件
└── .env                # 環境變數配置檔 (需自行建立)
```

## 環境設定

建立 `.env` 檔案並設定資料庫連接參數：

```env
HOST=your_database_host
DATABASE=your_database_name
USER=your_database_user
PASSWORD=your_database_password
```

## 主要模組說明

### 1. main.py - Streamlit 主應用程式

**主要功能組件：**

#### 使用者介面
- **側邊欄控制台**: 車站選擇、日期範圍設定
- **快速選擇**: 常用車站 (臺北、桃園、新竹、台中、臺南、高雄)
- **資料顯示區**: 表格和圖表展示

#### 資料處理流程
```python
# 1. 取得車站清單和日期範圍
stations = get_stations()
date_range = get_date_range()

# 2. 查詢指定車站和日期的資料
data = datasource.get_station_data_by_date(station, start_date, end_date)

# 3. 轉換為 DataFrame 並設定欄位名稱
df = pd.DataFrame(data)
df.columns = ["日期", "車站", "進站人數", "出站人數"]
```

### 2. plot_entry_exit_chart() - 核心視覺化函數

**函數特色：**

```python
def plot_entry_exit_chart(df, station_name):
    """
    繪製進站人數與出站人數比較圖
    
    Parameters:
    -----------
    df : pandas.DataFrame
        包含日期、進站人數、出站人數的資料
    station_name : str
        車站名稱，用於圖表標題
        
    Returns:
    --------
    matplotlib.figure.Figure
        完整的圖表物件
    """
```

**視覺化特色：**
- **雙線圖**: 藍色線條代表進站人數，橘色線條代表出站人數
- **差異填充**: 自動填充進出站差異區域，直觀顯示流量差異
- **標記符號**: 圓點標記進站數據，方形標記出站數據
- **專業配色**: 使用 `#1f77b4` (藍) 和 `#ff7f0e` (橘) 的配色方案

### 3. datasource.py - 資料庫操作模組

**核心函數：**

#### `get_stations_names()`
- 取得所有台鐵車站名稱清單
- 回傳車站名稱的 Python 清單

#### `get_min_and_max_date()`
- 查詢資料庫中的最早和最晚日期
- 用於設定日期選擇器的範圍限制

#### `get_station_data_by_date(station_name, start_date, end_date)`
- 查詢指定車站在特定日期範圍內的進出站資料
- 回傳包含日期、車站、進站人數、出站人數的資料集

## 使用方式

### 1. 啟動應用程式

```bash
# 確認在 pydev 環境中
conda activate pydev

# 啟動 Streamlit 應用
streamlit run main.py
```

### 2. 操作流程

1. **選擇車站**: 使用快速選擇或下拉選單選擇目標車站
2. **設定日期**: 選擇查詢的開始和結束日期
3. **查看結果**: 系統自動顯示資料表格和視覺化圖表
4. **統計分析**: 查看自動計算的統計摘要
5. **匯出資料**: 點擊「下載 CSV」按鈕匯出資料

### 3. 圖表解讀

- **藍色線條與圓點**: 進站人數趨勢
- **橘色線條與方點**: 出站人數趨勢  
- **藍色填充區域**: 進站人數 > 出站人數的時段
- **橘色填充區域**: 出站人數 > 進站人數的時段

## 統計指標說明

系統自動計算並顯示以下統計指標：

| 指標 | 說明 |
|------|------|
| Average Entry Count | 平均進站人數 |
| Maximum Entry Count | 最大進站人數 |
| Average Exit Count | 平均出站人數 |
| Maximum Exit Count | 最大出站人數 |
| Total Entry Count | 總進站人數 |
| Total Exit Count | 總出站人數 |

## 技術特色

### 資料處理
- **智慧欄位偵測**: 自動識別日期、進站、出站欄位
- **容錯機制**: 支援多種資料格式和欄位命名方式
- **記憶體管理**: 自動釋放圖表記憶體，避免記憶體洩漏

### 效能最佳化
- **快取機制**: 使用 `@st.cache_data` 快取車站清單和日期範圍
- **條件渲染**: 只在有資料時才產生圖表，提升載入速度

### 使用者體驗
- **錯誤處理**: 完整的例外處理和使用者友善的錯誤訊息
- **響應式設計**: 支援不同螢幕尺寸的顯示效果
- **操作引導**: 清楚的標籤和說明文字

## 資料庫結構

應用程式需要以下資料表：

### 台鐵車站資訊表
```sql
CREATE TABLE "台鐵車站資訊" (
    "stationCode" VARCHAR,
    "stationName" VARCHAR
);
```

### 每日各站進出站人數表
```sql
CREATE TABLE "每日各站進出站人數" (
    "日期" DATE,
    "車站代碼" VARCHAR,
    "進站人數" INTEGER,
    "出站人數" INTEGER
);
```

## 故障排除

### 常見問題

1. **無法連接資料庫**
   - 檢查 `.env` 檔案是否正確設定
   - 確認資料庫伺服器是否正常運作
   - 驗證網路連接和防火牆設定

2. **圖表顯示異常**
   - 確認查詢日期範圍內有資料
   - 檢查資料中是否有 NULL 值或異常數據
   - 驗證資料類型是否正確

3. **套件相依性錯誤**
   - 確認已安裝所有 requirements.txt 中的套件
   - 檢查 Python 和套件版本相容性

### 除錯模式

在程式碼中加入除錯資訊：

```python
# 檢查資料結構
st.write("資料欄位:", df.columns.tolist())
st.write("資料形狀:", df.shape)
st.write("資料類型:", df.dtypes)

# 檢查資料內容
st.write("前 5 筆資料:")
st.write(df.head())
```

## 擴展功能建議

- 📊 **多車站比較**: 同時比較多個車站的進出站數據
- 📈 **趨勢分析**: 加入移動平均線和趨勢預測
- ⏰ **時段分析**: 分析尖峰和離峰時段的流量模式
- 📱 **行動裝置最佳化**: 改善手機和平板的顯示效果
- 🔄 **即時更新**: 加入資料自動更新機制
- 📋 **報表產生**: 自動產生分析報告和 PDF 輸出

## 開發環境

- **作業系統**: Debian GNU/Linux 12 (bookworm)
- **Python 環境**: conda pydev
- **開發容器**: Docker Dev Container
- **資料庫**: PostgreSQL
- **前端框架**: Streamlit
- **視覺化**: matplotlib + seaborn

## 授權聲明

本專案僅供教育和學習使用。使用的台鐵資料請遵循相關的資料使用規範。

---

**開發團隊**: GitHub Copilot 協助開發  
**最後更新**: 2025年8月24日
