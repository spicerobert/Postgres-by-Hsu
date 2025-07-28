#!/usr/bin/env python3
"""
系統驗證和發布準備工具

這個腳本執行完整的系統驗證流程，確保所有模組正確整合，
並準備系統發布所需的文件和檢查項目。

主要功能：
1. 檢查專案結構完整性
2. 驗證所有模組的匯入和相依性
3. 執行自動化測試套件
4. 生成發布檢查清單
5. 創建發布版本

執行方式：
    python system_verification.py

作者: Taiwan Railway GUI Team
版本: 1.0.0
日期: 2025-07-28
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple
import importlib.util


class SystemVerificationTool:
    """系統驗證工具"""

    def __init__(self):
        """初始化驗證工具"""
        self.project_root = Path(__file__).parent
        self.verification_results = {}
        self.issues_found = []

    def run_verification(self):
        """執行完整系統驗證"""
        print("🔍 台鐵車站資訊查詢系統 - 系統驗證")
        print("=" * 60)

        # 1. 檢查專案結構
        self.check_project_structure()

        # 2. 檢查相依性
        self.check_dependencies()

        # 3. 檢查程式碼品質
        self.check_code_quality()

        # 4. 執行測試
        self.run_tests()

        # 5. 檢查文件完整性
        self.check_documentation()

        # 6. 生成發布報告
        self.generate_release_report()

    def check_project_structure(self):
        """檢查專案結構完整性"""
        print("\n📁 檢查專案結構...")

        required_structure = {
            "taiwan_railway_gui/": "主要程式套件",
            "taiwan_railway_gui/__init__.py": "套件初始化檔案",
            "taiwan_railway_gui/models/": "資料模型目錄",
            "taiwan_railway_gui/dao/": "資料存取層目錄",
            "taiwan_railway_gui/gui/": "GUI 介面目錄",
            "taiwan_railway_gui/services/": "服務層目錄",
            "taiwan_railway_gui/utils/": "工具程式目錄",
            "taiwan_railway_gui/config.py": "配置檔案",
            "tests/": "測試目錄",
            "docs/": "文件目錄",
            "main.py": "主程式",
            "requirements.txt": "相依性清單",
            "README.md": "專案說明文件"
        }

        missing_items = []
        existing_items = []

        for item, description in required_structure.items():
            item_path = self.project_root / item
            if item_path.exists():
                existing_items.append(f"✓ {item} - {description}")
            else:
                missing_items.append(f"✗ {item} - {description}")
                self.issues_found.append(f"缺少必要檔案/目錄: {item}")

        print(f"  結構檢查: {len(existing_items)}/{len(required_structure)} 項目存在")

        if missing_items:
            print("  缺少的項目:")
            for item in missing_items:
                print(f"    {item}")

        self.verification_results['project_structure'] = {
            'total': len(required_structure),
            'existing': len(existing_items),
            'missing': missing_items
        }

    def check_dependencies(self):
        """檢查相依性"""
        print("\n📦 檢查相依性...")

        required_packages = [
            'tkinter',
            'psycopg2',
            'matplotlib',
            'numpy',
            'pandas'
        ]

        available_packages = []
        missing_packages = []

        for package in required_packages:
            try:
                if package == 'tkinter':
                    import tkinter
                elif package == 'psycopg2':
                    import psycopg2
                elif package == 'matplotlib':
                    import matplotlib
                elif package == 'numpy':
                    import numpy
                elif package == 'pandas':
                    import pandas

                available_packages.append(package)
                print(f"  ✓ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ✗ {package}")
                self.issues_found.append(f"缺少套件: {package}")

        self.verification_results['dependencies'] = {
            'available': available_packages,
            'missing': missing_packages
        }

    def check_code_quality(self):
        """檢查程式碼品質"""
        print("\n🔧 檢查程式碼品質...")

        # 檢查 Python 檔案的基本語法
        python_files = list(self.project_root.rglob("*.py"))
        syntax_errors = []

        for py_file in python_files:
            if "test" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    compile(content, str(py_file), 'exec')
                    print(f"  ✓ {py_file.name}")
            except SyntaxError as e:
                syntax_errors.append(f"{py_file}: {e}")
                print(f"  ✗ {py_file.name} - 語法錯誤")
                self.issues_found.append(f"語法錯誤: {py_file}")
            except Exception as e:
                print(f"  ⚠ {py_file.name} - 無法檢查: {e}")

        self.verification_results['code_quality'] = {
            'total_files': len(python_files),
            'syntax_errors': syntax_errors
        }

    def run_tests(self):
        """執行測試"""
        print("\n🧪 執行測試...")

        test_files = list(self.project_root.glob("test_*.py"))
        test_results = {}

        for test_file in test_files:
            try:
                print(f"  執行測試: {test_file.name}")
                result = subprocess.run(
                    [sys.executable, str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    test_results[test_file.name] = "PASS"
                    print(f"    ✓ 通過")
                else:
                    test_results[test_file.name] = "FAIL"
                    print(f"    ✗ 失敗")
                    self.issues_found.append(f"測試失敗: {test_file.name}")

            except subprocess.TimeoutExpired:
                test_results[test_file.name] = "TIMEOUT"
                print(f"    ⏰ 逾時")
                self.issues_found.append(f"測試逾時: {test_file.name}")
            except Exception as e:
                test_results[test_file.name] = "ERROR"
                print(f"    ❌ 錯誤: {e}")
                self.issues_found.append(f"測試錯誤: {test_file.name}")

        self.verification_results['tests'] = test_results

    def check_documentation(self):
        """檢查文件完整性"""
        print("\n📖 檢查文件完整性...")

        required_docs = {
            "README.md": "專案說明",
            "docs/USER_MANUAL.md": "使用者手冊",
            "docs/INSTALLATION_GUIDE.md": "安裝指南",
            "docs/DEVELOPER_GUIDE.md": "開發者指南",
            "docs/CODE_DOCUMENTATION.md": "程式碼文件"
        }

        existing_docs = []
        missing_docs = []

        for doc_path, description in required_docs.items():
            doc_file = self.project_root / doc_path
            if doc_file.exists():
                # 檢查檔案大小（確保不是空檔案）
                if doc_file.stat().st_size > 100:  # 至少 100 bytes
                    existing_docs.append(f"✓ {doc_path} - {description}")
                else:
                    missing_docs.append(f"⚠ {doc_path} - {description} (檔案太小)")
            else:
                missing_docs.append(f"✗ {doc_path} - {description}")
                self.issues_found.append(f"缺少文件: {doc_path}")

        print(f"  文件檢查: {len(existing_docs)}/{len(required_docs)} 文件完整")

        self.verification_results['documentation'] = {
            'existing': existing_docs,
            'missing': missing_docs
        }

    def generate_release_report(self):
        """生成發布報告"""
        print("\n📋 生成發布報告...")

        # 計算整體完成度
        total_checks = 0
        passed_checks = 0

        for category, results in self.verification_results.items():
            if category == 'project_structure':
                total_checks += results['total']
                passed_checks += results['existing']
            elif category == 'dependencies':
                total_checks += len(results['available']) + len(results['missing'])
                passed_checks += len(results['available'])
            elif category == 'tests':
                total_checks += len(results)
                passed_checks += len([r for r in results.values() if r == 'PASS'])
            elif category == 'documentation':
                total_checks += len(results['existing']) + len(results['missing'])
                passed_checks += len(results['existing'])

        completion_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        # 生成報告
        report = self.create_release_report(completion_rate)

        # 儲存報告
        with open("RELEASE_VERIFICATION_REPORT.md", 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"  📄 發布報告已儲存: RELEASE_VERIFICATION_REPORT.md")
        print(f"  📊 系統完成度: {completion_rate:.1f}%")

        # 顯示發布建議
        self.show_release_recommendation(completion_rate)

    def create_release_report(self, completion_rate: float) -> str:
        """創建發布報告"""
        report = f"""# 台鐵車站資訊查詢系統 - 發布驗證報告

