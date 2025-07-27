#!/usr/bin/env python3
"""
測試執行腳本

執行所有單元測試並顯示結果。
"""

import sys
import os
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import unittest

def run_tests():
    """執行所有測試"""
    # 發現並執行測試
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 回傳結果
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)