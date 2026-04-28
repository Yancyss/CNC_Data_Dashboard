# utils/common.py
import pandas as pd
def show_update_time():
    from datetime import datetime
    import streamlit as st
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"📌 数据更新至：{now}")

def get_update_time(df):
    max_time = pd.concat([
        df["委托时间"],
        df["接收时间"]
    ]).max()
    return max_time