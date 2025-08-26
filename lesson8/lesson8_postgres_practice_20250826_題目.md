# Lesson 8 PostgreSQL / Python 實務練習題 (2025-08-26)

> 本套題目依據本節課示範：基本查詢、JOIN、聚合、字串處理、參數化查詢、Python 連線與錯誤處理。請勿直接修改資料表結構，除非題目特別要求。若無特別說明，日期欄位名稱為 `"日期"`，車站代碼欄位為 `"車站代碼"`，進出站欄位為 `"進站人數"`, `"出站人數"`。

## 資料表 (摘要)
- `"台鐵車站資訊"("stationCode", "stationName", "name", "stationAddrTw", "stationTel", "haveBike", ... )`
- `"每日各站進出站人數"("日期", "車站代碼", "進站人數", "出站人數")`

---
## 題目 1：基本條件查詢
撰寫 SQL：查出地址位於「臺北市」的車站代碼、車站中文名稱(`"stationName"`)、電話(`"stationTel"`)；以車站代碼排序。

---
## 題目 2：最近 7 日進站統計 (JOIN + 聚合)
撰寫 SQL：計算「臺北市」各車站最近 7 日 (含今天，假設使用 `CURRENT_DATE`) 的總進站人數與平均每日進站人數 (取兩位小數)。輸出欄位：`stationCode`, `stationName`, `sum_in`, `avg_in`；依 `sum_in` 由大到小。

---
## 題目 3：不安全字串拼接改寫為參數化
下列 Python 程式片段存在 SQL 注入風險，請改寫成參數化查詢：
```python
user_input = input("請輸入車站名稱關鍵字:")
sql = f"SELECT \"stationCode\", \"stationName\" FROM \"台鐵車站資訊\" WHERE \"stationName\" LIKE '%{user_input}%'"
cursor.execute(sql)
```
說明你的改寫重點 (列出 2 點即可)。

---
## 題目 4：指定日期進站 Top 5 與縣市
給定查詢日期 (例如 `2025-08-20`)，找出該日進站人數最多的前 5 個車站，並顯示「縣市」欄位 (由車站地址 `"stationAddrTw"` 以 `SUBSTRING("stationAddrTw" FROM '^[^市縣]*[市縣]')` 擷取)；輸出：`rank`, `stationCode`, `stationName`, `city`, `in_count`。

---
## 題目 5：撰寫 Python 函式
撰寫一個函式 `get_station_passengers(conn, station_code, start_date, end_date)`，回傳 dict：`{"stationCode":..., "sum_in":..., "sum_out":..., "avg_daily_total":...}`。
- `avg_daily_total` = (期間總進站+總出站) / 天數 (保留兩位小數)。
- 使用參數化與適當錯誤處理 (捕捉資料庫例外)。

---
## 題目 6：錯誤處理設計
說明在課堂 `lesson8_4.py` 類似的連線 + 查詢流程中，應特別處理哪三類錯誤？並寫出 try/except/finally 骨架 (不用實作查詢)。

---
## 題目 7：資料清理 & 交易一致性
將 `"台鐵車站資訊"` 中 `"haveBike"` 欄位為 NULL 或空字串的車站統一更新為 'N'：
1. 寫出單一 SQL 完成的語句 (使用 `UPDATE`)。
2. 寫出 Python 交易流程 (begin -> update -> commit / rollback) 骨架。

---
## 題目 8：索引設計建議
常見查詢模式：「依車站代碼 + 日期區間」統計進出站總數。請：
1. 提出 2 個索引 (或 1 個複合索引 + 1 個覆蓋/功能性索引) 的設計想法。
2. 寫出 `CREATE INDEX` 語法。(若使用條件式/功能索引請說明理由 1 句)

---
## 題目 9：建立視圖觀察日變化
建立一個視圖 `v_station_daily_change`：顯示每站當日 (`日期`) 與前一日進站差異 `diff_in` 以及成長百分比 `growth_pct`。欄位：`stationCode`, `日期`, `進站人數`, `prev_in`, `diff_in`, `growth_pct`。`growth_pct` 以前一日為分母 (避免除以 0)。

---
## 題目 10 (挑戰題)：JSON 欄位解析
假設有表 `api_log(id serial, payload jsonb, created_at timestamptz)`，`payload` 結構如下例：
```json
{
  "status": "OK",
  "meta": {"source": "crawlerA"},
  "metrics": {"latency_ms": 732}
}
```
撰寫 SQL：取出 `status='OK'` 且 `metrics.latency_ms > 500` 的前 20 筆，輸出：`id`, `source`, `latency_ms`，依 `latency_ms` 由高到低。

---
## 題目 11：視圖 vs 物化視圖 評估 (短答)
針對「最近 7 日各站總進站與平均進站」報表：
1. 什麼情形適合使用一般視圖？
2. 什麼情形改用物化視圖？
3. 使用物化視圖時為何可能需要 `CONCURRENTLY`？

---
## 題目 12：安全性檢查 (短答)
列出在課程中提到或暗示的 3 項防止 SQL 注入 / 增強安全性的做法。

---
## 題目 13：查詢計畫初探 (短答)
若發現題目 2 的查詢隨資料量成長變慢，提出 2 個第一步可嘗試的診斷 / 優化方向 (簡述)。

---
## 題目 14：結果格式化 (Python)
示範如何將題目 4 的結果 (list of tuples) 以固定欄寬輸出表格表頭 + 資料列 (只寫輸出迴圈與表頭，假設資料變數為 `rows`)。

---
## 題目 15：交易與自動提交 (短答)
說明 psycopg2 連線中 autocommit=False 與顯式使用 `conn.commit()` 的差異與好處 (2 點)。

---
**完成後請再對照解答檔自我檢查。**
