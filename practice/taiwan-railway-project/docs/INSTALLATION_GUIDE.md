# 台鐵車站資訊查詢系統 - 安裝指南

## 目錄

1. [系統需求](#系統需求)
2. [安裝前準備](#安裝前準備)
3. [安裝步驟](#安裝步驟)
4. [資料庫設定](#資料庫設定)
5. [環境變數設定](#環境變數設定)
6. [驗證安裝](#驗證安裝)
7. [常見安裝問題](#常見安裝問題)
8. [解除安裝](#解除安裝)

## 系統需求

### 支援的作業系統

- **Windows**: Windows 10 (1903) 或更新版本
- **macOS**: macOS 10.14 (Mojave) 或更新版本
- **Linux**: Ubuntu 18.04 LTS 或更新版本，CentOS 7 或更新版本

### 硬體需求

#### 最低需求
- **處理器**: 雙核心 1.6GHz 或更快
- **記憶體**: 4GB RAM
- **硬碟空間**: 1GB 可用空間
- **顯示器**: 1024x768 解析度

#### 建議需求
- **處理器**: 四核心 2.0GHz 或更快
- **記憶體**: 8GB RAM 或更多
- **硬碟空間**: 2GB 可用空間
- **顯示器**: 1920x1080 解析度或更高

### 軟體需求

- **Python**: 3.8.0 或更新版本
- **PostgreSQL**: 12.0 或更新版本（用於資料庫連線）
- **網路連線**: 用於資料庫存取和套件下載

## 安裝前準備

### 1. 檢查 Python 版本

開啟終端機或命令提示字元，執行：

```bash
python --version
```

或

```bash
python3 --version
```

確保版本為 3.8.0 或更高。如果沒有安裝 Python 或版本過舊，請前往 [Python 官方網站](https://www.python.org/downloads/) 下載最新版本。

### 2. 檢查 pip 工具

```bash
pip --version
```

或

```bash
pip3 --version
```

如果 pip 未安裝，請參考 [pip 安裝指南](https://pip.pypa.io/en/stable/installation/)。

### 3. 準備資料庫資訊

確保您有以下資料庫連線資訊：
- 資料庫主機位址
- 埠號（預設 5432）
- 資料庫名稱
- 使用者名稱
- 密碼

## 安裝步驟

### 方法一：從原始碼安裝（推薦）

#### 步驟 1: 下載原始碼

```bash
# 使用 git 克隆（如果有 git）
git clone https://github.com/your-repo/taiwan-railway-gui.git
cd taiwan-railway-gui

# 或下載 ZIP 檔案並解壓縮
```

#### 步驟 2: 建立虛擬環境（建議）

```bash
# 建立虛擬環境
python -m venv taiwan_railway_env

# 啟動虛擬環境
# Windows:
taiwan_railway_env\Scripts\activate

# macOS/Linux:
source taiwan_railway_env/bin/activate
```

#### 步驟 3: 安裝相依套件

```bash
# 升級 pip
pip install --upgrade pip

# 安裝專案相依套件
pip install -r requirements.txt
```

#### 步驟 4: 驗證安裝

```bash
python -c "import tkinter; import psycopg2; import matplotlib; print('所有套件安裝成功')"
```

### 方法二：使用 pip 安裝（如果有發布到 PyPI）

```bash
pip install taiwan-railway-gui
```

## 資料庫設定

### PostgreSQL 安裝

如果您還沒有 PostgreSQL 資料庫，請按照以下步驟安裝：

#### Windows

1. 前往 [PostgreSQL 官方網站](https://www.postgresql.org/download/windows/)
2. 下載適合的安裝程式
3. 執行安裝程式並按照指示完成安裝
4. 記住設定的密碼

#### macOS

使用 Homebrew：
```bash
brew install postgresql
brew services start postgresql
```

或下載官方安裝程式。

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### CentOS/RHEL

```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 資料庫初始化

1. 建立資料庫：

```sql
CREATE DATABASE taiwan_railway;
```

2. 建立使用者（可選）：

```sql
CREATE USER railway_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE taiwan_railway TO railway_user;
```

3. 匯入資料（如果有提供資料檔案）：

```bash
psql -U your_username -d taiwan_railway -f data/taiwan_railway_data.sql
```

## 環境變數設定

### 方法一：設定環境變數

#### Windows

在命令提示字元中：
```cmd
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=taiwan_railway
set DB_USER=your_username
set DB_PASSWORD=your_password
```

或在系統環境變數中永久設定。

#### macOS/Linux

在終端機中：
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=taiwan_railway
export DB_USER=your_username
export DB_PASSWORD=your_password
```

或將這些設定加入 `~/.bashrc` 或 `~/.zshrc` 檔案中。

### 方法二：建立 .env 檔案

在專案根目錄建立 `.env` 檔案：

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=taiwan_railway
DB_USER=your_username
DB_PASSWORD=your_password
```

### 方法三：修改設定檔

直接編輯 `taiwan_railway_gui/config.py` 檔案：

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'taiwan_railway',
    'user': 'your_username',
    'password': 'your_password',
}
```

**注意**: 不建議將密碼直接寫在程式碼中，特別是在版本控制系統中。

## 驗證安裝

### 1. 測試資料庫連線

```bash
python -c "
from taiwan_railway_gui.dao.database_manager import get_database_manager
db = get_database_manager()
if db.test_connection():
    print('資料庫連線成功')
else:
    print('資料庫連線失敗')
"
```

### 2. 啟動應用程式

```bash
python main.py
```

如果安裝成功，應該會看到應用程式主視窗。

### 3. 執行測試

```bash
# 執行所有測試
python -m pytest tests/

# 或執行特定測試
python test_database_connection.py
```

## 常見安裝問題

### 問題 1: Python 版本過舊

**錯誤訊息**: `SyntaxError` 或 `This application requires Python 3.8 or higher`

**解決方法**:
1. 安裝 Python 3.8 或更新版本
2. 使用 `python3` 而不是 `python` 命令
3. 更新系統的預設 Python 版本

### 問題 2: pip 安裝套件失敗

**錯誤訊息**: `ERROR: Could not install packages due to an EnvironmentError`

**解決方法**:
```bash
# 升級 pip
pip install --upgrade pip

# 使用使用者安裝
pip install --user -r requirements.txt

# 或使用管理員權限（Windows）
# 以管理員身分執行命令提示字元

# macOS/Linux 使用 sudo
sudo pip install -r requirements.txt
```

### 問題 3: psycopg2 安裝失敗

**錯誤訊息**: `Error: pg_config executable not found`

**解決方法**:

#### Windows
```bash
pip install psycopg2-binary
```

#### macOS
```bash
brew install postgresql
pip install psycopg2
```

#### Ubuntu/Debian
```bash
sudo apt-get install libpq-dev python3-dev
pip install psycopg2
```

#### CentOS/RHEL
```bash
sudo yum install postgresql-devel python3-devel
pip install psycopg2
```

### 問題 4: tkinter 模組找不到

**錯誤訊息**: `ModuleNotFoundError: No module named '_tkinter'`

**解決方法**:

#### Ubuntu/Debian
```bash
sudo apt-get install python3-tk
```

#### CentOS/RHEL
```bash
sudo yum install tkinter
```

#### macOS
通常 tkinter 已包含在 Python 中，如果沒有：
```bash
brew install python-tk
```

### 問題 5: matplotlib 顯示問題

**錯誤訊息**: 圖表無法顯示或 `backend` 相關錯誤

**解決方法**:
```bash
# 安裝額外的圖形後端
pip install PyQt5

# 或設定環境變數
export MPLBACKEND=TkAgg
```

### 問題 6: 資料庫連線失敗

**錯誤訊息**: `could not connect to server` 或 `authentication failed`

**解決方法**:
1. 確認 PostgreSQL 服務正在運行
2. 檢查防火牆設定
3. 驗證資料庫連線參數
4. 檢查使用者權限

### 問題 7: 權限錯誤

**錯誤訊息**: `Permission denied` 或 `Access is denied`

**解決方法**:
1. 使用管理員權限執行
2. 檢查檔案和資料夾權限
3. 使用虛擬環境避免系統權限問題

## 解除安裝

### 1. 停止應用程式

確保應用程式已完全關閉。

### 2. 移除虛擬環境（如果使用）

```bash
# 停用虛擬環境
deactivate

# 刪除虛擬環境資料夾
rm -rf taiwan_railway_env  # macOS/Linux
rmdir /s taiwan_railway_env  # Windows
```

### 3. 移除應用程式檔案

刪除整個專案資料夾。

### 4. 清理環境變數

移除設定的環境變數或刪除 `.env` 檔案。

### 5. 移除 Python 套件（如果使用 pip 安裝）

```bash
pip uninstall taiwan-railway-gui
```

## 開發環境設定

如果您想要參與開發或修改程式碼：

### 1. 安裝開發相依套件

```bash
pip install -r requirements-dev.txt
```

### 2. 安裝 pre-commit hooks

```bash
pre-commit install
```

### 3. 執行程式碼品質檢查

```bash
# 程式碼格式化
black taiwan_railway_gui/

# 程式碼檢查
flake8 taiwan_railway_gui/

# 型別檢查
mypy taiwan_railway_gui/
```

### 4. 執行測試

```bash
# 執行所有測試
pytest

# 執行測試並產生覆蓋率報告
pytest --cov=taiwan_railway_gui
```

---

**版本**: 1.0.0
**最後更新**: 2024年1月
**文件語言**: 繁體中文

如果您在安裝過程中遇到任何問題，請參考 [使用者手冊](USER_MANUAL.md) 中的故障排除章節，或聯絡技術支援。