import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data
from utils.preprocess import get_valid_data, add_duration

st.set_page_config(page_title="时长区间分析", layout="wide")

st.header("⏱ 时长区间分析看板")

# =====================
# ⭐ Sidebar 时间筛选
# =====================
st.sidebar.header("筛选条件")

range_option = st.sidebar.selectbox(
    "时间范围",
    ["近1月","近3月","近5月","近1年","近3年","近5年","全部"],
    index=3
)

# =====================
# ⭐ 数据加载
# =====================
df = load_data()
df_valid = get_valid_data(df)
df_valid = add_duration(df_valid)

df_valid["接收时间"] = pd.to_datetime(df_valid["接收时间"], errors="coerce")

max_time = df_valid["接收时间"].max()

# =====================
# ⭐ 时间筛选逻辑
# =====================
month_map = {"近1月":1,"近3月":3,"近5月":5}
year_map = {"近1年":1,"近3年":3,"近5年":5}

if range_option in month_map:
    df_valid = df_valid[df_valid["接收时间"] >= max_time - pd.DateOffset(months=month_map[range_option])]
elif range_option in year_map:
    df_valid = df_valid[df_valid["接收时间"] >= max_time - pd.DateOffset(years=year_map[range_option])]
# “全部”不筛选

# =====================
# ⭐ 区间定义
# =====================
bins = [0, 3, 6, 12, 24, 48, 72, float("inf")]
labels = ["特快","高效","正常","微慢","慢","超时","极慢工单"]

df_valid["时长区间"] = pd.cut(
    df_valid["处理时长(小时)"],
    bins=bins,
    labels=labels,
    right=False
)

# =====================
# ⭐ 总体分布
# =====================
st.subheader("📊 总体时长分布")

dist = df_valid["时长区间"].value_counts().reindex(labels, fill_value=0)

dist_df = pd.DataFrame({
    "区间": dist.index,
    "订单数": dist.values
})

col1, col2 = st.columns(2)

with col1:
    fig_bar = px.bar(
        dist_df,
        x="区间",
        y="订单数",
        text="订单数"
    )
    fig_bar.update_traces(textposition="outside")
    st.plotly_chart(fig_bar, width="stretch")

with col2:
    fig_pie = px.pie(
        dist_df,
        names="区间",
        values="订单数"
    )
    fig_pie.update_traces(textinfo="percent+label", textfont_size=16)
    st.plotly_chart(fig_pie, width="stretch")

# =====================
# ⭐ 人员对比
# =====================
st.subheader("👤 人员时长区间对比")

person_list = df_valid["接收人"].dropna().unique()
person_default = ["李树伟","薛爱迪","杨雪","徐雷","季嗣珉","朱强","孙波","戴鼎章"]

selected_persons = st.multiselect(
    "选择人员",
    options=sorted(person_list),
    default=[p for p in person_default if p in person_list]
)

df_person = df_valid[df_valid["接收人"].isin(selected_persons)]

person_dist = pd.crosstab(
    df_person["接收人"],
    df_person["时长区间"]
).reindex(columns=labels, fill_value=0)

person_dist = person_dist.reset_index()

fig_person = px.bar(
    person_dist,
    x="接收人",
    y=labels
)

st.plotly_chart(fig_person, width="stretch")

# =====================
# ⭐ 机床对比（按全局频次排序）
# =====================
st.subheader("⚙️ 机床时长区间对比")

machine_list = df_valid["使用设备"].dropna().unique()

# ⭐ 默认选 Top5（按频次）
top5_machines = (
    df_valid["使用设备"]
    .value_counts()
    .head(5)
    .index
    .tolist()
)

selected_machines = st.multiselect(
    "选择机床",
    options=sorted(machine_list),
    default=top5_machines
)

# ⭐ 全局频次排序（核心）
machine_order_global = (
    df_valid["使用设备"]
    .value_counts()
    .index
    .tolist()
)

# ⭐ 当前筛选数据
df_machine = df_valid[df_valid["使用设备"].isin(selected_machines)]

machine_dist = pd.crosstab(
    df_machine["使用设备"],
    df_machine["时长区间"]
).reindex(columns=labels, fill_value=0)

# ⭐ 按全局频次排序（只保留选中的）
machine_order = [m for m in machine_order_global if m in machine_dist.index]
machine_dist = machine_dist.loc[machine_order]

machine_dist = machine_dist.reset_index()

# ⭐ 关键：强制 Plotly 按这个顺序画
fig_machine = px.bar(
    machine_dist,
    x="使用设备",
    y=labels,
    category_orders={"使用设备": machine_dist["使用设备"].tolist()}
)

fig_machine.update_layout(xaxis_tickangle=-30)

st.plotly_chart(fig_machine, width="stretch")

from utils.time import get_update_time
update_time = get_update_time(df)
st.caption(f"📌 数据更新至：{update_time.strftime('%Y-%m-%d %H:%M:%S')}")