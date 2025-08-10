import datasource
import streamlit as st

def main():
    st.title("台鐵車站名稱列表")
    results = datasource.get_stations_names()
    if results:
        st.dataframe(results, width=400, height=600)
    else:
        st.error("無法取得車站資料")

if __name__ == "__main__":
    main()