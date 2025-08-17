import streamlit as st
import datasource

st.sidebar.title("台鐵車站資訊")
st.sidebar.header("2023年各站進出人數")
st.subheader("進出站人數顯示區")

@st.cache_resource
def get_stations():
    """取得車站資料"""
    return datasource.get_stations_names()

stations = get_stations()
if stations is None:
    st.error("無法取得車站資料，請稍後再試。")
    st.stop()

#sidebar要先顯示常用的車站名稱
#使用者可以很快的選擇
#如果不常用的車站名稱,再使用selectbox

# 先取前五個站為常用站（可改為固定清單或從使用者設定讀取）
common_stations = stations[:5] if len(stations) >= 5 else stations

# 在 sidebar 顯示常用站列表，並加上「其他」選項（當總站數大於常用站數時）
quick_options = common_stations + (["其他"] if len(stations) > len(common_stations) else [])
choice = st.sidebar.radio("快速選擇常用車站", quick_options)

if choice == "其他":
    station = st.sidebar.selectbox(
        "請選擇車站",
        stations,
    )
else:
    station = choice

st.write("您選擇的車站:", station)

