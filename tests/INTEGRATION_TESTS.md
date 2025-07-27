# 整合測試文件

## 概述

本文件描述台鐵車站資訊查詢系統的整合測試實作，包含資料庫整合測試、GUI元件互動測試、端到端使用者工作流程測試、錯誤條件測試和效能測試。

## 整合測試架構

### 測試類型

1. **資料庫整合測試** (`test_integration_database.py`)
   - 測試DAO層與實際資料庫的整合
   - 驗證資料庫連線和交易處理
   - 測試資料查詢和更新操作

2. **GUI元件互動測試** (`test_integration_gui.py`)
   - 測試GUI元件之間的互動
   - 驗證分頁切換和資料傳遞
   - 測試使用者介面回應和狀態更新

3. **端到端整合測試** (`test_integration_end_to_end.py`)
   - 測試完整的使用者工作流程
   - 驗證系統在真實使用情境下的行為
   - 測試錯誤處理和效能表現

## 測試執行

### 執行所有整合測試

```bash
# 執行所有整合測試
python tests/run_integration_tests.py

# 或者使用具體的執行器
python tests/run_integration_tests.py --category all
```

### 執行特定類別的測試

```bash
# 只執行資料庫整合測試
python tests/run_integration_tests.py --category database

# 只執行GUI整合測試
python tests/run_integration_tests.py --category gui

# 只執行端到端測試
python tests/run_integration_tests.py --category e2e
```

### 詳細輸出

```bash
# 顯示詳細測試輸出
python tests/run_integration_tests.py --verbose
```

## 測試環境設定

### 依賴套件

整合測試需要以下套件：

```
# 基本需求
unittest (Python 標準函式庫)
tkinter (GUI 測試)
sqlite3 (測試資料庫)

# 可選需求
psutil (記憶體使用測試，可選)
```

### 測試資料庫

整合測試使用 SQLite 記憶體資料庫進行測試，包含：

- 5個測試車站
- 30天的乘客流量資料
- 完整的資料關聯和約束

### 測試配置

測試配置定義在 `test_config.py` 中，包含：

- 測試資料庫設定
- 測試資料生成參數
- GUI測試超時設定
- 效能測試閾值

## 測試覆蓋範圍

### 資料庫整合測試

✅ **StationDAO 整合測試**
- `test_get_all_stations()` - 取得所有車站
- `test_search_stations_by_name()` - 按名稱搜尋車站
- `test_get_station_by_id()` - 根據ID取得車站
- `test_search_stations_by_line()` - 按路線搜尋車站

✅ **PassengerFlowDAO 整合測試**
- `test_get_passenger_flow_by_station_and_date_range()` - 按車站和日期範圍查詢
- `test_get_passenger_flow_summary()` - 取得客流量摘要
- `test_get_top_stations_by_passenger_count()` - 取得客流量最高車站
- `test_compare_stations_passenger_flow()` - 比較多個車站客流量

✅ **資料庫連線整合測試**
- `test_database_connection_singleton()` - 測試單例模式
- `test_database_connection_retry()` - 測試連線重試
- `test_transaction_handling()` - 測試交易處理

### GUI元件互動測試

✅ **主視窗整合測試**
- `test_main_window_initialization()` - 主視窗初始化
- `test_tab_switching()` - 分頁切換功能
- `test_status_bar_updates()` - 狀態列更新
- `test_loading_indicator()` - 載入指示器

✅ **車站搜尋分頁測試**
- `test_search_functionality()` - 搜尋功能
- `test_station_selection()` - 車站選擇
- `test_clear_functionality()` - 清除功能

✅ **客流量查詢分頁測試**
- `test_station_combobox_population()` - 車站下拉選單
- `test_date_range_validation()` - 日期範圍驗證
- `test_query_execution()` - 查詢執行

✅ **車站比較分頁測試**
- `test_station_addition()` - 車站新增
- `test_station_removal()` - 車站移除
- `test_maximum_stations_limit()` - 最大車站限制
- `test_comparison_execution()` - 比較執行

✅ **圖表分頁測試**
- `test_chart_generation()` - 圖表生成
- `test_chart_controls()` - 圖表控制項
- `test_chart_export()` - 圖表匯出

✅ **跨分頁整合測試**
- `test_station_search_to_passenger_flow()` - 車站搜尋到客流量查詢
- `test_station_selection_to_comparison()` - 車站選擇到比較功能
- `test_data_consistency_across_tabs()` - 跨分頁資料一致性

### 端到端整合測試

✅ **完整使用者工作流程測試**
- `test_complete_station_search_workflow()` - 完整車站搜尋流程
- `test_complete_passenger_flow_query_workflow()` - 完整客流量查詢流程
- `test_complete_station_comparison_workflow()` - 完整車站比較流程
- `test_complete_chart_visualization_workflow()` - 完整圖表視覺化流程
- `test_complete_data_export_workflow()` - 完整資料匯出流程

