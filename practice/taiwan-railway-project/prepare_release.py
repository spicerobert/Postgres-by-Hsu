#!/usr/bin/env python3
"""
發布準備工具

這個腳本會自動執行發布前的所有準備工作，包括：
1. 清理臨時檔案
2. 更新版本資訊
3. 生成發布清單
4. 創建發布套件
5. 執行最終檢查

執行方式：
    python prepare_release.py [version]

範例：
    python prepare_release.py 1.0.0

作者: Taiwan Railway GUI Team
版本: 1.0.0
日期: 2025-07-28
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import json


class ReleasePreparationTool:
    """發布準備工具"""

    def __init__(self, version: str = "1.0.0"):
        """初始化發布準備工具"""
        self.version = version
        self.project_root = Path(__file__).parent
        self.release_dir = self.project_root / "release"
        self.build_dir = self.project_root / "build"

    def prepare_release(self):
        """準備發布"""
        print(f"🚀 準備發布台鐵車站資訊查詢系統 v{self.version}")
        print("=" * 60)

        # 1. 清理舊檔案
        self.clean_old_files()

        # 2. 創建發布目錄
        self.create_release_directories()

        # 3. 複製核心檔案
        self.copy_core_files()

        # 4. 生成發布資訊
        self.generate_release_info()

        # 5. 創建安裝指令
        self.create_installation_scripts()

        # 6. 打包發布檔案
        self.package_release()

        # 7. 生成發布清單
        self.generate_release_checklist()

        print(f"\n✅ 發布準備完成！")
        print(f"📦 發布檔案位置: {self.release_dir}")

    def clean_old_files(self):
        """清理舊檔案"""
        print("🧹 清理舊檔案...")

        # 清理 __pycache__ 目錄
        for pycache_dir in self.project_root.rglob("__pycache__"):
            if pycache_dir.is_dir():
                shutil.rmtree(pycache_dir)
                print(f"  清理: {pycache_dir}")

        # 清理 .pyc 檔案
        for pyc_file in self.project_root.rglob("*.pyc"):
            pyc_file.unlink()
            print(f"  清理: {pyc_file}")

        # 清理舊的發布檔案
        if self.release_dir.exists():
            shutil.rmtree(self.release_dir)
            print(f"  清理舊發布目錄: {self.release_dir}")

        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print(f"  清理建置目錄: {self.build_dir}")

    def create_release_directories(self):
        """創建發布目錄"""
        print("📁 創建發布目錄...")

        directories = [
            self.release_dir,
            self.release_dir / "taiwan_railway_gui",
            self.release_dir / "docs",
            self.release_dir / "tests",
            self.release_dir / "scripts"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  創建: {directory}")

    def copy_core_files(self):
        """複製核心檔案"""
        print("📋 複製核心檔案...")

        # 核心程式檔案
        core_files = [
            "main.py",
            "requirements.txt",
            "README.md",
            "QUICK_START.md"
        ]

        for file_name in core_files:
            src_file = self.project_root / file_name
            if src_file.exists():
                dst_file = self.release_dir / file_name
                shutil.copy2(src_file, dst_file)
                print(f"  複製: {file_name}")

        # 複製整個 taiwan_railway_gui 目錄
        gui_src = self.project_root / "taiwan_railway_gui"
        gui_dst = self.release_dir / "taiwan_railway_gui"

        if gui_src.exists():
            shutil.copytree(gui_src, gui_dst, dirs_exist_ok=True)
            print(f"  複製目錄: taiwan_railway_gui")

        # 複製文件
        docs_src = self.project_root / "docs"
        docs_dst = self.release_dir / "docs"

        if docs_src.exists():
            shutil.copytree(docs_src, docs_dst, dirs_exist_ok=True)
            print(f"  複製目錄: docs")

        # 複製重要的測試檔案
        important_tests = [
            "test_database_connection.py",
            "final_system_integration_test.py"
        ]

        for test_file in important_tests:
            src_test = self.project_root / test_file
            if src_test.exists():
                dst_test = self.release_dir / "tests" / test_file
                shutil.copy2(src_test, dst_test)
                print(f"  複製測試: {test_file}")

    def generate_release_info(self):
        """生成發布資訊"""
        print("ℹ️  生成發布資訊...")

        release_info = {
            "name": "台鐵車站資訊查詢系統",
            "version": self.version,
            "release_date": datetime.now().isoformat(),
            "description": "一個基於 Python 和 tkinter 的台鐵車站資訊查詢系統",
            "features": [
                "車站搜尋功能",
                "客流量資料查詢",
                "多車站比較分析",
                "圖表視覺化",
                "資料匯出功能"
            ],
            "requirements": [
                "Python 3.8+",
                "tkinter",
                "psycopg2",
                "matplotlib",
                "numpy",
                "pandas"
            ],
            "authors": ["Taiwan Railway GUI Team"],
            "license": "MIT",
            "contact": "台鐵車站資訊查詢系統開發團隊"
        }

        # 儲存 JSON 格式
        with open(self.release_dir / "release_info.json", 'w', encoding='utf-8') as f:
            json.dump(release_info, f, ensure_ascii=False, indent=2)

        # 生成版本資訊檔案
        version_info = f"""# 版本資訊

**軟體名稱:** {release_info['name']}
**版本:** v{self.version}
**發布日期:** {datetime.now().strftime('%Y年%m月%d日')}

