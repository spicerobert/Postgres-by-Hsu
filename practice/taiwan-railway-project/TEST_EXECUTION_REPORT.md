# 台鐵車站資訊查詢系統 - 測試執行報告

**執行時間:** 2025-07-28 23:37:00
**測試時長:** 92.36 秒
**成功率:** 31.2%

## 測試統計

| 項目 | 數量 |
|------|------|
| 總測試數 | 16 |
| 通過測試 | 5 |
| 失敗測試 | 11 |

## 分類統計

### 單元測試

- 通過率: 33.3% (1/3)

- ❌ `tests/test_models.py`: Traceback (most recent call last):
  File "/Users/roberthsu2003/Documents/GitHub/__2025_06_29_chihlee_postgres__/practice/taiwan-railway-project/tests/test_models.py", line 9, in <module>
    from tai
- ✅ `tests/test_config.py`: 測試通過
- ❌ `tests/test_dao.py`: Traceback (most recent call last):
  File "/Users/roberthsu2003/Documents/GitHub/__2025_06_29_chihlee_postgres__/practice/taiwan-railway-project/tests/test_dao.py", line 10, in <module>
    from taiwa

### 整合測試

- 通過率: 0.0% (0/3)

- ❌ `tests/test_integration_database.py`: test_get_all_stations (__main__.TestStationDAOIntegration)
測試取得所有車站 ... FAIL
test_get_station_by_code (__main__.TestStationDAOIntegration)
測試根據代碼取得車站 ... ok
test_get_stations_by_codes (__main__.TestSt
- ❌ `tests/test_integration_end_to_end.py`: test_complete_chart_visualization_workflow (__main__.TestCompleteUserWorkflows)
測試完整的圖表視覺化工作流程 ... ERROR
test_complete_data_export_workflow (__main__.TestCompleteUserWorkflows)
測試完整的資料匯出工作流程 ... ERROR
- ❌ `tests/run_integration_tests.py`: 未知錯誤

### GUI 測試

- 通過率: 33.3% (2/6)

- ❌ `test_gui.py`: 未知錯誤
- ❌ `test_station_search_gui.py`: 未知錯誤
- ❌ `test_passenger_flow_gui.py`: 未知錯誤
- ✅ `test_comparison_gui.py`: 測試通過
- ❌ `test_chart_gui.py`: Traceback (most recent call last):
  File "/Users/roberthsu2003/Documents/GitHub/__2025_06_29_chihlee_postgres__/practice/taiwan-railway-project/test_chart_gui.py", line 38, in test_chart_tab
    char
- ✅ `test_ui_consistency.py`: 測試通過

### 系統測試

- 通過率: 33.3% (1/3)

- ✅ `test_database_connection.py`: 測試通過
- ❌ `tests/test_performance.py`: Traceback (most recent call last):
  File "/Users/roberthsu2003/Documents/GitHub/__2025_06_29_chihlee_postgres__/practice/taiwan-railway-project/tests/test_performance.py", line 12, in <module>
    fr
- ❌ `tests/test_error_handling.py`: Traceback (most recent call last):
  File "/Users/roberthsu2003/Documents/GitHub/__2025_06_29_chihlee_postgres__/practice/taiwan-railway-project/tests/test_error_handling.py", line 13, in <module>
   

### 最終整合測試

- 通過率: 100.0% (1/1)

- ✅ `final_system_integration_test.py`: 測試通過

## 測試建議

🔴 **需改善** - 測試結果不佳，需要大幅修正
