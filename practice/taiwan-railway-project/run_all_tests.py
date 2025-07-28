#!/usr/bin/env python3
"""
自動化測試執行器

這個腳本會自動執行所有相關的測試，包括單元測試、整合測試和系統測試，
並生成完整的測試報告。

功能：
1. 自動發現和執行所有測試檔案
2. 執行最終系統整合測試
3. 生成測試覆蓋率報告
4. 統計測試結果和建議

執行方式：
    python run_all_tests.py

作者: Taiwan Railway GUI Team
版本: 1.0.0
日期: 2025-07-28
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Tuple


class TestRunner:
    """測試執行器"""

    def __init__(self):
        """初始化測試執行器"""
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = time.time()

    def run_all_tests(self):
        """執行所有測試"""
        print("🧪 台鐵車站資訊查詢系統 - 自動化測試執行器")
        print("=" * 60)
        print(f"開始時間: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 1. 執行單元測試
        self.run_unit_tests()

        # 2. 執行整合測試
        self.run_integration_tests()

        # 3. 執行 GUI 測試
        self.run_gui_tests()

        # 4. 執行系統測試
        self.run_system_tests()

        # 5. 執行最終整合測試
        self.run_final_integration_test()

        # 6. 生成測試報告
        self.generate_test_report()

    def run_unit_tests(self):
        """執行單元測試"""
        print("1️⃣ 執行單元測試")
        print("-" * 30)

        unit_test_files = [
            "tests/test_models.py",
            "tests/test_config.py",
            "tests/test_dao.py"
        ]

        for test_file in unit_test_files:
            self.run_single_test(test_file, "單元測試")

        print()

    def run_integration_tests(self):
        """執行整合測試"""
        print("2️⃣ 執行整合測試")
        print("-" * 30)

        integration_test_files = [
            "tests/test_integration_database.py",
            "tests/test_integration_end_to_end.py",
            "tests/run_integration_tests.py"
        ]

        for test_file in integration_test_files:
            self.run_single_test(test_file, "整合測試")

        print()

    def run_gui_tests(self):
        """執行 GUI 測試"""
        print("3️⃣ 執行 GUI 測試")
        print("-" * 30)

        gui_test_files = [
            "test_gui.py",
            "test_station_search_gui.py",
            "test_passenger_flow_gui.py",
            "test_comparison_gui.py",
            "test_chart_gui.py",
            "test_ui_consistency.py"
        ]

        for test_file in gui_test_files:
            self.run_single_test(test_file, "GUI 測試")

        print()

    def run_system_tests(self):
        """執行系統測試"""
        print("4️⃣ 執行系統測試")
        print("-" * 30)

        system_test_files = [
            "test_database_connection.py",
            "tests/test_performance.py",
            "tests/test_error_handling.py"
        ]

        for test_file in system_test_files:
            self.run_single_test(test_file, "系統測試")

        print()

    def run_final_integration_test(self):
        """執行最終整合測試"""
        print("5️⃣ 執行最終整合測試")
        print("-" * 30)

        self.run_single_test("final_system_integration_test.py", "最終整合測試")
        print()

    def run_single_test(self, test_file: str, test_category: str):
        """執行單一測試檔案"""
        test_path = self.project_root / test_file

        if not test_path.exists():
            print(f"  ⚠️  {test_file} - 檔案不存在")
            self.record_test_result(test_file, False, "檔案不存在", test_category)
            return

        try:
            print(f"  🔄 執行 {test_file}...")

            # 執行測試
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=60,  # 60 秒逾時
                cwd=self.project_root
            )

            if result.returncode == 0:
                print(f"    ✅ 通過")
                self.record_test_result(test_file, True, "測試通過", test_category)
            else:
                print(f"    ❌ 失敗")
                error_message = result.stderr[:200] if result.stderr else "未知錯誤"
                self.record_test_result(test_file, False, error_message, test_category)

        except subprocess.TimeoutExpired:
            print(f"    ⏰ 逾時")
            self.record_test_result(test_file, False, "測試逾時", test_category)
        except Exception as e:
            print(f"    ❌ 執行錯誤: {e}")
            self.record_test_result(test_file, False, f"執行錯誤: {e}", test_category)

    def record_test_result(self, test_file: str, passed: bool, message: str, category: str):
        """記錄測試結果"""
        self.total_tests += 1

        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

        self.test_results[test_file] = {
            'passed': passed,
            'message': message,
            'category': category,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def generate_test_report(self):
        """生成測試報告"""
        end_time = time.time()
        duration = end_time - self.start_time

        print("📊 測試執行完成")
        print("=" * 60)
        print(f"執行時間: {duration:.2f} 秒")
        print(f"總測試數: {self.total_tests}")
        print(f"通過測試: {self.passed_tests}")
        print(f"失敗測試: {self.failed_tests}")

        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"成功率: {success_rate:.1f}%")

        # 按分類統計
        print("\n📋 分類統計:")
        categories = {}
        for test_file, result in self.test_results.items():
            category = result['category']
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0}
            categories[category]['total'] += 1
            if result['passed']:
                categories[category]['passed'] += 1

        for category, stats in categories.items():
            rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {category}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")

        # 失敗的測試
        if self.failed_tests > 0:
            print(f"\n❌ 失敗的測試 ({self.failed_tests} 個):")
            for test_file, result in self.test_results.items():
                if not result['passed']:
                    print(f"  • {test_file}: {result['message'][:100]}")

        # 生成 Markdown 報告
        self.save_test_report()

        # 最終建議
        print(f"\n🎯 測試建議:")
        if success_rate >= 95:
            print("  ✅ 測試覆蓋率極佳，系統已準備發布")
        elif success_rate >= 85:
            print("  🟡 大部分測試通過，建議修正失敗項目")
        elif success_rate >= 70:
            print("  🟠 測試結果普通，需要改善")
        else:
            print("  🔴 測試結果不佳，需要大幅修正")

    def save_test_report(self):
        """儲存測試報告到檔案"""
        report_content = self.create_markdown_report()

        with open("TEST_EXECUTION_REPORT.md", 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\n📄 測試報告已儲存: TEST_EXECUTION_REPORT.md")

    def create_markdown_report(self) -> str:
        """創建 Markdown 格式的測試報告"""
        end_time = time.time()
        duration = end_time - self.start_time
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0

        report = f"""# 台鐵車站資訊查詢系統 - 測試執行報告

