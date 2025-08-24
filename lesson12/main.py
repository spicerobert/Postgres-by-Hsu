import datetime
import streamlit as st
import datasource
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 設定 matplotlib 字型
plt.rcParams['font.family'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

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

def plot_entry_exit_chart(df, station_name):
    """
    繪製進站人數與出站人數比較圖
    """
    # 確保日期欄位為 datetime 格式
    if '日期' in df.columns:
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期')
    
    # 設定圖表樣式
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 繪製進站和出站人數
    x = df['日期'] if '日期' in df.columns else range(len(df))
    entry_data = df['進站人數'] if '進站人數' in df.columns else df.iloc[:, 2]
    exit_data = df['出站人數'] if '出站人數' in df.columns else df.iloc[:, 3]
    
    ax.plot(x, entry_data, label='Entry Count', color='#1f77b4', linewidth=2, marker='o', markersize=4)
    ax.plot(x, exit_data, label='Exit Count', color='#ff7f0e', linewidth=2, marker='s', markersize=4)
    
    # 添加填充區域以顯示差異
    ax.fill_between(x, entry_data, exit_data, 
                    where=(entry_data >= exit_data),
                    interpolate=True, color='#1f77b4', alpha=0.1)
    ax.fill_between(x, entry_data, exit_data, 
                    where=(entry_data < exit_data),
                    interpolate=True, color='#ff7f0e', alpha=0.1)
    
    # 設定圖表標題和標籤
    ax.set_title(f'{station_name} Entry vs Exit Count Comparison', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    
    # 設定圖例
    ax.legend(loc='upper right')
    
    # 格式化 x 軸日期顯示
    if '日期' in df.columns:
        plt.xticks(rotation=45)
    
    # 調整布局
    plt.tight_layout()
    
    return fig

data = datasource.get_station_data_by_date(station, start_date, end_date)
if data is None:
    st.error("無法取得車站資料，請稍後再試。")
else:
    try:
        # 若已經是 DataFrame，直接使用；否則嘗試轉成 DataFrame
        if isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            df = pd.DataFrame(data)
            # 如果 DataFrame 欄位為預設數字索引 (表示原始資料為 tuple/list)，加入友善欄位名稱
            expected_cols = ["日期", "車站", "進站人數", "出站人數"]
            try:
                # RangeIndex 常見於 list-of-tuples 轉成 DataFrame 的情況
                if isinstance(df.columns, pd.RangeIndex) and df.shape[1] == len(expected_cols):
                    df.columns = expected_cols
            except Exception:
                # 若任何步驟失敗，保留原始欄位，後續再嘗試
                pass
    except Exception:
        # 如果直接轉換失敗，嘗試先將資料轉為 list（支援 generator 等）
        try:
            df = pd.DataFrame(list(data))
            # 再次嘗試加入欄位名稱（若符合長度）
            if df is not None:
                try:
                    if isinstance(df.columns, pd.RangeIndex) and df.shape[1] == 4:
                        df.columns = ["日期", "車站", "進站人數", "出站人數"]
                except Exception:
                    pass
        except Exception as e:
            st.error(f"處理資料時發生錯誤: {e}")
            df = None

    if df is None or df.empty:
        st.info("查無資料。")
    else:
        st.write("進出站人數資料:")
        st.dataframe(df)
        
        # 顯示圖表
        if len(df) > 0:
            st.subheader("📊 Entry vs Exit Count Comparison Chart")
            try:
                fig = plot_entry_exit_chart(df, station)
                st.pyplot(fig)
                plt.close(fig)  # 釋放記憶體
                
                # 顯示統計摘要
                col1, col2, col3 = st.columns(3)
                
                entry_col = '進站人數' if '進站人數' in df.columns else df.columns[2]
                exit_col = '出站人數' if '出站人數' in df.columns else df.columns[3]
                
                with col1:
                    st.metric("Average Entry Count", f"{df[entry_col].mean():.0f}")
                    st.metric("Maximum Entry Count", f"{df[entry_col].max():.0f}")
                
                with col2:
                    st.metric("Average Exit Count", f"{df[exit_col].mean():.0f}")
                    st.metric("Maximum Exit Count", f"{df[exit_col].max():.0f}")
                
                with col3:
                    total_entry = df[entry_col].sum()
                    total_exit = df[exit_col].sum()
                    st.metric("Total Entry Count", f"{total_entry:,.0f}")
                    st.metric("Total Exit Count", f"{total_exit:,.0f}")
                    
            except Exception as e:
                st.error(f"繪製圖表時發生錯誤: {e}")
        
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