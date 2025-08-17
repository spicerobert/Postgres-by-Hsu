# lesson8/lesson8_4.py 程式碼說明

## 檔案概述
這個 Python 腳本 (`lesson8/lesson8_4.py`) 是一個簡單的「台鐵資料查詢系統」的主程式。它主要用於示範如何連接到 PostgreSQL 資料庫，並執行一個基本的查詢來驗證連線。

## 功能說明
- **資料庫連線**：使用 `psycopg2` 模組連接到 PostgreSQL 資料庫。
- **連線配置**：資料庫連線參數（如資料庫名稱、使用者、密碼、主機和埠號）在 `DB_CONFIG` 字典中定義。其中，`host` 設定為 `host.docker.internal`，這表示它設計用於在 Docker 容器內部運行，並連接到 Docker 主機上的 PostgreSQL 服務。
- **連線測試**：成功連接後，程式會執行一個 `SELECT version();` 查詢來獲取並顯示 PostgreSQL 資料庫的版本，以此驗證連線的有效性。
- **錯誤處理**：如果資料庫連線失敗，程式會捕獲異常並列印錯誤訊息，然後安全地退出。

## 程式碼結構

### `DB_CONFIG` (字典)
- 儲存資料庫連線所需的設定。
  - `dbname`: 資料庫名稱 (e.g., "postgres")
  - `user`: 資料庫使用者名稱 (e.g., "postgres")
  - `password`: 資料庫密碼 (e.g., "raspberry")
  - `host`: 資料庫主機位址 (e.g., "host.docker.internal")
  - `port`: 資料庫埠號 (e.g., "5432")

### `connect_to_database()` 函數
- **目的**：建立並返回一個 PostgreSQL 資料庫連線物件。
- **流程**：
    1. 嘗試使用 `DB_CONFIG` 中的參數建立 `psycopg2` 連線。
    2. 如果連線成功，返回連線物件。
    3. 如果發生任何異常（例如連線失敗），捕獲異常，列印錯誤訊息，並返回 `None`。

### `main()` 函數
- **目的**：程式的主執行邏輯。
- **流程**：
    1. 呼叫 `connect_to_database()` 嘗試建立資料庫連線。
    2. 如果 `connect_to_database()` 返回 `None`（表示連線失敗），則列印錯誤訊息並使用 `sys.exit(1)` 終止程式。
    3. 如果連線成功，列印「成功連接到資料庫！」訊息。
    4. 建立一個資料庫游標 (cursor)。
    5. 執行 SQL 查詢 `SELECT version();`。
    6. 獲取查詢結果（資料庫版本）。
    7. 列印 PostgreSQL 資料庫的版本資訊。
    8. 關閉游標。
    9. 關閉資料庫連線。
    10. 列印「資料庫連接已關閉」訊息。

## 如何運行
1.  **安裝依賴**：確保您的 Python 環境中安裝了 `psycopg2` 模組。如果沒有，可以使用 pip 安裝：
    ```bash
    pip install psycopg2-binary
    ```
2.  **PostgreSQL 資料庫**：確保您有一個正在運行的 PostgreSQL 資料庫，並且其配置與 `DB_CONFIG` 中的設定相符。特別是，如果是在 Docker 環境中運行此腳本，請確保 PostgreSQL 服務在 Docker 主機上運行，並且可以透過 `host.docker.internal` 訪問。
3.  **執行腳本**：
    ```bash
    python lesson8/lesson8_4.py
    ```

## 預期輸出
如果資料庫連線成功，您將看到類似以下的輸出：
```
成功連接到資料庫！
PostgreSQL 資料庫版本: PostgreSQL 16.3 (Debian 16.3-1.pgdg120+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit
資料庫連接已關閉
```
如果連線失敗，則會顯示錯誤訊息。