**執行時間:** {time.strftime('%Y-%m-%d %H:%M:%S')}
**測試時長:** {duration:.2f} 秒
**成功率:** {success_rate:.1f}%

## 測試統計

| 項目 | 數量 |
|------|------|
| 總測試數 | {self.total_tests} |
| 通過測試 | {self.passed_tests} |
| 失敗測試 | {self.failed_tests} |

## 分類統計

"""

        # 按分類統計
        categories = {}
        for test_file, result in self.test_results.items():
            category = result['category']
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0, 'tests': []}
            categories[category]['total'] += 1
            categories[category]['tests'].append((test_file, result))
            if result['passed']:
                categories[category]['passed'] += 1

        for category, stats in categories.items():
            rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            report += f"### {category}\n\n"
            report += f"- 通過率: {rate:.1f}% ({stats['passed']}/{stats['total']})\n\n"

            for test_file, result in stats['tests']:
                status = "✅" if result['passed'] else "❌"
                report += f"- {status} `{test_file}`: {result['message']}\n"

            report += "\n"

        # 建議
        report += "## 測試建議\n\n"
        if success_rate >= 95:
            report += "✅ **優秀** - 測試覆蓋率極佳，系統已準備發布\n"
        elif success_rate >= 85:
            report += "🟡 **良好** - 大部分測試通過，建議修正失敗項目\n"
        elif success_rate >= 70:
            report += "🟠 **普通** - 測試結果普通，需要改善\n"
        else:
            report += "🔴 **需改善** - 測試結果不佳，需要大幅修正\n"

        return report


def main():
    """主程式"""
    try:
        runner = TestRunner()
        runner.run_all_tests()

    except KeyboardInterrupt:
        print("\n測試執行被使用者中斷")
        sys.exit(1)
    except Exception as e:
        print(f"測試執行錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