✅ **錯誤條件測試**
- `test_database_connection_error_handling()` - 資料庫連線錯誤處理
- `test_invalid_input_handling()` - 無效輸入處理
- `test_empty_search_results_handling()` - 空搜尋結果處理
- `test_export_permission_error_handling()` - 匯出權限錯誤處理

✅ **效能和大型資料集測試**
- `test_large_dataset_query_performance()` - 大型資料集查詢效能
- `test_pagination_functionality()` - 分頁功能
- `test_memory_usage_with_large_dataset()` - 大型資料集記憶體使用（可選）

## 測試資料

### 測試車站

整合測試使用以下5個測試車站：

| 車站ID | 車站名稱 | 等級 | 路線 |
|--------|----------|------|------|
| 1000   | 台北     | 特等 | 縱貫線 |
| 1001   | 板橋     | 一等 | 縱貫線 |
| 1008   | 桃園     | 一等 | 縱貫線 |
| 1025   | 新竹     | 一等 | 縱貫線 |
| 1100   | 台中     | 特等 | 縱貫線 |

### 測試乘客流量資料

- **時間範圍**：過去30天（標準測試）或90天（大型資料集測試）
- **資料密度**：每個車站每天一筆記錄
- **數值範圍**：進站人數 1000-2500，出站人數 950-2400
- **總記錄數**：150筆（標準）或450筆（大型資料集）

## 測試結果格式

### 成功輸出範例

```
🚀 開始執行台鐵車站資訊查詢系統整合測試
⏰ 開始時間：2025-07-27 15:30:00

============================================================
🔍 執行資料庫整合測試
============================================================
test_get_all_stations ... ok
test_search_stations_by_name ... ok
test_get_station_by_id ... ok
...

============================================================
🖥️  執行GUI整合測試
============================================================
test_main_window_initialization ... ok
test_tab_switching ... ok
test_status_bar_updates ... ok
...

============================================================
🔄 執行端到端整合測試
============================================================
test_complete_station_search_workflow ... ok
test_complete_passenger_flow_query_workflow ... ok
...

============================================================
📊 整合測試執行摘要
============================================================
⏱️  執行時間：45.32 秒
🧪 總測試數：42
✅ 成功：42
❌ 失敗：0
⚠️  錯誤：0

   DATABASE        ✅ 通過   (12 測試)
   GUI             ✅ 通過   (18 測試)
   END_TO_END      ✅ 通過   (12 測試)

🎉 所有整合測試通過！
```

### 失敗輸出範例

```
============================================================
📊 整合測試執行摘要
============================================================
⏱️  執行時間：38.15 秒
🧪 總測試數：42
✅ 成功：39
❌ 失敗：2
⚠️  錯誤：1

   DATABASE        ✅ 通過   (12 測試)
   GUI             ❌ 失敗   (18 測試)
   END_TO_END      ❌ 失敗   (12 測試)

💥 整合測試失敗！2 個失敗，1 個錯誤
```

## 疑難排解

### 常見問題

1. **資料庫連線失敗**
   ```
   錯誤：sqlite3.OperationalError: unable to open database file
   解決：檢查測試資料庫路徑權限，確保臨時目錄可寫入
   ```

2. **GUI測試超時**
   ```
   錯誤：測試在等待GUI更新時超時
   解決：增加 GUI_TEST_CONFIG 中的 wait_timeout 值
   ```

3. **記憶體測試跳過**
   ```
   警告：psutil 未安裝，跳過記憶體使用測試
   解決：安裝 psutil 套件或忽略此測試
   ```

4. **模組載入錯誤**
   ```
   錯誤：無法載入GUI整合測試模組
   解決：檢查 PYTHONPATH 設定，確保專案根目錄在路徑中
   ```

### 效能調整

如果測試執行時間過長，可以調整以下參數：

```python
# 在 test_config.py 中調整
PERFORMANCE_TEST_CONFIG = {
    'max_query_time': 5.0,      # 降低最大查詢時間要求
    'large_dataset_size': 30,   # 減少大型資料集大小
}

GUI_TEST_CONFIG = {
    'wait_timeout': 1.0,        # 減少GUI等待時間
}
```

## 持續整合

### GitHub Actions 設定

```yaml
name: Integration Tests
on: [push, pull_request]
jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run integration tests
      run: |
        python tests/run_integration_tests.py
```

### 本地開發環境

```bash
# 在提交前執行整合測試
git add .
python tests/run_integration_tests.py
git commit -m "功能更新"
```

## 測試報告

整合測試執行後會生成以下資訊：

- **執行時間統計**：各類測試的執行時間
- **測試覆蓋統計**：成功/失敗/錯誤的測試數量
- **詳細錯誤報告**：失敗測試的具體錯誤訊息
- **效能指標**：查詢時間、記憶體使用等效能數據

這些資訊可用於：
- 驗證系統功能正確性
- 監控系統效能表現
- 識別和修復整合問題
- 確保軟體品質標準
