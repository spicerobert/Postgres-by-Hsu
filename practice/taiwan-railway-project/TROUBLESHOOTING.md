# 台鐵車站資訊查詢 GUI 應用程式 - 故障排除指南

## 常見問題與解決方案

### 1. 資料庫連線問題

**問題**: 應用程式無法連接到 PostgreSQL 資料庫

**解決方案**:
1. 確認 PostgreSQL 服務正在運行
2. 檢查資料庫配置（taiwan_railway_gui/config.py）:
   - 主機: localhost
   - 埠號: 5432
   - 資料庫名稱: taiwan_railway
   - 使用者名稱: postgres
   - 密碼: raspberry

3. 執行資料庫設定腳本:
   ```bash
   python setup_database_simple.py
   ```

### 2. GUI 顯示問題

**問題**: GUI 介面無法正常顯示或出現樣式錯誤

**解決方案**:
1. 確認 tkinter 已正確安裝
2. 在 macOS 上，可能需要安裝 Python 的 tkinter 支援
3. 如果出現樣式錯誤，應用程式會自動降級到預設樣式

### 3. 套件相依性問題

**問題**: 缺少必要的 Python 套件

**解決方案**:
```bash
pip install psycopg2-binary matplotlib
```

### 4. 資料表不存在

**問題**: 查詢時出現 "relation does not exist" 錯誤

**解決方案**:
執行資料庫設定腳本建立必要的表格:
```bash
python setup_database_simple.py
```

### 5. 權限問題

**問題**: 無法寫入日誌檔案或匯出檔案

**解決方案**:
1. 確認應用程式目錄有寫入權限
2. 選擇有寫入權限的匯出目錄

## 測試指令

### 測試資料庫連線
```bash
python test_database_connection.py
```

### 執行完整測試
```bash
python final_bug_fixes_and_integration.py
```

### 啟動應用程式
```bash
python launch_app.py
```

## 日誌檔案

應用程式會在執行目錄建立 `taiwan_railway_gui.log` 日誌檔案，
包含詳細的錯誤資訊和執行記錄。

## 聯絡支援

如果問題持續存在，請檢查日誌檔案並提供錯誤訊息以獲得進一步協助。
