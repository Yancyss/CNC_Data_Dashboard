import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("data/final_result.csv")

    # 字段统一（适配你原数据）
    df = df.rename(columns={
        "编号": "委托单编号",
        "下单时间": "委托时间",
        "完成时间": "接收时间",
        "订单状态": "流程状态"
    })

    # 时间处理
    df["委托时间"] = pd.to_datetime(df["委托时间"], errors="coerce")
    df["接收时间"] = pd.to_datetime(df["接收时间"], errors="coerce")

    return df