**驗證日期:** {self.get_current_timestamp()}
**系統完成度:** {completion_rate:.1f}%

## 驗證摘要

### 專案結構
- 總項目: {self.verification_results.get('project_structure', {}).get('total', 0)}
- 完成項目: {self.verification_results.get('project_structure', {}).get('existing', 0)}

### 相依性檢查
- 可用套件: {len(self.verification_results.get('dependencies', {}).get('available', []))}
- 缺少套件: {len(self.verification_results.get('dependencies', {}).get('missing', []))}

### 測試結果
"""

        if 'tests' in self.verification_results:
            test_results = self.verification_results['tests']
            for test_name, result in test_results.items():
                status = "✅" if result == "PASS" else "❌"
                report += f"- {status} {test_name}: {result}\n"

        report += f"""
### 發現的問題

"""

        if self.issues_found:
            for issue in self.issues_found:
                report += f"- ⚠️ {issue}\n"
        else:
            report += "- 🎉 未發現重大問題\n"

        report += f"""
## 發布建議

"""

        if completion_rate >= 95:
            report += "✅ **建議發布** - 系統已準備就緒，可以進行正式發布。\n"
        elif completion_rate >= 85:
            report += "⚠️ **有條件發布** - 系統基本完成，建議修正小問題後發布。\n"
        elif completion_rate >= 70:
            report += "🔄 **需要改善** - 系統需要進一步改善，不建議目前發布。\n"
        else:
            report += "❌ **不建議發布** - 系統存在重大問題，需要大幅修正。\n"

        return report

    def show_release_recommendation(self, completion_rate: float):
        """顯示發布建議"""
        print("\n🎯 發布建議:")

        if completion_rate >= 95:
            print("  ✅ 系統已準備就緒，建議進行正式發布")
            print("  📦 可以開始準備發布版本")
        elif completion_rate >= 85:
            print("  ⚠️ 系統基本完成，建議修正問題後發布")
            print("  🔧 需要修正的問題:")
            for issue in self.issues_found[:5]:  # 顯示前 5 個問題
                print(f"     • {issue}")
        elif completion_rate >= 70:
            print("  🔄 系統需要進一步改善")
            print("  ❌ 不建議目前發布")
        else:
            print("  ❌ 系統存在重大問題，需要大幅修正")
            print("  🚫 強烈不建議發布")

        print(f"\n📊 總計發現 {len(self.issues_found)} 個問題需要處理")

    def get_current_timestamp(self) -> str:
        """取得目前時間戳記"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """主程式"""
    try:
        verifier = SystemVerificationTool()
        verifier.run_verification()

    except KeyboardInterrupt:
        print("\n驗證被使用者中斷")
        sys.exit(1)
    except Exception as e:
        print(f"驗證過程發生錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