## 主要功能

"""

        for feature in release_info['features']:
            version_info += f"- {feature}\n"

        version_info += f"""
## 系統需求

"""

        for requirement in release_info['requirements']:
            version_info += f"- {requirement}\n"

        with open(self.release_dir / "VERSION.md", 'w', encoding='utf-8') as f:
            f.write(version_info)

        print(f"  生成: release_info.json")
        print(f"  生成: VERSION.md")

    def create_installation_scripts(self):
        """創建安裝指令"""
        print("🛠️ 創建安裝指令...")

        # Windows 批次檔
        windows_script = f"""@echo off
echo 安裝台鐵車站資訊查詢系統 v{self.version}
echo ====================================

echo 檢查 Python 版本...
python --version
if errorlevel 1 (
    echo 錯誤: 未找到 Python，請先安裝 Python 3.8 或更高版本
    pause
    exit /b 1
)

echo 安裝相依套件...
pip install -r requirements.txt
if errorlevel 1 (
    echo 錯誤: 套件安裝失敗
    pause
    exit /b 1
)

echo 測試資料庫連線...
python test_database_connection.py

echo 安裝完成！
echo 執行 'python main.py' 來啟動應用程式
pause
"""

        with open(self.release_dir / "scripts" / "install.bat", 'w', encoding='utf-8') as f:
            f.write(windows_script)

        # Unix/Linux/macOS 腳本
        unix_script = f"""#!/bin/bash
echo "安裝台鐵車站資訊查詢系統 v{self.version}"
echo "===================================="

echo "檢查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 未找到 Python3，請先安裝 Python 3.8 或更高版本"
    exit 1
fi

python3 --version

echo "安裝相依套件..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "錯誤: 套件安裝失敗"
    exit 1
fi

echo "測試資料庫連線..."
python3 test_database_connection.py

echo "安裝完成！"
echo "執行 'python3 main.py' 來啟動應用程式"
"""

        with open(self.release_dir / "scripts" / "install.sh", 'w', encoding='utf-8') as f:
            f.write(unix_script)

        # 設定執行權限 (Unix/Linux/macOS)
        try:
            os.chmod(self.release_dir / "scripts" / "install.sh", 0o755)
        except:
            pass  # Windows 可能會失敗，忽略

        print(f"  生成: scripts/install.bat")
        print(f"  生成: scripts/install.sh")

    def package_release(self):
        """打包發布檔案"""
        print("📦 打包發布檔案...")

        # 創建 ZIP 檔案
        zip_filename = f"taiwan_railway_gui_v{self.version}.zip"
        zip_path = self.project_root / zip_filename

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.release_dir.rglob("*"):
                if file_path.is_file():
                    # 計算相對路徑
                    relative_path = file_path.relative_to(self.release_dir)
                    zipf.write(file_path, relative_path)

        print(f"  打包完成: {zip_filename}")
        print(f"  檔案大小: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")

    def generate_release_checklist(self):
        """生成發布清單"""
        print("📋 生成發布清單...")

        checklist = f"""# 台鐵車站資訊查詢系統 v{self.version} - 發布清單

## 發布前檢查

### 程式碼品質
- [ ] 所有程式碼已通過語法檢查
- [ ] 程式碼符合 PEP 8 規範
- [ ] 所有函數和類別都有適當的文件字串
- [ ] 移除了所有調試程式碼和註解

### 測試
- [ ] 所有單元測試通過
- [ ] 所有整合測試通過
- [ ] GUI 功能測試完成
- [ ] 資料庫連線測試成功
- [ ] 效能測試達到預期

### 文件
- [ ] README.md 已更新
- [ ] 使用者手冊完整
- [ ] 安裝指南詳細
- [ ] 開發者文件齊全
- [ ] API 文件正確

### 功能驗證
- [ ] 車站搜尋功能正常
- [ ] 客流量查詢功能正常
- [ ] 車站比較功能正常
- [ ] 圖表生成功能正常
- [ ] 資料匯出功能正常
- [ ] 錯誤處理機制完善

### 相依性
- [ ] requirements.txt 已更新
- [ ] 所有必要套件版本正確
- [ ] 相容性測試完成

### 發布檔案
- [ ] 所有核心檔案已包含
- [ ] 安裝腳本測試成功
- [ ] 壓縮檔案完整
- [ ] 版本資訊正確

## 發布後檢查

- [ ] 下載檔案測試
- [ ] 安裝流程測試
- [ ] 基本功能測試
- [ ] 使用者回饋收集

## 發布資訊

**版本:** v{self.version}
**發布日期:** {datetime.now().strftime('%Y年%m月%d日')}
**負責人:** Taiwan Railway GUI Team

## 聯絡資訊

如有問題請聯絡開發團隊。

---
*此清單由發布準備工具自動生成*
"""

        with open(self.release_dir / "RELEASE_CHECKLIST.md", 'w', encoding='utf-8') as f:
            f.write(checklist)

        print(f"  生成: RELEASE_CHECKLIST.md")


def main():
    """主程式"""
    version = "1.0.0"

    # 從命令列參數取得版本號
    if len(sys.argv) > 1:
        version = sys.argv[1]

    try:
        tool = ReleasePreparationTool(version)
        tool.prepare_release()

    except KeyboardInterrupt:
        print("\n發布準備被使用者中斷")
        sys.exit(1)
    except Exception as e:
        print(f"發布準備錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
