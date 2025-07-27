#!/usr/bin/env python3
"""
錯誤處理和使用者回饋系統示範

展示統一錯誤處理機制、多層級驗證和使用者友善回饋的功能。
"""

from taiwan_railway_gui.services.error_handler import get_error_handler, ErrorCategory, ErrorSeverity
from taiwan_railway_gui.services.validation import create_validation_service, ValidationLevel
from datetime import date

def demo_error_handling():
    """示範錯誤處理功能"""
    print("🔧 錯誤處理系統示範")
    print("=" * 50)

    error_handler = get_error_handler()

    # 示範不同類型的錯誤處理
    print("1. 資料庫連線錯誤:")
    db_error = Exception("psycopg2.OperationalError: connection to server failed")
    error_info = error_handler.handle_error(db_error)
    print(f"   使用者看到: {error_info.user_message}")
    print(f"   建議動作: {', '.join(error_info.suggested_actions)}")
    print()

    print("2. 輸入驗證錯誤:")
    validation_error = Exception("invalid date range specified")
    error_info = error_handler.handle_error(validation_error)
    print(f"   使用者看到: {error_info.user_message}")
    print(f"   建議動作: {', '.join(error_info.suggested_actions)}")
    print()

    print("3. 檔案操作錯誤:")
    file_error = FileNotFoundError("permission denied: cannot write to file")
    error_info = error_handler.handle_error(file_error)
    print(f"   使用者看到: {error_info.user_message}")
    print(f"   建議動作: {', '.join(error_info.suggested_actions)}")
    print()

def demo_validation():
    """示範多層級驗證功能"""
    print("✅ 多層級驗證系統示範")
    print("=" * 50)

    validation_service = create_validation_service()

    # 示範車站代碼驗證
    print("1. 車站代碼驗證:")
    test_codes = ["1001", "abc", "", "12345678901", "0000"]

    for code in test_codes:
        result = validation_service.validate_with_level(code, 'station_code', ValidationLevel.BUSINESS)
        status = "✓ 有效" if result.is_valid else "✗ 無效"
        print(f"   '{code}' -> {status}")
        if not result.is_valid:
            print(f"      錯誤: {result.error_message}")
            if result.suggestions:
                print(f"      建議: {result.suggestions[0]}")
        if result.warnings:
            print(f"      警告: {result.warnings[0]}")
    print()

    # 示範搜尋查詢驗證
    print("2. 搜尋查詢驗證:")
    test_queries = ["台北", "DROP TABLE", "<script>", "", "a" * 60]

    for query in test_queries:
        result = validation_service.validate_with_level(query, 'search_query', ValidationLevel.BUSINESS)
        status = "✓ 有效" if result.is_valid else "✗ 無效"
        display_query = query[:20] + "..." if len(query) > 20 else query
        print(f"   '{display_query}' -> {status}")
        if not result.is_valid:
            print(f"      錯誤: {result.error_message}")
        if result.warnings:
            print(f"      警告: {result.warnings[0]}")
    print()

    # 示範日期範圍驗證
    print("3. 日期範圍驗證:")
    test_ranges = [
        (date(2023, 1, 1), date(2023, 12, 31), "正常範圍"),
        (date(2023, 12, 31), date(2023, 1, 1), "順序錯誤"),
        (date(2030, 1, 1), date(2030, 12, 31), "未來日期"),
        (date(1990, 1, 1), date(1990, 12, 31), "過於久遠"),
    ]

    for start, end, description in test_ranges:
        result = validation_service.validate_with_level((start, end), 'date_range', ValidationLevel.BUSINESS)
        status = "✓ 有效" if result.is_valid else "✗ 無效"
        print(f"   {description} -> {status}")
        if not result.is_valid:
            print(f"      錯誤: {result.error_message}")
            if result.corrected_value:
                print(f"      建議修正: {result.corrected_value}")
        if result.warnings:
            print(f"      警告: {result.warnings[0]}")
    print()

