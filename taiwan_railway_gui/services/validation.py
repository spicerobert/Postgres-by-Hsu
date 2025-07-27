"""
資料驗證服務

提供各種資料驗證功能，確保輸入資料的正確性和一致性。
支援多層級驗證和詳細的錯誤回饋。
"""

import re
from datetime import date, datetime
from typing import Tuple, List, Optional, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass
from taiwan_railway_gui.interfaces import ValidationServiceInterface


class ValidationLevel(Enum):
    """驗證層級"""
    BASIC = "basic"         # 基本格式驗證
    BUSINESS = "business"   # 業務邏輯驗證
    STRICT = "strict"       # 嚴格驗證


@dataclass
class ValidationResult:
    """驗證結果"""
    is_valid: bool
    error_message: str
    error_code: str
    suggestions: List[str]
    warnings: List[str]
    corrected_value: Any = None


class ValidationService(ValidationServiceInterface):
    """
    資料驗證服務實作

    提供日期範圍、車站代碼、搜尋查詢等各種驗證功能。
    支援多層級驗證和自動修正建議。
    """

    def __init__(self):
        """初始化驗證服務"""
        self._init_validation_rules()
        self._init_error_messages()

    def _init_validation_rules(self):
        """初始化驗證規則"""
        self.validation_rules = {
            'station_code': {
                'min_length': 1,
                'max_length': 10,
                'pattern': r'^\d+$',
                'required': True
            },
            'station_name': {
                'min_length': 1,
                'max_length': 50,
                'pattern': r'^[\u4e00-\u9fff\w\s]+$',
                'required': True
            },
            'search_query': {
                'max_length': 50,
                'forbidden_chars': ['<', '>', '"', "'", ';', '--', '/*', '*/'],
                'forbidden_words': ['DROP', 'DELETE', 'UPDATE', 'INSERT']
            },
            'date_range': {
                'max_days': 730,  # 最多2年
                'min_date': date(2000, 1, 1),
                'max_future_days': 0  # 不允許未來日期
            },
            'passenger_count': {
                'min_value': 0,
                'max_value': 100000,
                'required': True
            },
            'filename': {
                'max_length': 255,
                'forbidden_chars': ['<', '>', ':', '"', '|', '?', '*', '/', '\\'],
                'reserved_names': ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3',
                                 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                                 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6',
                                 'LPT7', 'LPT8', 'LPT9']
            }
        }

    def _init_error_messages(self):
        """初始化錯誤訊息"""
        self.error_messages = {
            'required_field': "此欄位為必填項目",
            'invalid_format': "格式不正確",
            'too_short': "長度過短，最少需要 {min_length} 個字元",
            'too_long': "長度過長，最多允許 {max_length} 個字元",
            'invalid_pattern': "格式不符合要求",
            'forbidden_chars': "包含不允許的字元: {chars}",
            'forbidden_words': "包含不允許的關鍵字: {words}",
            'invalid_date': "日期格式不正確",
            'date_order': "開始日期不能晚於結束日期",
            'future_date': "不允許未來日期",
            'date_too_old': "日期過於久遠",
            'date_range_too_long': "日期範圍過長，最多允許 {max_days} 天",
            'value_too_small': "數值過小，最小值為 {min_value}",
            'value_too_large': "數值過大，最大值為 {max_value}",
            'reserved_name': "不能使用保留名稱: {name}",
            'duplicate_values': "不能包含重複值",
            'too_many_items': "項目過多，最多允許 {max_items} 個"
        }

    def validate_with_level(self, value: Any, validation_type: str,
                          level: ValidationLevel = ValidationLevel.BUSINESS) -> ValidationResult:
        """
        多層級驗證

        Args:
            value: 要驗證的值
            validation_type: 驗證類型
            level: 驗證層級

        Returns:
            ValidationResult: 驗證結果
        """
        try:
            # 根據驗證類型選擇驗證方法
            if validation_type == 'date_range':
                return self._validate_date_range_enhanced(value, level)
            elif validation_type == 'station_code':
                return self._validate_station_code_enhanced(value, level)
            elif validation_type == 'search_query':
                return self._validate_search_query_enhanced(value, level)
            elif validation_type == 'station_list':
                return self._validate_station_list_enhanced(value, level)
            elif validation_type == 'passenger_count':
                return self._validate_passenger_count_enhanced(value, level)
            elif validation_type == 'filename':
                return self._validate_filename_enhanced(value, level)
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"未知的驗證類型: {validation_type}",
                    error_code="unknown_validation_type",
                    suggestions=["檢查驗證類型是否正確"],
                    warnings=[]
                )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"驗證過程發生錯誤: {str(e)}",
                error_code="validation_error",
                suggestions=["重新檢查輸入值", "聯絡技術支援"],
                warnings=[]
            )

    def _validate_date_range_enhanced(self, value: Tuple[date, date],
                                    level: ValidationLevel) -> ValidationResult:
        """增強的日期範圍驗證"""
        try:
            start_date, end_date = value
            warnings = []
            suggestions = []

            # 基本驗證
            if not isinstance(start_date, date) or not isinstance(end_date, date):
                return ValidationResult(
                    is_valid=False,
                    error_message="日期必須是有效的日期物件",
                    error_code="invalid_date_type",
                    suggestions=["確認日期格式正確", "使用 YYYY-MM-DD 格式"],
                    warnings=[]
                )

            # 日期順序檢查
            if start_date > end_date:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['date_order'],
                    error_code="invalid_date_order",
                    suggestions=["檢查開始和結束日期", "交換日期順序"],
                    warnings=[],
                    corrected_value=(end_date, start_date)
                )

            # 業務邏輯驗證
            if level in [ValidationLevel.BUSINESS, ValidationLevel.STRICT]:
                today = date.today()
                rules = self.validation_rules['date_range']

                # 未來日期檢查
                if start_date > today or end_date > today:
                    return ValidationResult(
                        is_valid=False,
                        error_message=self.error_messages['future_date'],
                        error_code="future_date",
                        suggestions=["選擇今天或之前的日期"],
                        warnings=[]
                    )

                # 日期過於久遠
                if start_date < rules['min_date']:
                    return ValidationResult(
                        is_valid=False,
                        error_message=self.error_messages['date_too_old'],
                        error_code="date_too_old",
                        suggestions=[f"選擇 {rules['min_date']} 之後的日期"],
                        warnings=[]
                    )

                # 日期範圍過長
                days_diff = (end_date - start_date).days
                if days_diff > rules['max_days']:
                    return ValidationResult(
                        is_valid=False,
                        error_message=self.error_messages['date_range_too_long'].format(
                            max_days=rules['max_days']
                        ),
                        error_code="date_range_too_long",
                        suggestions=[
                            f"縮短日期範圍至 {rules['max_days']} 天內",
                            "分批查詢資料"
                        ],
                        warnings=[]
                    )

                # 嚴格驗證
                if level == ValidationLevel.STRICT:
                    # 檢查是否為週末或假日（可擴展）
                    if days_diff > 90:
                        warnings.append("查詢範圍較長，可能需要較多時間")

                    if (today - end_date).days > 365:
                        warnings.append("查詢的是較舊的資料")

            return ValidationResult(
                is_valid=True,
                error_message="",
                error_code="",
                suggestions=suggestions,
                warnings=warnings
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"日期範圍驗證錯誤: {str(e)}",
                error_code="date_validation_error",
                suggestions=["檢查日期格式", "重新輸入日期"],
                warnings=[]
            )

    def _validate_station_code_enhanced(self, value: str,
                                      level: ValidationLevel) -> ValidationResult:
        """增強的車站代碼驗證"""
        try:
            warnings = []
            suggestions = []
            rules = self.validation_rules['station_code']

            # 基本驗證
            if not value:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['required_field'],
                    error_code="required_field",
                    suggestions=["輸入車站代碼", "從下拉選單選擇"],
                    warnings=[]
                )

            if not isinstance(value, str):
                return ValidationResult(
                    is_valid=False,
                    error_message="車站代碼必須是字串",
                    error_code="invalid_type",
                    suggestions=["確認輸入格式"],
                    warnings=[]
                )

            # 去除空白並檢查
            cleaned_value = value.strip()
            if not cleaned_value:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['required_field'],
                    error_code="empty_after_trim",
                    suggestions=["輸入有效的車站代碼"],
                    warnings=[],
                    corrected_value=""
                )

            # 長度檢查
            if len(cleaned_value) < rules['min_length']:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['too_short'].format(
                        min_length=rules['min_length']
                    ),
                    error_code="too_short",
                    suggestions=["輸入完整的車站代碼"],
                    warnings=[]
                )

            if len(cleaned_value) > rules['max_length']:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['too_long'].format(
                        max_length=rules['max_length']
                    ),
                    error_code="too_long",
                    suggestions=["縮短車站代碼"],
                    warnings=[]
                )

            # 格式檢查
            if not re.match(rules['pattern'], cleaned_value):
                return ValidationResult(
                    is_valid=False,
                    error_message="車站代碼格式不正確，應為數字",
                    error_code="invalid_format",
                    suggestions=["輸入數字格式的車站代碼", "從下拉選單選擇"],
                    warnings=[]
                )

            # 業務邏輯驗證
            if level in [ValidationLevel.BUSINESS, ValidationLevel.STRICT]:
                # 檢查是否為常見的無效代碼
                invalid_codes = ['0', '00', '000', '0000']
                if cleaned_value in invalid_codes:
                    warnings.append("此代碼可能無效")
                    suggestions.append("確認車站代碼正確性")

                # 嚴格驗證
                if level == ValidationLevel.STRICT:
                    # 檢查代碼長度是否符合台鐵標準（通常4位數）
                    if len(cleaned_value) != 4:
                        warnings.append("台鐵車站代碼通常為4位數")

            return ValidationResult(
                is_valid=True,
                error_message="",
                error_code="",
                suggestions=suggestions,
                warnings=warnings,
                corrected_value=cleaned_value if cleaned_value != value else None
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"車站代碼驗證錯誤: {str(e)}",
                error_code="station_code_validation_error",
                suggestions=["重新輸入車站代碼", "檢查輸入格式"],
                warnings=[]
            )

    def _validate_search_query_enhanced(self, value: str,
                                      level: ValidationLevel) -> ValidationResult:
        """增強的搜尋查詢驗證"""
        try:
            warnings = []
            suggestions = []
            rules = self.validation_rules['search_query']

            # 基本驗證
            if not isinstance(value, str):
                return ValidationResult(
                    is_valid=False,
                    error_message="搜尋查詢必須是字串",
                    error_code="invalid_type",
                    suggestions=["確認輸入格式"],
                    warnings=[]
                )

            # 允許空查詢
            cleaned_value = value.strip()
            if not cleaned_value:
                return ValidationResult(
                    is_valid=True,
                    error_message="",
                    error_code="",
                    suggestions=["輸入關鍵字以縮小搜尋範圍"],
                    warnings=["空查詢將顯示所有結果"],
                    corrected_value=""
                )

            # 長度檢查
            if len(cleaned_value) > rules['max_length']:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['too_long'].format(
                        max_length=rules['max_length']
                    ),
                    error_code="too_long",
                    suggestions=["縮短搜尋關鍵字"],
                    warnings=[]
                )

            # 危險字元檢查
            found_chars = [char for char in rules['forbidden_chars'] if char in cleaned_value]
            if found_chars:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['forbidden_chars'].format(
                        chars=', '.join(found_chars)
                    ),
                    error_code="forbidden_chars",
                    suggestions=["移除特殊字元", "使用一般文字搜尋"],
                    warnings=[]
                )

            # 業務邏輯驗證
            if level in [ValidationLevel.BUSINESS, ValidationLevel.STRICT]:
                # 危險關鍵字檢查
                query_upper = cleaned_value.upper()
                found_words = [word for word in rules['forbidden_words'] if word in query_upper]
                if found_words:
                    return ValidationResult(
                        is_valid=False,
                        error_message=self.error_messages['forbidden_words'].format(
                            words=', '.join(found_words)
                        ),
                        error_code="forbidden_words",
                        suggestions=["使用一般搜尋關鍵字"],
                        warnings=[]
                    )

                # 檢查搜尋類型
                if cleaned_value.isdigit():
                    # 數字搜尋，可能是車站代碼
                    code_result = self._validate_station_code_enhanced(cleaned_value, level)
                    if not code_result.is_valid:
                        warnings.append("數字格式可能不是有效的車站代碼")
                        suggestions.append("確認車站代碼正確性")

                elif re.search(r'[\u4e00-\u9fff]', cleaned_value):
                    # 中文搜尋，可能是車站名稱
                    name_rules = self.validation_rules['station_name']
                    if not re.match(name_rules['pattern'], cleaned_value):
                        warnings.append("車站名稱格式可能不正確")
                        suggestions.append("檢查中文字元和格式")

                # 嚴格驗證
                if level == ValidationLevel.STRICT:
                    # 檢查搜尋長度是否合理
                    if len(cleaned_value) == 1:
                        warnings.append("單字元搜尋可能返回過多結果")
                        suggestions.append("使用更具體的關鍵字")

            return ValidationResult(
                is_valid=True,
                error_message="",
                error_code="",
                suggestions=suggestions,
                warnings=warnings,
                corrected_value=cleaned_value if cleaned_value != value else None
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"搜尋查詢驗證錯誤: {str(e)}",
                error_code="search_validation_error",
                suggestions=["重新輸入搜尋關鍵字", "檢查輸入格式"],
                warnings=[]
            )

    def _validate_station_list_enhanced(self, value: List[str],
                                      level: ValidationLevel) -> ValidationResult:
        """增強的車站列表驗證"""
        try:
            warnings = []
            suggestions = []

            # 基本驗證
            if not isinstance(value, list):
                return ValidationResult(
                    is_valid=False,
                    error_message="車站列表必須是 list 類型",
                    error_code="invalid_type",
                    suggestions=["確認輸入格式"],
                    warnings=[]
                )

            if not value:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['required_field'],
                    error_code="empty_list",
                    suggestions=["至少選擇一個車站"],
                    warnings=[]
                )

            # 數量檢查
            max_items = 5
            if len(value) > max_items:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['too_many_items'].format(
                        max_items=max_items
                    ),
                    error_code="too_many_items",
                    suggestions=[f"最多選擇 {max_items} 個車站"],
                    warnings=[]
                )

            # 重複檢查
            if len(value) != len(set(value)):
                duplicates = [item for item in set(value) if value.count(item) > 1]
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['duplicate_values'],
                    error_code="duplicate_values",
                    suggestions=["移除重複的車站"],
                    warnings=[],
                    corrected_value=list(set(value))
                )

            # 逐一驗證每個車站代碼
            invalid_codes = []
            for i, code in enumerate(value):
                code_result = self._validate_station_code_enhanced(code, level)
                if not code_result.is_valid:
                    invalid_codes.append((i + 1, code, code_result.error_message))

            if invalid_codes:
                error_details = "; ".join([
                    f"第{pos}個車站({code}): {msg}"
                    for pos, code, msg in invalid_codes
                ])
                return ValidationResult(
                    is_valid=False,
                    error_message=f"車站代碼驗證失敗: {error_details}",
                    error_code="invalid_station_codes",
                    suggestions=["檢查車站代碼格式", "從下拉選單選擇"],
                    warnings=[]
                )

            # 業務邏輯驗證
            if level in [ValidationLevel.BUSINESS, ValidationLevel.STRICT]:
                # 檢查是否選擇了過多車站（影響效能）
                if len(value) >= 4:
                    warnings.append("選擇較多車站可能影響查詢效能")
                    suggestions.append("考慮分批比較")

                # 嚴格驗證
                if level == ValidationLevel.STRICT:
                    # 檢查車站代碼是否來自同一區域（可擴展）
                    if len(value) > 2:
                        suggestions.append("建議選擇相近區域的車站進行比較")

            return ValidationResult(
                is_valid=True,
                error_message="",
                error_code="",
                suggestions=suggestions,
                warnings=warnings
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"車站列表驗證錯誤: {str(e)}",
                error_code="station_list_validation_error",
                suggestions=["重新選擇車站", "檢查輸入格式"],
                warnings=[]
            )

    def _validate_passenger_count_enhanced(self, value: int,
                                         level: ValidationLevel) -> ValidationResult:
        """增強的乘客數量驗證"""
        try:
            warnings = []
            suggestions = []
            rules = self.validation_rules['passenger_count']

            # 基本驗證
            if not isinstance(value, int):
                return ValidationResult(
                    is_valid=False,
                    error_message="乘客數量必須是整數",
                    error_code="invalid_type",
                    suggestions=["輸入整數值"],
                    warnings=[]
                )

            # 範圍檢查
            if value < rules['min_value']:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['value_too_small'].format(
                        min_value=rules['min_value']
                    ),
                    error_code="value_too_small",
                    suggestions=["輸入非負數"],
                    warnings=[]
                )

            if value > rules['max_value']:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['value_too_large'].format(
                        max_value=rules['max_value']
                    ),
                    error_code="value_too_large",
                    suggestions=["檢查數值是否正確", "確認資料來源"],
                    warnings=[]
                )

            # 業務邏輯驗證
            if level in [ValidationLevel.BUSINESS, ValidationLevel.STRICT]:
                # 異常高的數值警告
                if value > 50000:
                    warnings.append("乘客數量異常高，請確認資料正確性")
                    suggestions.append("檢查資料來源")

                # 嚴格驗證
                if level == ValidationLevel.STRICT:
                    # 檢查是否為合理的日客流量
                    if value > 20000:
                        warnings.append("單日客流量較高，可能是特殊情況")

            return ValidationResult(
                is_valid=True,
                error_message="",
                error_code="",
                suggestions=suggestions,
                warnings=warnings
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"乘客數量驗證錯誤: {str(e)}",
                error_code="passenger_count_validation_error",
                suggestions=["重新輸入數值", "檢查數值格式"],
                warnings=[]
            )

    def _validate_filename_enhanced(self, value: str,
                                  level: ValidationLevel) -> ValidationResult:
        """增強的檔案名稱驗證"""
        try:
            warnings = []
            suggestions = []
            rules = self.validation_rules['filename']

            # 基本驗證
            if not isinstance(value, str):
                return ValidationResult(
                    is_valid=False,
                    error_message="檔案名稱必須是字串",
                    error_code="invalid_type",
                    suggestions=["確認輸入格式"],
                    warnings=[]
                )

            cleaned_value = value.strip()
            if not cleaned_value:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['required_field'],
                    error_code="empty_filename",
                    suggestions=["輸入檔案名稱"],
                    warnings=[]
                )

            # 長度檢查
            if len(cleaned_value) > rules['max_length']:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['too_long'].format(
                        max_length=rules['max_length']
                    ),
                    error_code="filename_too_long",
                    suggestions=["縮短檔案名稱"],
                    warnings=[]
                )

            # 禁用字元檢查
            found_chars = [char for char in rules['forbidden_chars'] if char in cleaned_value]
            if found_chars:
                return ValidationResult(
                    is_valid=False,
                    error_message=self.error_messages['forbidden_chars'].format(
                        chars=', '.join(found_chars)
                    ),
                    error_code="forbidden_chars",
                    suggestions=["移除特殊字元", "使用英文字母和數字"],
                    warnings=[],
                    corrected_value=''.join(char for char in cleaned_value
                                          if char not in rules['forbidden_chars'])
                )

            # 保留名稱檢查
            filename_upper = cleaned_value.upper()
            for reserved in rules['reserved_names']:
                if filename_upper == reserved or filename_upper.startswith(reserved + '.'):
                    return ValidationResult(
                        is_valid=False,
                        error_message=self.error_messages['reserved_name'].format(
                            name=reserved
                        ),
                        error_code="reserved_name",
                        suggestions=["使用其他檔案名稱"],
                        warnings=[]
                    )

            # 業務邏輯驗證
            if level in [ValidationLevel.BUSINESS, ValidationLevel.STRICT]:
                # 檢查副檔名
                if '.' not in cleaned_value:
                    warnings.append("檔案名稱沒有副檔名")
                    suggestions.append("考慮加入適當的副檔名")

                # 嚴格驗證
                if level == ValidationLevel.STRICT:
                    # 檢查是否包含中文字元
                    if re.search(r'[\u4e00-\u9fff]', cleaned_value):
                        warnings.append("檔案名稱包含中文字元，可能影響跨平台相容性")
                        suggestions.append("考慮使用英文檔案名稱")

            return ValidationResult(
                is_valid=True,
                error_message="",
                error_code="",
                suggestions=suggestions,
                warnings=warnings,
                corrected_value=cleaned_value if cleaned_value != value else None
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"檔案名稱驗證錯誤: {str(e)}",
                error_code="filename_validation_error",
                suggestions=["重新輸入檔案名稱", "檢查輸入格式"],
                warnings=[]
            )

    # 保持原有的方法以維持向後相容性
    def validate_date_range(self, start_date: date, end_date: date) -> Tuple[bool, str]:
        """
        驗證日期範圍（向後相容性方法）

        Args:
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            Tuple[bool, str]: (是否有效, 錯誤訊息)
        """
        result = self._validate_date_range_enhanced((start_date, end_date), ValidationLevel.BUSINESS)
        return result.is_valid, result.error_message

    def validate_station_code(self, station_code: str) -> Tuple[bool, str]:
        """
        驗證車站代碼（向後相容性方法）

        Args:
            station_code: 車站代碼

        Returns:
            Tuple[bool, str]: (是否有效, 錯誤訊息)
        """
        result = self._validate_station_code_enhanced(station_code, ValidationLevel.BUSINESS)
        return result.is_valid, result.error_message

    def validate_search_query(self, query: str) -> Tuple[bool, str]:
        """
        驗證搜尋查詢（向後相容性方法）

        Args:
            query: 搜尋查詢字串

        Returns:
            Tuple[bool, str]: (是否有效, 錯誤訊息)
        """
        result = self._validate_search_query_enhanced(query, ValidationLevel.BUSINESS)
        return result.is_valid, result.error_message

    def validate_station_list(self, station_codes: List[str]) -> Tuple[bool, str]:
        """
        驗證車站代碼列表（向後相容性方法）

        Args:
            station_codes: 車站代碼列表

        Returns:
            Tuple[bool, str]: (是否有效, 錯誤訊息)
        """
        result = self._validate_station_list_enhanced(station_codes, ValidationLevel.BUSINESS)
        return result.is_valid, result.error_message

    def validate_passenger_count(self, count: int) -> Tuple[bool, str]:
        """
        驗證乘客數量（向後相容性方法）

        Args:
            count: 乘客數量

        Returns:
            Tuple[bool, str]: (是否有效, 錯誤訊息)
        """
        result = self._validate_passenger_count_enhanced(count, ValidationLevel.BUSINESS)
        return result.is_valid, result.error_message

    def validate_export_filename(self, filename: str) -> Tuple[bool, str]:
        """
        驗證匯出檔案名稱（向後相容性方法）

        Args:
            filename: 檔案名稱

        Returns:
            Tuple[bool, str]: (是否有效, 錯誤訊息)
        """
        result = self._validate_filename_enhanced(filename, ValidationLevel.BUSINESS)
        return result.is_valid, result.error_message


def create_validation_service() -> ValidationService:
    """建立驗證服務實例"""
    return ValidationService()