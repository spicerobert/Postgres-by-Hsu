# 台鐵車站資訊查詢 GUI 應用程式

## 專案概述

這是一個基於 Python tkinter 的桌面 GUI 應用程式，用於查詢和分析台鐵車站資訊及進出站人數資料。此應用程式既是功能性工具，也是展示 GUI 開發和 PostgreSQL 資料庫整合的教學範例。

## 專案結構

```
taiwan_railway_gui/
├── __init__.py              # 套件初始化
├── config.py                # 應用程式配置
├── interfaces.py            # 核心介面定義
├── models/                  # 資料模型
│   └── __init__.py
├── dao/                     # 資料存取物件
│   └── __init__.py
├── gui/                     # 圖形使用者介面
│   └── __init__.py
├── services/                # 業務邏輯服務
│   └── __init__.py
└── utils/                   # 工具函數
    └── __init__.py
```

## 主要功能

1. **車站搜尋**: 搜尋和查看車站基本資訊
2. **客流量查詢**: 查詢特定車站的進出站人數統計
3. **車站比較**: 比較多個車站的客流量
4. **圖表視覺化**: 客流量資料的圖形化表示
5. **資料匯出**: 匯出查詢結果為 CSV 檔案

## 技術架構

- **前端**: Python tkinter + ttk
- **後端**: Python + psycopg2
- **視覺化**: matplotlib
- **資料庫**: PostgreSQL
- **架構模式**: 分層架構 + DAO 模式

## 安裝需求

- Python 3.8+
- PostgreSQL 資料庫
- 必要套件（見 requirements.txt）

## 使用方式

```bash
# 安裝依賴套件
pip install -r requirements.txt

# 執行應用程式
python main.py
```

## 開發指南

此專案遵循以下開發原則：

1. **模組化設計**: 清楚的模組分離和介面定義
2. **測試驅動**: 每個功能都有對應的單元測試
3. **程式碼品質**: 遵循 PEP 8 編碼規範
4. **教學導向**: 程式碼包含詳細註解和文件

## 授權

此專案僅供教學使用。