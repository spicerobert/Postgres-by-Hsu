"""
整合測試執行器

統一執行所有整合測試的主程式。
"""

import unittest
import sys
import os
import time
from io import StringIO
from datetime import datetime

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 匯入所有整合測試模組
try:
    from tests.test_integration_simple import (
        SimpleIntegrationTest,
        ComponentInteractionTest,
        EndToEndSimulationTest
    )
    simple_tests_available = True
except ImportError as e:
    print(f"警告：無法載入簡化整合測試：{e}")
    simple_tests_available = False

try:
    from tests.test_integration_database import (
        TestStationDAOIntegration,
        TestPassengerFlowDAOIntegration,
        TestDatabaseConnectionIntegration
    )
    database_tests_available = True
except ImportError as e:
    print(f"警告：無法載入資料庫整合測試：{e}")
    database_tests_available = False

try:
    from tests.test_integration_gui import (
        TestMainWindowIntegration,
        TestStationSearchTabIntegration,
        TestPassengerFlowTabIntegration,
        TestComparisonTabIntegration,
        TestChartTabIntegration,
        TestCrossTabIntegration
    )
    gui_tests_available = True
except ImportError as e:
    print(f"警告：無法載入GUI整合測試：{e}")
    gui_tests_available = False

try:
    from tests.test_integration_end_to_end import (
        TestCompleteUserWorkflows,
        TestErrorConditionWorkflows,
        TestPerformanceAndLargeDataset
    )
    e2e_tests_available = True
except ImportError as e:
    print(f"警告：無法載入端到端整合測試：{e}")
    e2e_tests_available = False

try:
    from tests.test_integration_comprehensive import (
        TestDatabaseIntegration,
        TestModelIntegration,
        TestComponentInteraction,
        TestEndToEndWorkflows,
        TestErrorConditions,
        TestPerformanceAndLargeDataset as TestComprehensivePerformance
    )
    comprehensive_tests_available = True
except ImportError as e:
    print(f"警告：無法載入綜合整合測試：{e}")
    comprehensive_tests_available = False


