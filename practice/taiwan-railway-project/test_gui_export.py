#!/usr/bin/env python3
"""
測試 GUI 匯出功能整合

測試匯出管理器與 GUI 元件的整合。
"""

import tkinter as tk
from datetime import date

from taiwan_railway_gui.models.station import Station
from taiwan_railway_gui.models.passenger_flow import PassengerFlow
from taiwan_railway_gui.services.export_manager import get_export_manager


def test_gui_integration():
    """測試 GUI 整合"""
    print("測試 GUI 匯出整合...")

    # 建立測試視窗
    root = tk.Tk()
    root.title("匯出測試")
    root.geometry("400x300")

    # 建立測試資料
    test_stations = [
        Station(
            station_code='1001',
            station_name='台北車站',
            address='台北市中正區北平西路3號',
            phone='02-23713558',
            gps_lat=25.047924,
            gps_lng=121.517081,
            has_bike_rental=True
        ),
        Station(
            station_code='1002',
            station_name='板橋車站',
            address='新北市板橋區縣民大道二段7號',
            phone='02-29603001',
            gps_lat=25.013711,
            gps_lng=121.463528,
            has_bike_rental=False
        )
    ]

    test_flows = [
        PassengerFlow(
            station_code='1001',
            date=date(2024, 1, 1),
            in_passengers=10000,
            out_passengers=9500
        ),
        PassengerFlow(
            station_code='1001',
            date=date(2024, 1, 2),
            in_passengers=12000,
            out_passengers=11500
        )
    ]

    # 建立匯出管理器
    export_manager = get_export_manager()

    # 建立按鈕
    def export_stations():
        success = export_manager.export_stations(root, test_stations)
        if success:
            print("✓ 車站資料匯出成功")
        else:
            print("✗ 車站資料匯出失敗或取消")

    def export_flows():
        success = export_manager.export_passenger_flows(root, test_flows)
        if success:
            print("✓ 客流量資料匯出成功")
        else:
            print("✗ 客流量資料匯出失敗或取消")

    # 建立介面
    frame = tk.Frame(root)
    frame.pack(expand=True, fill='both', padx=20, pady=20)

    tk.Label(frame, text="匯出功能測試", font=('Arial', 16, 'bold')).pack(pady=10)

    tk.Button(
        frame,
        text="匯出車站資料",
        command=export_stations,
        width=20,
        height=2
    ).pack(pady=10)

    tk.Button(
        frame,
        text="匯出客流量資料",
        command=export_flows,
        width=20,
        height=2
    ).pack(pady=10)

    tk.Button(
        frame,
        text="關閉",
        command=root.quit,
        width=20,
        height=2
    ).pack(pady=10)

    tk.Label(
        frame,
        text="點選按鈕測試匯出功能\n選擇欄位後選擇儲存位置",
        justify=tk.CENTER
    ).pack(pady=10)

    print("GUI 測試視窗已開啟，請手動測試匯出功能...")
    print("測試完成後請關閉視窗")

    # 執行主迴圈
    root.mainloop()

    print("✓ GUI 整合測試完成")


def main():
    """主函數"""
    print("開始 GUI 匯出整合測試...")
    print("=" * 50)

    try:
        test_gui_integration()
        print("=" * 50)
        print("✅ GUI 整合測試完成！")

    except Exception as e:
        print("=" * 50)
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)