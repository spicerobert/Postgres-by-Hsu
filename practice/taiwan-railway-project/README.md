# 台鐵車站資訊查詢系統

一個基於 Python tkinter 的桌面應用程式，提供直觀的圖形化介面來查詢和分析台鐵車站資訊及進出站人數資料。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## 📋 目錄

- [功能特色](#功能特色)
- [系統需求](#系統需求)
- [快速開始](#快速開始)
- [安裝指南](#安裝指南)
- [使用說明](#使用說明)
- [專案結構](#專案結構)
- [開發指南](#開發指南)
- [API 文件](#api-文件)
- [測試](#測試)
- [貢獻指南](#貢獻指南)
- [授權條款](#授權條款)
- [聯絡資訊](#聯絡資訊)

## ✨ 功能特色

### 🔍 車站搜尋
- 即時搜尋車站資訊
- 支援車站名稱和代碼查詢
- 顯示詳細車站資訊（地址、電話、GPS座標等）

### 📊 客流量查詢
- 查詢特定車站的進出站人數統計
- 支援日期範圍查詢
- 提供統計摘要（總進站、總出站、平均每日）

### 🔄 車站比較
- 同時比較多個車站的客流量（最多5個）
- 排名顯示和視覺指示器
- 支援多種比較指標

### 📈 圖表視覺化
- 客流量趨勢圖表
- 支援縮放、平移等互動操作
- 多種圖表格式匯出

### 💾 資料匯出
- CSV 格式資料匯出
- 圖表匯出（PNG、JPG、SVG）
- 自訂欄位選擇

### 🚀 效能最佳化
- 非同步資料庫查詢
- 智慧快取機制
- 記憶體管理和監控
- 分頁載入大型資料集

## 🔧 系統需求

### 最低需求
- **作業系統**: Windows 10, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **記憶體**: 4GB RAM
- **硬碟空間**: 500MB

### 建議需求
- **記憶體**: 8GB RAM 或更多
- **硬碟空間**: 1GB
- **顯示器**: 1920x1080 解析度

## 🚀 快速開始

### 1. 克隆專案

```bash
git clone https://github.com/your-repo/taiwan-railway-gui.git
cd taiwan-railway-gui
```

### 2. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 3. 設定資料庫連線

建立 `.env` 檔案或設定環境變數：

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=taiwan_railway
DB_USER=your_username
DB_PASSWORD=your_password
```

### 4. 啟動應用程式

```bash
python main.py
```

## 📖 安裝指南

詳細的安裝指南請參考：[安裝指南](docs/INSTALLATION_GUIDE.md)

## 📚 使用說明

完整的使用說明請參考：[使用者手冊](docs/USER_MANUAL.md)

### 基本操作

1. **車站搜尋**: 在搜尋框輸入車站名稱或代碼
2. **客流量查詢**: 選擇車站和日期範圍，點擊查詢
3. **車站比較**: 新增多個車站進行比較分析
4. **圖表視覺化**: 生成客流量趨勢圖表
5. **資料匯出**: 將結果匯出為 CSV 或圖片檔案

## 🏗️ 專案結構

```
taiwan_railway_gui/
├── __init__.py                 # 套件初始化
├── config.py                   # 應用程式配置
├── interfaces.py               # 介面定義
├── dao/                        # 資料存取層
│   ├── database_manager.py     # 資料庫管理
│   ├── station_dao.py          # 車站資料存取
│   └── passenger_flow_dao.py   # 客流量資料存取
├── models/                     # 資料模型
│   ├── station.py              # 車站模型
│   └── passenger_flow.py       # 客流量模型
├── services/                   # 服務層
│   ├── error_handler.py        # 錯誤處理
│   ├── async_manager.py        # 非同步管理
│   ├── cache_manager.py        # 快取管理
│   ├── validation.py           # 資料驗證
│   └── export_manager.py       # 資料匯出
├── gui/                        # GUI 層
│   ├── main_window.py          # 主視窗
│   ├── base_tab.py             # 分頁基礎類別
│   ├── station_search_tab.py   # 車站搜尋分頁
│   ├── passenger_flow_tab.py   # 客流量查詢分頁
│   ├── comparison_tab.py       # 車站比較分頁
│   └── chart_tab.py            # 圖表視覺化分頁
└── utils/                      # 工具模組
    ├── gui_helpers.py          # GUI 輔助函數
    └── memory_manager.py       # 記憶體管理
```

## 👨‍💻 開發指南

### 開發環境設定

```bash
# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安裝開發相依套件
pip install -r requirements-dev.txt

# 安裝 pre-commit hooks
pre-commit install
```

### 程式碼品質

```bash
# 程式碼格式化
black taiwan_railway_gui/

# 程式碼檢查
flake8 taiwan_railway_gui/

# 型別檢查
mypy taiwan_railway_gui/
```

詳細的開發指南請參考：[開發者指南](docs/DEVELOPER_GUIDE.md)

## 📖 API 文件

### 核心類別

#### Station 模型

```python
from taiwan_railway_gui.models.station import Station

station = Station(
    station_code="1000",
    station_name="台北車站",
    address="台北市中正區北平西路3號",
    phone="02-2371-3558",
    gps_lat=25.0478,
    gps_lng=121.5170,
    has_bike_rental=True
)

# 取得座標
coords = station.coordinates  # (25.0478, 121.5170)

# 計算距離
distance = station.distance_to(other_station)
```

#### 資料庫操作

```python
from taiwan_railway_gui.dao.station_dao import StationDAO

station_dao = StationDAO()

# 搜尋車站
stations = station_dao.search_stations("台北")

# 根據代碼取得車站
station = station_dao.get_station_by_code("1000")
```

更多 API 範例請參考：[教學範例](docs/TUTORIAL_EXAMPLES.md)

## 🧪 測試

### 執行測試

```bash
# 執行所有測試
pytest

# 執行特定測試檔案
pytest tests/unit/test_models.py

# 產生覆蓋率報告
pytest --cov=taiwan_railway_gui --cov-report=html
```

### 測試類型

- **單元測試**: 測試個別函數和類別
- **整合測試**: 測試元件間的互動
- **GUI 測試**: 測試使用者介面
- **端到端測試**: 測試完整的使用者工作流程

## 🤝 貢獻指南

我們歡迎任何形式的貢獻！

### 如何貢獻

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

### 程式碼規範

- 遵循 PEP 8 編碼規範
- 撰寫清楚的文件字串
- 包含適當的測試
- 確保所有測試通過

### 回報問題

使用 [GitHub Issues](https://github.com/your-repo/taiwan-railway-gui/issues) 回報問題時，請包含：

- 作業系統和版本
- Python 版本
- 詳細的錯誤訊息
- 重現步驟

## 📄 授權條款

本專案採用 MIT 授權條款。詳細內容請參考 [LICENSE](LICENSE) 檔案。

## 📞 聯絡資訊

- **專案維護者**: Taiwan Railway GUI Team
- **電子郵件**: support@taiwan-railway-gui.com
- **問題回報**: [GitHub Issues](https://github.com/your-repo/taiwan-railway-gui/issues)
- **功能建議**: [GitHub Discussions](https://github.com/your-repo/taiwan-railway-gui/discussions)

## 🙏 致謝

感謝所有為這個專案做出貢獻的開發者和使用者。

特別感謝：
- [psycopg2](https://pypi.org/project/psycopg2/) - PostgreSQL 資料庫連接器
- [matplotlib](https://matplotlib.org/) - 圖表視覺化函式庫
- [tkinter](https://docs.python.org/3/library/tkinter.html) - Python GUI 工具包

---

**版本**: 1.0.0
**最後更新**: 2024年1月
**文件語言**: 繁體中文