def demo_error_statistics():
    """示範錯誤統計功能"""
    print("📊 錯誤統計系統示範")
    print("=" * 50)

    error_handler = get_error_handler()

    # 清除歷史記錄
    error_handler.clear_error_history()

    # 模擬一些錯誤
    print("模擬各種錯誤...")
    errors = [
        (Exception("database connection timeout"), "資料庫連線逾時"),
        (Exception("invalid station code format"), "車站代碼格式錯誤"),
        (FileNotFoundError("export file not found"), "匯出檔案未找到"),
        (Exception("tkinter widget creation failed"), "GUI 元件建立失敗"),
        (Exception("network connection refused"), "網路連線被拒絕"),
        (MemoryError("out of memory"), "記憶體不足"),
    ]

    for error, description in errors:
        error_info = error_handler.handle_error(error)
        print(f"   {description} -> {error_info.category.value} ({error_info.severity.value})")

    print()

    # 顯示統計資訊
    stats = error_handler.get_error_statistics()
    print(f"總錯誤數: {stats['total']}")
    print()

    print("按類別統計:")
    for category, count in stats['by_category'].items():
        if count > 0:
            print(f"   {category}: {count}")
    print()

    print("按嚴重程度統計:")
    for severity, count in stats['by_severity'].items():
        if count > 0:
            print(f"   {severity}: {count}")
    print()

    print("最近錯誤:")
    for error in stats['recent_errors'][:3]:
        print(f"   [{error['timestamp'][:19]}] {error['category']} - {error['message'][:50]}...")

def demo_graceful_degradation():
    """示範優雅降級功能"""
    print("🛡️ 優雅降級系統示範")
    print("=" * 50)

    error_handler = get_error_handler()

    print("1. 輕微錯誤 - 繼續運作:")
    minor_error = Exception("validation warning: unusual input detected")
    error_info = error_handler.handle_error(minor_error, severity=ErrorSeverity.LOW)
    print(f"   處理方式: 顯示警告，允許繼續操作")
    print(f"   使用者訊息: {error_info.user_message}")
    print()

    print("2. 中等錯誤 - 功能降級:")
    medium_error = Exception("database query timeout")
    error_info = error_handler.handle_error(medium_error, severity=ErrorSeverity.MEDIUM)
    print(f"   處理方式: 使用快取資料或簡化功能")
    print(f"   使用者訊息: {error_info.user_message}")
    print()

    print("3. 嚴重錯誤 - 安全模式:")
    severe_error = Exception("database connection completely failed")
    error_info = error_handler.handle_error(severe_error, severity=ErrorSeverity.HIGH)
    print(f"   處理方式: 切換到離線模式")
    print(f"   使用者訊息: {error_info.user_message}")
    print()

    print("4. 致命錯誤 - 安全關閉:")
    critical_error = MemoryError("system out of memory")
    error_info = error_handler.handle_error(critical_error, severity=ErrorSeverity.CRITICAL)
    print(f"   處理方式: 儲存資料並建議重新啟動")
    print(f"   使用者訊息: {error_info.user_message}")
    print()

def main():
    """主示範函數"""
    print("🚀 台鐵 GUI 錯誤處理和使用者回饋系統示範")
    print("=" * 60)
    print()

    demo_error_handling()
    print()

    demo_validation()
    print()

    demo_error_statistics()
    print()

    demo_graceful_degradation()
    print()

    print("✨ 示範完成！")
    print()
    print("主要功能:")
    print("• 統一錯誤處理機制 - 自動分類和嚴重程度評估")
    print("• 使用者友善訊息 - 將技術錯誤轉換為易懂的說明")
    print("• 多層級輸入驗證 - 基本、業務邏輯、嚴格三個層級")
    print("• 優雅降級功能 - 根據錯誤嚴重程度採取適當措施")
    print("• 錯誤記錄機制 - 完整的錯誤歷史和統計資訊")
    print("• 建議動作系統 - 為每個錯誤提供具體的解決建議")

if __name__ == "__main__":
    main()