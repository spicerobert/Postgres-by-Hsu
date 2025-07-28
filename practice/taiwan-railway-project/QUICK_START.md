# 快速開始指南

## 🚀 5分鐘快速體驗

### 1. 環境準備
```bash
# 確保 Python 3.8+ 已安裝
python --version

# 進入專案目錄
cd practice/taiwan-railway-project

# 安裝依賴（如果需要）
pip install -r requirements.txt
```

### 2. 立即執行
```bash
# 啟動應用程式
python main.py
```

### 3. 執行測試
```bash
# 執行綜合整合測試（最完整的測試）
python tests/run_integration_tests.py --category comprehensive

# 執行簡單測試（快速驗證）
python tests/run_integration_tests.py --category simple
```

## 📋 功能體驗清單

### ✅ 車站搜尋
1. 啟動應用程式
2. 在搜尋框輸入 "台北"
3. 查看搜尋結果和車站詳細資訊

### ✅ 客流量查詢
1. 切換到 "客流量查詢" 分頁
2. 選擇車站
3. 設定日期範圍
4. 執行查詢查看結果

### ✅ 車站比較
1. 切換到 "車站比較" 分頁
2. 新增多個車站
3. 執行比較查看排名

### ✅ 圖表視覺化
1. 切換到 "圖表" 分頁
2. 選擇車站和日期範圍
3. 生成客流量趨勢圖

## 🧪 測試驗證

### 快速測試
```bash
# 基本功能測試（約30秒）
python tests/run_integration_tests.py --category simple

# 綜合功能測試（約1分鐘）
python tests/run_integration_tests.py --category comprehensive
```

### 完整測試
```bash
# 所有測試（約3-5分鐘）
python tests/run_integration_tests.py --category all
```

## 📚 學習路徑

### 🔰 初學者路徑
1. **了解專案結構** - 閱讀 `PROJECT_OVERVIEW.md`
2. **執行應用程式** - 運行 `python main.py`
3. **查看主要模型** - 研究 `taiwan_railway_gui/models/`
4. **理解GUI結構** - 查看 `taiwan_railway_gui/gui/`

### 🔧 開發者路徑
1. **架構分析** - 閱讀 `.kiro/specs/taiwan-railway-gui/design.md`
2. **資料存取層** - 研究 `taiwan_railway_gui/dao/`
3. **服務層設計** - 分析 `taiwan_railway_gui/services/`
4. **測試策略** - 學習 `tests/` 中的測試方法

### 🏗️ 架構師路徑
1. **需求分析** - 閱讀 `.kiro/specs/taiwan-railway-gui/requirements.md`
2. **系統設計** - 研究整體架構設計
3. **整合測試** - 分析 `tests/test_integration_comprehensive.py`
4. **效能優化** - 查看效能測試和優化策略

## 🔍 常見問題

### Q: 應用程式無法啟動？
A: 檢查 Python 版本和依賴套件安裝

### Q: 測試失敗？
A: 某些GUI測試可能在特定環境下有問題，建議執行 comprehensive 測試

### Q: 如何修改資料庫配置？
A: 編輯 `taiwan_railway_gui/config.py` 檔案

### Q: 如何添加新功能？
A: 參考現有的模組結構，遵循 MVC 架構模式

## 📞 支援

- 查看 `PROJECT_OVERVIEW.md` 了解詳細資訊
- 閱讀程式碼註解和文件
- 執行測試了解系統行為
- 研究 `.kiro/specs/` 中的規格文件

---

**祝您學習愉快！** 🎉