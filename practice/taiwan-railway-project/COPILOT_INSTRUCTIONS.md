# 專案開發指引

這個檔案包含了 GitHub Copilot 在此專案中應該遵循的指引和慣例。

## 資料庫相關
- 表格名稱使用繁體中文
- 欄位名稱使用雙引號包圍
- 優先使用 PostgreSQL 特有功能

## 程式碼風格
- 註解使用繁體中文
- 變數命名使用駝峰式
- SQL 關鍵字大寫

## 專案工具
- 主要使用 `mcp_vscode_postgr_query` 進行資料庫查詢
- Jupyter Notebook 用於資料分析和視覺化

## 常見查詢模式
```sql
-- 查詢特定地區車站
SELECT "stationCode", "stationName"
FROM "台鐵車站資訊"
WHERE "stationAddrTw" LIKE '地區名%';

-- 查詢進出站人數
SELECT 日期, 車站代碼, 進站人數, 出站人數
FROM "每日各站進出站人數"
WHERE 日期 BETWEEN '開始日期' AND '結束日期';
```
