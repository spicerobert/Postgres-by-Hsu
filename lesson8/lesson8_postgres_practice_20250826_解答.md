# Lesson 8 PostgreSQL / Python 實務練習題 解答與解析 (2025-08-26)

> 解答僅供參考，實務可依實際 schema / 效能調整。若欄位型別不同請自行轉型。

## 題目 1 解答
```sql
SELECT "stationCode", "stationName", "stationTel"
FROM "台鐵車站資訊"
WHERE "stationAddrTw" LIKE '%臺北市%'
ORDER BY "stationCode";
```
解析：LIKE 模糊比對；未使用 `ILIKE` 因原題未提大小寫需求。

## 題目 2 解答
```sql
SELECT t."stationCode",
       t."stationName",
       SUM(d."進站人數") AS sum_in,
       ROUND(AVG(d."進站人數")::numeric, 2) AS avg_in
FROM "台鐵車站資訊" t
JOIN "每日各站進出站人數" d ON t."stationCode" = d."車站代碼"
WHERE t."stationAddrTw" LIKE '%臺北市%'
  AND d."日期" BETWEEN CURRENT_DATE - INTERVAL '6 days' AND CURRENT_DATE
GROUP BY t."stationCode", t."stationName"
ORDER BY sum_in DESC;
```
解析：7 日含今日 => 0~6 天前；AVG 轉 numeric 保留兩位。

## 題目 3 解答
安全參數化：
```python
user_input = input("請輸入車站名稱關鍵字:")
sql = """SELECT "stationCode", "stationName"
FROM "台鐵車站資訊"
WHERE "stationName" LIKE %s"""
param = (f"%{user_input}%", )
cursor.execute(sql, param)
```
重點：
1. 使用 `%s` 佔位並將值放入參數 tuple，避免字串直接拼接。
2. 模糊查詢的 `%` 放到參數內容中，驅動程式會正確跳脫。

## 題目 4 解答
```sql
WITH base AS (
  SELECT d."車站代碼", d."進站人數",
         SUBSTRING(t."stationAddrTw" FROM '^[^市縣]*[市縣]') AS city,
         t."stationName"
  FROM "每日各站進出站人數" d
  JOIN "台鐵車站資訊" t ON t."stationCode" = d."車站代碼"
  WHERE d."日期" = DATE '2025-08-20'
)
SELECT ROW_NUMBER() OVER (ORDER BY "進站人數" DESC) AS rank,
       "車站代碼" AS "stationCode",
       "stationName",
       city,
       "進站人數" AS in_count
FROM base
ORDER BY in_count DESC
LIMIT 5;
```
解析：ROW_NUMBER 產生排名；SUBSTRING 擷取縣市。

## 題目 5 解答
```python
def get_station_passengers(conn, station_code, start_date, end_date):
    """回傳指定站在期間內進出站統計。"""
    sql = """
        SELECT
          SUM("進站人數") AS sum_in,
          SUM("出站人數") AS sum_out,
          COUNT(DISTINCT "日期") AS days
        FROM "每日各站進出站人數"
        WHERE "車站代碼" = %s
          AND "日期" BETWEEN %s AND %s
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (station_code, start_date, end_date))
            row = cur.fetchone()
            if not row or row[2] == 0:
                return {"stationCode": station_code, "sum_in": 0, "sum_out": 0, "avg_daily_total": 0.00}
            sum_in, sum_out, days = row
            avg_daily_total = round((sum_in + sum_out) / days, 2)
            return {"stationCode": station_code, "sum_in": sum_in, "sum_out": sum_out, "avg_daily_total": avg_daily_total}
    except Exception as e:
        # 可細分 psycopg2.Error 類型
        return {"stationCode": station_code, "error": str(e)}
```
解析：使用 `with cursor()` 自動釋放；days 防除以 0。

## 題目 6 解答
三類錯誤：
1. 連線錯誤 (認證 / 網路 / Host 不可達)
2. 查詢錯誤 (SQL 語法 / 欄位不存在)
3. 資料一致性 / 邏輯錯誤 (空結果、資料型別轉換)
骨架：
```python
import psycopg2
from psycopg2 import sql, OperationalError, ProgrammingError

conn = None
try:
    conn = psycopg2.connect(...)
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        print(cur.fetchone())
except OperationalError as oe:
    print("連線失敗:", oe)
except ProgrammingError as pe:
    print("SQL 錯誤:", pe)
except Exception as e:
    print("其他錯誤:", e)
finally:
    if conn:
        conn.close()
```

