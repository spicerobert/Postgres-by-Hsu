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
station = st.sidebar.selectbox(
    "請選擇車站",
    stations,
)

st.write("您選擇的車站:", station)

