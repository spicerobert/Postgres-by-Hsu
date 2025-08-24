import datetime
import streamlit as st
import datasource

st.sidebar.title("台鐵車站資訊")
st.sidebar.header("2023年各站進出人數")
st.subheader("進出站人數顯示區")

@st.cache_data
def get_stations():
    """取得車站資料"""
    return datasource.get_stations_names()

@st.cache_data
def get_date_range():
    """取得日期範圍"""
    return datasource.get_min_and_max_date()

stations = get_stations()
if stations is None:
    st.error("無法取得車站資料，請稍後再試。")
    st.stop()


common_stations = ['臺北','桃園','新竹','台中','臺南','高雄','其它']

choice = st.sidebar.radio("快速選擇常用車站", common_stations)

if choice == "其它":
    station = st.sidebar.selectbox(
        "請選擇車站",
        stations,
    )
else:
    station = choice
date_range = get_date_range()
if date_range is None:
    st.error("無法取得日期範圍，請稍後再試。")
    st.stop()

# 轉換為 datetime.date（如果 datasource 回傳字串）
try:
    min_date, max_date = date_range
    if isinstance(min_date, str):
        min_date = datetime.date.fromisoformat(min_date)
    if isinstance(max_date, str):
        max_date = datetime.date.fromisoformat(max_date)
except Exception as e:
    st.error(f"無法解析日期範圍: {e}")
    st.stop()

# 在 sidebar 顯示只限於此範圍的日期選擇器（選擇範圍）
selected_dates = st.sidebar.date_input(
    "選擇日期範圍",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# 如果使用者只選單一日期，將其視為起訖相同
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = end_date = selected_dates

# 請使用datasource.get_station_data_by_date 函數取得資料,並顯示資料
st.write("您選擇的車站:", station)
st.write("日期範圍:", start_date, "至", end_date)

import pandas as pd

data = datasource.get_station_data_by_date(station, start_date, end_date)
if data is None:
    st.error("無法取得車站資料，請稍後再試。")
else:
    try:
        # 若已經是 DataFrame，直接使用；否則嘗試轉成 DataFrame
        if isinstance(data, pd.DataFrame):
            df = data
        else:
            df = pd.DataFrame(data)
    except Exception:
        # 如果直接轉換失敗，嘗試先將資料轉為 list（支援 generator 等）
        try:
            df = pd.DataFrame(list(data))
        except Exception as e:
            st.error(f"處理資料時發生錯誤: {e}")
            df = None

    if df is None or df.empty:
        st.info("查無資料。")
    else:
        st.write("進出站人數資料:")
        st.dataframe(df)
        # 提供下載 CSV 的按鈕
        try:
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "下載 CSV",
                data=csv,
                file_name=f"{station}_{start_date}_{end_date}.csv",
                mime="text/csv",
            )
        except Exception:
            # 若無 download_button（非常舊版 streamlit），則忽略下載功能
            pass