## 題目 7 解答
1) SQL：
```sql
UPDATE "台鐵車站資訊"
SET "haveBike" = 'N'
WHERE COALESCE(TRIM("haveBike"), '') = '';
```
2) 交易骨架：
```python
try:
    conn.autocommit = False
    with conn.cursor() as cur:
        cur.execute("UPDATE \"台鐵車站資訊\" SET \"haveBike\"='N' WHERE COALESCE(TRIM(\"haveBike\"), '')='' ")
    conn.commit()
except Exception:
    conn.rollback()
    raise
```
解析：使用 COALESCE + TRIM 捕捉 NULL 與空白。

## 題目 8 解答
設計：
- 複合索引：(`"車站代碼"`, `"日期"`) 加速依站+日期範圍查。
- 覆蓋/功能索引：若常計算總和可用 BRIN 或針對日期做範圍；或建立僅日期的索引以支援按日期批次。
語法示例：
```sql
CREATE INDEX idx_daily_station_date ON "每日各站進出站人數"("車站代碼", "日期");
-- 若資料是時間序列且巨大，可考慮 BRIN 以降低索引大小
CREATE INDEX idx_daily_date_brin ON "每日各站進出站人數" USING BRIN ("日期");
```
理由：BRIN 對大量按時間 append 的表具備更低維護成本。

## 題目 9 解答
```sql
CREATE OR REPLACE VIEW v_station_daily_change AS
WITH ordered AS (
  SELECT "車站代碼" AS stationCode,
         "日期",
         "進站人數",
         LAG("進站人數") OVER (PARTITION BY "車站代碼" ORDER BY "日期") AS prev_in
  FROM "每日各站進出站人數"
)
SELECT stationCode,
       "日期",
       "進站人數",
       prev_in,
       ("進站人數" - prev_in) AS diff_in,
       CASE WHEN prev_in IS NULL OR prev_in = 0 THEN NULL
            ELSE ROUND(("進站人數" - prev_in)::numeric / prev_in * 100, 2) END AS growth_pct
FROM ordered;
```
解析：LAG 取前一日；除以 0 與 NULL 轉為 NULL。

## 題目 10 解答
```sql
SELECT id,
       payload->'meta'->>'source' AS source,
       (payload->'metrics'->>'latency_ms')::int AS latency_ms
FROM api_log
WHERE payload->>'status' = 'OK'
  AND (payload->'metrics'->>'latency_ms')::int > 500
ORDER BY latency_ms DESC
LIMIT 20;
```
解析：使用 -> / ->> 抽取；數值轉型排序。

## 題目 11 解答
1. 資料即時、更新頻繁且查詢成本不高 → 一般視圖 (即時反映底層資料)。
2. 計算昂貴、重複被查且可容忍延遲 → 物化視圖 (降低重複聚合成本)。
3. `CONCURRENTLY`：在刷新時仍允許查詢舊資料，減少鎖表影響 (需具備索引要求與條件)。

## 題目 12 解答
1. 參數化查詢 (`%s`) 避免字串拼接。
2. 最小權限原則 (僅授權 SELECT/INSERT 所需表)。
3. 驗證 / 限制使用者輸入 (長度、型別、允許字元)。
(其他可接受：隔離帳號、使用交易控制、審計 log)。

## 題目 13 解答
1. 使用 `EXPLAIN (ANALYZE, BUFFERS)` 檢視是否 Seq Scan，可評估建立 (`車站代碼`,`日期`) 複合索引。
2. 檢查時間範圍是否可被條件縮小 (避免不必要的日期跨度) 或建立物化 / 快取層。

## 題目 14 解答
```python
# 表頭
print(f"{'RANK':<5}{'CODE':<10}{'NAME':<15}{'CITY':<8}{'IN':>8}")
print('-'*46)
for r in rows:  # 假設 (rank, code, name, city, in_count)
    rank, code, name, city, in_count = r
    print(f"{rank:<5}{code:<10}{name:<15}{(city or ''):<8}{in_count:>8}")
```
解析：使用對齊格式 `<` 左對齊，`>` 右對齊；處理 city 可能為 NULL。

## 題目 15 解答
1. autocommit=False 允許多個語句組成原子操作，出錯可 rollback 確保一致性。
2. 顯式 `commit()` 提供更精細控制 (例如批次更新、降低頻繁 fsync 成本)，也可在失敗時 rollback 減少半成品狀態。

---
## 延伸建議
- 可將題目 9 視圖改物化並排程刷新以供報表使用。
- 對 JSON 日誌頻繁篩選欄位建立 GIN 索引：`CREATE INDEX ON api_log USING GIN (payload jsonb_path_ops);`
- Python 層加入重試機制與連線池 (psycopg2.pool)。

(完)