class IntegrationTestRunner:
    """整合測試執行器"""

    def __init__(self):
        """初始化測試執行器"""
        self.test_results = {}
        self.total_tests = 0
        self.total_failures = 0
        self.total_errors = 0
        self.start_time = None
        self.end_time = None

    def run_simple_tests(self):
        """執行簡化整合測試"""
        if not simple_tests_available:
            print("⚠️  跳過簡化整合測試（模組無法載入）")
            return None

        print("\n" + "="*60)
        print("🔧 執行簡化整合測試")
        print("="*60)

        suite = unittest.TestSuite()
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(SimpleIntegrationTest))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(ComponentInteractionTest))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(EndToEndSimulationTest))

        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)

        self.test_results['simple'] = result
        self.total_tests += result.testsRun
        self.total_failures += len(result.failures)
        self.total_errors += len(result.errors)

        return result

    def run_database_tests(self):
        """執行資料庫整合測試"""
        if not database_tests_available:
            print("⚠️  跳過資料庫整合測試（模組無法載入）")
            return None

        print("\n" + "="*60)
        print("🔍 執行資料庫整合測試")
        print("="*60)

        suite = unittest.TestSuite()
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStationDAOIntegration))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPassengerFlowDAOIntegration))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDatabaseConnectionIntegration))

        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)

        self.test_results['database'] = result
        self.total_tests += result.testsRun
        self.total_failures += len(result.failures)
        self.total_errors += len(result.errors)

        return result

    def run_gui_tests(self):
        """執行GUI整合測試"""
        if not gui_tests_available:
            print("⚠️  跳過GUI整合測試（模組無法載入）")
            return None

        print("\n" + "="*60)
        print("🖥️  執行GUI整合測試")
        print("="*60)

        suite = unittest.TestSuite()
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMainWindowIntegration))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStationSearchTabIntegration))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPassengerFlowTabIntegration))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestComparisonTabIntegration))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestChartTabIntegration))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCrossTabIntegration))

        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)

        self.test_results['gui'] = result
        self.total_tests += result.testsRun
        self.total_failures += len(result.failures)
        self.total_errors += len(result.errors)

        return result

    def run_end_to_end_tests(self):
        """執行端到端整合測試"""
        if not e2e_tests_available:
            print("⚠️  跳過端到端整合測試（模組無法載入）")
            return None

        print("\n" + "="*60)
        print("🔄 執行端到端整合測試")
        print("="*60)

        suite = unittest.TestSuite()
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCompleteUserWorkflows))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestErrorConditionWorkflows))
        # 注意：大型資料集測試可能需要額外的依賴，暫時跳過
        # suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPerformanceAndLargeDataset))

        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)

        self.test_results['end_to_end'] = result
        self.total_tests += result.testsRun
        self.total_failures += len(result.failures)
        self.total_errors += len(result.errors)

        return result

    def run_comprehensive_tests(self):
        """執行綜合整合測試"""
        if not comprehensive_tests_available:
            print("⚠️  跳過綜合整合測試（模組無法載入）")
            return None

        print("\n" + "="*60)
        print("🧪 執行綜合整合測試")
        print("="*60)

        suite = unittest.TestSuite()
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDatabaseIntegration))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestModelIntegration))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestComponentInteraction))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEndToEndWorkflows))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestErrorConditions))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestComprehensivePerformance))

        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)

        self.test_results['comprehensive'] = result
        self.total_tests += result.testsRun
        self.total_failures += len(result.failures)
        self.total_errors += len(result.errors)

        return result

    def run_all_tests(self):
        """執行所有整合測試"""
        self.start_time = time.time()

        print("🚀 開始執行台鐵車站資訊查詢系統整合測試")
        print(f"⏰ 開始時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 執行各類測試
        self.run_simple_tests()
        self.run_database_tests()
        self.run_gui_tests()
        self.run_end_to_end_tests()
        self.run_comprehensive_tests()

        self.end_time = time.time()
        self.print_summary()

    def print_summary(self):
        """印出測試摘要"""
        duration = self.end_time - self.start_time

        print("\n" + "="*60)
        print("📊 整合測試執行摘要")
        print("="*60)

        print(f"⏱️  執行時間：{duration:.2f} 秒")
        print(f"🧪 總測試數：{self.total_tests}")
        print(f"✅ 成功：{self.total_tests - self.total_failures - self.total_errors}")
        print(f"❌ 失敗：{self.total_failures}")
        print(f"⚠️  錯誤：{self.total_errors}")

        # 各類測試詳細結果
        for test_type, result in self.test_results.items():
            if result:
                status = "✅ 通過" if result.wasSuccessful() else "❌ 失敗"
                print(f"   {test_type.upper():15} {status:8} ({result.testsRun} 測試)")

        # 整體結果
        overall_success = self.total_failures == 0 and self.total_errors == 0
        if overall_success:
            print("\n🎉 所有整合測試通過！")
            return True
        else:
            print(f"\n💥 整合測試失敗！{self.total_failures} 個失敗，{self.total_errors} 個錯誤")
            return False

    def run_specific_test_category(self, category):
        """執行特定類別的測試"""
        self.start_time = time.time()

        if category == 'simple':
            result = self.run_simple_tests()
        elif category == 'database':
            result = self.run_database_tests()
        elif category == 'gui':
            result = self.run_gui_tests()
        elif category == 'e2e':
            result = self.run_end_to_end_tests()
        elif category == 'comprehensive':
            result = self.run_comprehensive_tests()
        else:
            print(f"❌ 未知的測試類別：{category}")
            return False

        self.end_time = time.time()

        if result:
            duration = self.end_time - self.start_time
            print(f"\n⏱️  執行時間：{duration:.2f} 秒")

            if result.wasSuccessful():
                print(f"✅ {category.upper()} 測試通過！")
                return True
            else:
                print(f"❌ {category.upper()} 測試失敗！")
                return False
        else:
            print(f"⚠️  {category.upper()} 測試無法執行")
            return False


def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(description='台鐵車站資訊查詢系統整合測試')
    parser.add_argument(
        '--category',
        choices=['all', 'simple', 'database', 'gui', 'e2e', 'comprehensive'],
        default='all',
        help='要執行的測試類別 (預設: all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='顯示詳細輸出'
    )

    args = parser.parse_args()

    # 建立測試執行器
    runner = IntegrationTestRunner()

    # 執行測試
    if args.category == 'all':
        success = runner.run_all_tests()
    else:
        success = runner.run_specific_test_category(args.category)

    # 返回適當的退出碼
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
