# 台鐵車站資訊查詢系統 - 完整專案

## 專案概述

這是一個完整的台鐵車站資訊查詢系統，使用 Python 和 Tkinter 開發，提供車站搜尋、客流量查詢、車站比較和圖表視覺化功能。

## 專案結構

```
taiwan-railway-project/
├── taiwan_railway_gui/          # 主要應用程式碼
│   ├── dao/                     # 資料存取層
│   ├── gui/                     # 圖形使用者介面
│   ├── models/                  # 資料模型
│   ├── services/                # 服務層
│   ├── utils/                   # 工具函數
│   ├── config.py                # 配置檔案
│   └── interfaces.py            # 介面定義
├── tests/                       # 測試檔案
│   ├── test_integration_comprehensive.py  # 綜合整合測試
│   ├── test_integration_database.py       # 資料庫整合測試
│   ├── test_integration_gui.py            # GUI整合測試
│   ├── test_integration_end_to_end.py     # 端到端測試
│   ├── run_integration_tests.py           # 整合測試執行器
│   └── 其他單元測試檔案...
├── .kiro/                       # Kiro IDE 配置和規格
│   └── specs/taiwan-railway-gui/  # 專案規格文件
├── main.py                      # 主程式入口
├── requirements.txt             # Python 依賴套件
├── README.md                    # 專案說明
└── 各種測試檔案...
```

## 主要功能

### 1. 車站搜尋功能
- 支援車站名稱模糊搜尋
- 顯示車站詳細資訊（地址、電話、GPS座標）
- 車站列表瀏覽

### 2. 客流量查詢
- 按車站和日期範圍查詢客流量
- 顯示進站、出站和總人數統計
- 支援資料匯出功能

### 3. 車站比較
- 多車站客流量比較
- 排名和統計分析
- 視覺化比較結果

### 4. 圖表視覺化
- 客流量趨勢圖表
- 多種圖表類型支援
- 圖表匯出功能

## 技術特色

### 架構設計
- **MVC 架構**：清楚分離模型、視圖和控制器
- **DAO 模式**：資料存取層抽象化
- **服務層**：業務邏輯封裝
- **介面導向**：使用抽象介面提高可測試性

### 資料庫整合
- PostgreSQL 主資料庫支援
- SQLite 測試資料庫
- 連線池管理
- 交易處理

### GUI 設計
- Tkinter 現代化介面
- 響應式設計
- 一致的視覺風格
- 使用者友善的操作流程

### 測試覆蓋
- **單元測試**：各模組獨立測試
- **整合測試**：系統整合驗證
- **端到端測試**：完整使用者流程測試
- **效能測試**：大型資料集處理測試

## 安裝和執行

### 1. 環境需求
```bash
Python 3.8+
PostgreSQL (可選，用於生產環境)
```

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 執行應用程式
```bash
python main.py
```

### 4. 執行測試
```bash
# 執行所有測試
python run_tests.py

# 執行整合測試
python tests/run_integration_tests.py

# 執行特定類別的整合測試
python tests/run_integration_tests.py --category comprehensive
```

## 測試說明

### 整合測試類別

1. **Simple Tests** (`--category simple`)
   - 基本模組整合測試
   - 模型驗證測試
   - 配置和服務測試

2. **Database Tests** (`--category database`)
   - 資料庫連線測試
   - DAO 層整合測試
   - 資料完整性測試

3. **GUI Tests** (`--category gui`)
   - GUI 元件互動測試
   - 使用者介面測試
   - 跨分頁整合測試

4. **End-to-End Tests** (`--category e2e`)
   - 完整使用者工作流程測試
   - 錯誤處理測試
   - 效能測試

5. **Comprehensive Tests** (`--category comprehensive`)
   - 綜合整合測試
   - 涵蓋所有主要功能
   - 資料庫、模型、服務層整合

### 測試執行範例

```bash
# 執行綜合整合測試（推薦）
python tests/run_integration_tests.py --category comprehensive

# 執行所有整合測試
python tests/run_integration_tests.py --category all

# 顯示詳細輸出
python tests/run_integration_tests.py --category comprehensive --verbose
```

## 開發文件

### 規格文件
- `.kiro/specs/taiwan-railway-gui/requirements.md` - 需求規格
- `.kiro/specs/taiwan-railway-gui/design.md` - 設計文件
- `.kiro/specs/taiwan-railway-gui/tasks.md` - 任務清單

### 技術文件
- `taiwan_railway_gui/README.md` - 程式碼結構說明
- `tests/INTEGRATION_TESTS.md` - 整合測試文件
- `UI_CONSISTENCY_IMPLEMENTATION.md` - UI 一致性實作說明

## 專案亮點

### 1. 完整的軟體工程實踐
- 需求分析 → 設計 → 實作 → 測試的完整流程
- 規格驅動開發 (Spec-Driven Development)
- 測試驅動開發 (Test-Driven Development)

### 2. 高品質程式碼
- 遵循 PEP 8 程式碼風格
- 完整的錯誤處理
- 詳細的程式碼註解和文件

### 3. 可維護性設計
- 模組化架構
- 清楚的責任分離
- 易於擴展的設計模式

### 4. 教育價值
- 適合作為 Python GUI 開發教學範例
- 展示資料庫整合最佳實踐
- 完整的測試策略示範

## 學習建議

### 初學者
1. 從 `main.py` 開始了解程式入口
2. 查看 `taiwan_railway_gui/models/` 了解資料結構
3. 研究 `taiwan_railway_gui/gui/` 學習 GUI 開發

### 進階開發者
1. 研究 `taiwan_railway_gui/dao/` 的資料存取模式
2. 分析 `taiwan_railway_gui/services/` 的服務層設計
3. 學習 `tests/` 中的測試策略和技巧

### 系統架構學習
1. 閱讀設計文件了解整體架構
2. 分析各層之間的互動關係
3. 研究錯誤處理和效能優化策略

## 貢獻指南

1. 遵循現有的程式碼風格
2. 為新功能添加相應的測試
3. 更新相關文件
4. 確保所有測試通過

## 授權

本專案僅供教育和學習使用。

---

**最後更新**: 2025年1月
**版本**: 1.0.0
**作者**: 開發團隊