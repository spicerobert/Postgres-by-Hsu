# 台鐵車站資訊查詢系統 - 開發者指南

## 目錄

1. [專案概述](#專案概述)
2. [架構設計](#架構設計)
3. [開發環境設定](#開發環境設定)
4. [程式碼結構](#程式碼結構)
5. [API 文件](#api-文件)
6. [開發規範](#開發規範)
7. [測試指南](#測試指南)
8. [部署指南](#部署指南)
9. [貢獻指南](#貢獻指南)

## 專案概述

台鐵車站資訊查詢系統是一個基於 Python tkinter 的桌面應用程式，採用分層架構設計，提供車站資訊查詢、客流量分析和資料視覺化功能。

### 技術堆疊

- **前端**: Python tkinter + ttk
- **後端**: Python 3.8+
- **資料庫**: PostgreSQL 12+
- **視覺化**: matplotlib
- **測試**: pytest
- **程式碼品質**: black, flake8, mypy

### 設計原則

- **分層架構**: 清楚分離 GUI、業務邏輯和資料存取層
- **模組化設計**: 每個功能模組獨立，便於維護和測試
- **介面導向**: 使用抽象介面定義系統邊界
- **錯誤處理**: 統一的錯誤處理機制
- **效能最佳化**: 非同步處理、快取機制、記憶體管理

## 架構設計

### 整體架構

```
┌─────────────────────────────────────┐
│           GUI Layer                 │
│  ┌─────────────────────────────────┐│
│  │ MainWindow                      ││
│  │ ├── StationSearchTab            ││
│  │ ├── PassengerFlowTab            ││
│  │ ├── ComparisonTab               ││
│  │ └── ChartTab                    ││
│  └─────────────────────────────────┘│
├─────────────────────────────────────┤
│         Service Layer               │
│  ┌─────────────────────────────────┐│
│  │ ErrorHandler                    ││
│  │ AsyncManager                    ││
│  │ CacheManager                    ││
│  │ ValidationService               ││
│  │ ExportManager                   ││
│  └─────────────────────────────────┘│
├─────────────────────────────────────┤
│        Data Access Layer           │
│  ┌─────────────────────────────────┐│
│  │ DatabaseManager                 ││
│  │ StationDAO                      ││
│  │ PassengerFlowDAO                ││
│  └─────────────────────────────────┘│
├─────────────────────────────────────┤
│         Model Layer                 │
│  ┌─────────────────────────────────┐│
│  │ Station                         ││
│  │ PassengerFlow                   ││
│  │ StationStatistics               ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

### 核心元件

#### 1. GUI Layer (taiwan_railway_gui/gui/)
- **MainWindow**: 主視窗管理器
- **BaseTab**: 分頁基礎類別
- **各功能分頁**: 實作具體功能的 GUI 元件

#### 2. Service Layer (taiwan_railway_gui/services/)
- **ErrorHandler**: 統一錯誤處理
- **AsyncManager**: 非同步任務管理
- **CacheManager**: 資料快取管理
- **ValidationService**: 資料驗證服務
- **ExportManager**: 資料匯出服務

#### 3. Data Access Layer (taiwan_railway_gui/dao/)
- **DatabaseManager**: 資料庫連線管理
- **StationDAO**: 車站資料存取
- **PassengerFlowDAO**: 客流量資料存取

#### 4. Model Layer (taiwan_railway_gui/models/)
- **Station**: 車站資料模型
- **PassengerFlow**: 客流量資料模型
- **StationStatistics**: 統計資料模型

## 開發環境設定

### 1. 克隆專案

```bash
git clone https://github.com/your-repo/taiwan-railway-gui.git
cd taiwan-railway-gui
```

### 2. 建立虛擬環境

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 3. 安裝開發相依套件

```bash
pip install -r requirements-dev.txt
```

### 4. 設定 pre-commit hooks

```bash
pre-commit install
```

### 5. 設定 IDE

#### VS Code 設定 (.vscode/settings.json)

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm 設定

1. 設定 Python 解釋器為虛擬環境中的 Python
2. 啟用 flake8 和 mypy 檢查
3. 設定 black 為程式碼格式化工具
4. 設定 pytest 為測試執行器

## 程式碼結構

```
taiwan_railway_gui/
├── __init__.py                 # 套件初始化
├── config.py                   # 應用程式配置
├── interfaces.py               # 介面定義
├── dao/                        # 資料存取層
│   ├── __init__.py
│   ├── database_manager.py     # 資料庫管理
│   ├── station_dao.py          # 車站資料存取
│   └── passenger_flow_dao.py   # 客流量資料存取
├── models/                     # 資料模型
│   ├── __init__.py
│   ├── station.py              # 車站模型
│   └── passenger_flow.py       # 客流量模型
├── services/                   # 服務層
│   ├── __init__.py
│   ├── error_handler.py        # 錯誤處理
│   ├── async_manager.py        # 非同步管理
│   ├── cache_manager.py        # 快取管理
│   ├── validation.py           # 資料驗證
│   ├── export_manager.py       # 資料匯出
│   └── pagination_manager.py   # 分頁管理
├── gui/                        # GUI 層
│   ├── __init__.py
│   ├── main_window.py          # 主視窗
│   ├── base_tab.py             # 分頁基礎類別
│   ├── station_search_tab.py   # 車站搜尋分頁
│   ├── passenger_flow_tab.py   # 客流量查詢分頁
│   ├── comparison_tab.py       # 車站比較分頁
│   ├── chart_tab.py            # 圖表視覺化分頁
│   ├── styles.py               # 樣式管理
│   ├── accessibility.py        # 無障礙功能
│   ├── visual_feedback.py      # 視覺回饋
│   ├── user_feedback.py        # 使用者回饋
│   └── platform_consistency.py # 跨平台一致性
└── utils/                      # 工具模組
    ├── __init__.py
    ├── gui_helpers.py          # GUI 輔助函數
    └── memory_manager.py       # 記憶體管理
```

## API 文件

### 核心介面

#### DatabaseManagerInterface

```python
class DatabaseManagerInterface(ABC):
    """資料庫管理介面"""

    @abstractmethod
    def get_connection(self):
        """取得資料庫連線"""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: tuple = None):
        """執行查詢"""
        pass
```

#### StationDAOInterface

```python
class StationDAOInterface(ABC):
    """車站資料存取介面"""

    @abstractmethod
    def search_stations(self, query: str) -> List[Station]:
        """搜尋車站"""
        pass

    @abstractmethod
    def get_station_by_code(self, code: str) -> Optional[Station]:
        """根據代碼取得車站"""
        pass
```

### 主要類別

#### Station 模型

```python
@dataclass
class Station:
    """車站資料模型"""
    station_code: str
    station_name: str
    address: str
    phone: str
    gps_lat: float
    gps_lng: float
    has_bike_rental: bool

    @property
    def coordinates(self) -> tuple[float, float]:
        """取得座標元組"""
        return (self.gps_lat, self.gps_lng)

    def distance_to(self, other_station: 'Station') -> float:
        """計算到另一個車站的距離"""
        pass
```

#### AsyncManager

```python
class AsyncManager:
    """非同步管理器"""

    def submit_task(self, task_func: Callable,
                   callback: Callable = None,
                   error_callback: Callable = None) -> str:
        """提交非同步任務"""
        pass

    def cancel_task(self, task_id: str) -> bool:
        """取消任務"""
        pass
```

## 開發規範

### 程式碼風格

#### 1. 命名規範

- **類別**: PascalCase (例: `StationDAO`)
- **函數和變數**: snake_case (例: `get_station_by_code`)
- **常數**: UPPER_SNAKE_CASE (例: `MAX_STATIONS`)
- **私有成員**: 前綴底線 (例: `_private_method`)

#### 2. 文件字串

所有公開的類別和函數都必須有文件字串：

```python
def search_stations(self, query: str) -> List[Station]:
    """
    搜尋車站

    Args:
        query: 搜尋查詢字串

    Returns:
        List[Station]: 匹配的車站清單

    Raises:
        ValueError: 當查詢字串無效時
        DatabaseError: 當資料庫查詢失敗時
    """
    pass
```

#### 3. 型別提示

所有函數都應該包含型別提示：

```python
from typing import List, Optional, Dict, Any

def process_data(data: List[Dict[str, Any]]) -> Optional[str]:
    """處理資料"""
    pass
```

#### 4. 錯誤處理

使用統一的錯誤處理機制：

```python
from taiwan_railway_gui.services.error_handler import handle_error, ErrorCategory

try:
    result = database_operation()
except Exception as e:
    handle_error(e, context={'operation': 'database_query'},
                category=ErrorCategory.DATABASE)
```

### 程式碼品質工具

#### 1. Black (程式碼格式化)

```bash
black taiwan_railway_gui/
```

#### 2. Flake8 (程式碼檢查)

```bash
flake8 taiwan_railway_gui/
```

#### 3. MyPy (型別檢查)

```bash
mypy taiwan_railway_gui/
```

#### 4. isort (import 排序)

```bash
isort taiwan_railway_gui/
```

### Git 工作流程

#### 1. 分支命名

- **功能分支**: `feature/功能名稱`
- **修復分支**: `fix/問題描述`
- **文件分支**: `docs/文件類型`

#### 2. 提交訊息格式

```
類型(範圍): 簡短描述

詳細描述（可選）

相關問題: #123
```

類型：
- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文件更新
- `style`: 程式碼格式調整
- `refactor`: 程式碼重構
- `test`: 測試相關
- `chore`: 其他雜項

## 測試指南

### 測試結構

```
tests/
├── unit/                       # 單元測試
│   ├── test_models.py
│   ├── test_dao.py
│   └── test_services.py
├── integration/                # 整合測試
│   ├── test_database.py
│   └── test_gui.py
└── e2e/                       # 端到端測試
    └── test_workflows.py
```

### 測試類型

#### 1. 單元測試

測試個別函數和類別：

```python
import pytest
from taiwan_railway_gui.models.station import Station

class TestStation:
    def test_station_creation(self):
        """測試車站建立"""
        station = Station(
            station_code="1000",
            station_name="台北車站",
            address="台北市中正區北平西路3號",
            phone="02-2371-3558",
            gps_lat=25.0478,
            gps_lng=121.5170,
            has_bike_rental=True
        )

        assert station.station_code == "1000"
        assert station.station_name == "台北車站"
        assert station.has_bike_rental is True

    def test_coordinates_property(self):
        """測試座標屬性"""
        station = Station(...)
        coords = station.coordinates
        assert coords == (25.0478, 121.5170)
```

#### 2. 整合測試

測試元件間的互動：

```python
import pytest
from taiwan_railway_gui.dao.station_dao import StationDAO
from taiwan_railway_gui.dao.database_manager import get_database_manager

class TestStationDAO:
    @pytest.fixture
    def station_dao(self):
        """建立 StationDAO 實例"""
        db_manager = get_database_manager()
        return StationDAO(db_manager)

    def test_search_stations(self, station_dao):
        """測試車站搜尋"""
        results = station_dao.search_stations("台北")
        assert len(results) > 0
        assert all("台北" in station.station_name for station in results)
```

#### 3. GUI 測試

測試使用者介面：

```python
import tkinter as tk
from taiwan_railway_gui.gui.station_search_tab import StationSearchTab

class TestStationSearchTab:
    def setup_method(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.tab = StationSearchTab(self.root)

    def teardown_method(self):
        """清理測試環境"""
        self.root.destroy()

    def test_search_functionality(self):
        """測試搜尋功能"""
        # 模擬使用者輸入
        self.tab.search_entry.insert(0, "台北")
        self.tab.on_search()

        # 驗證結果
        assert len(self.tab.results_listbox.get(0, tk.END)) > 0
```

### 執行測試

```bash
# 執行所有測試
pytest

# 執行特定測試檔案
pytest tests/unit/test_models.py

# 執行特定測試類別
pytest tests/unit/test_models.py::TestStation

# 執行特定測試方法
pytest tests/unit/test_models.py::TestStation::test_station_creation

# 產生覆蓋率報告
pytest --cov=taiwan_railway_gui --cov-report=html
```

### 測試配置

#### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    unit: 單元測試
    integration: 整合測試
    gui: GUI 測試
    slow: 執行時間較長的測試
```

## 部署指南

### 1. 建立發布版本

```bash
# 更新版本號
# 編輯 taiwan_railway_gui/__init__.py 中的 __version__

# 建立標籤
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 2. 打包應用程式

#### 使用 PyInstaller

```bash
# 安裝 PyInstaller
pip install pyinstaller

# 建立執行檔
pyinstaller --onefile --windowed main.py

# 或使用設定檔
pyinstaller taiwan_railway_gui.spec
```

#### PyInstaller 設定檔 (taiwan_railway_gui.spec)

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('taiwan_railway_gui/gui/icons', 'icons'),
        ('docs', 'docs'),
    ],
    hiddenimports=[
        'tkinter',
        'psycopg2',
        'matplotlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='taiwan_railway_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

### 3. 建立安裝程式

#### Windows (使用 NSIS)

建立 `installer.nsi` 檔案：

```nsis
!define APP_NAME "台鐵車站資訊查詢系統"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Your Company"
!define APP_EXE "taiwan_railway_gui.exe"

Name "${APP_NAME}"
OutFile "Taiwan_Railway_GUI_Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File "dist\${APP_EXE}"
    File /r "docs"

    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
SectionEnd
```

#### macOS (使用 create-dmg)

```bash
# 建立 .app 套件
pyinstaller --onefile --windowed --name "Taiwan Railway GUI" main.py

# 建立 DMG
create-dmg \
  --volname "Taiwan Railway GUI" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --app-drop-link 425 120 \
  "Taiwan_Railway_GUI.dmg" \
  "dist/"
```

## 貢獻指南

### 1. 回報問題

使用 GitHub Issues 回報問題時，請包含：

- 作業系統和版本
- Python 版本
- 應用程式版本
- 詳細的錯誤訊息
- 重現步驟
- 預期行為

### 2. 提交功能請求

功能請求應包含：

- 功能描述
- 使用案例
- 預期效益
- 可能的實作方式

### 3. 提交程式碼

1. Fork 專案
2. 建立功能分支
3. 撰寫程式碼和測試
4. 確保所有測試通過
5. 提交 Pull Request

#### Pull Request 檢查清單

- [ ] 程式碼遵循專案風格指南
- [ ] 包含適當的測試
- [ ] 所有測試通過
- [ ] 文件已更新
- [ ] 提交訊息清楚描述變更

### 4. 程式碼審查

所有 Pull Request 都需要經過程式碼審查：

- 至少一位維護者的批准
- 所有 CI 檢查通過
- 沒有合併衝突

---

**版本**: 1.0.0
**最後更新**: 2024年1月
**文件語言**: 繁體中文

如需更多資訊，請參考專案的其他文件或聯絡開發團隊。