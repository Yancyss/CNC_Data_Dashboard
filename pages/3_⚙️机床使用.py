import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data

st.set_page_config(page_title="机床看板", layout="wide")

st.header("⚙️ 机床使用分析看板")

# =====================
# ⭐ Sidebar（时间筛选）
# =====================
st.sidebar.header("筛选条件")

range_option = st.sidebar.selectbox(
    "时间范围",
    ["近1月","近3月","近5月","近1年","近3年","近5年"],
    index=3
)

# =====================
# ⭐ 数据加载
# =====================
df = load_data()
df["委托时间"] = pd.to_datetime(df["委托时间"], errors="coerce")

max_time = df["委托时间"].max()

month_map = {"近1月":1,"近3月":3,"近5月":5}
year_map = {"近1年":1,"近3年":3,"近5年":5}

if range_option in month_map:
    df_range = df[df["委托时间"] >= max_time - pd.DateOffset(months=month_map[range_option])]
else:
    df_range = df[df["委托时间"] >= max_time - pd.DateOffset(years=year_map[range_option])]

# =====================
# ⭐ 机床频次（排序）
# =====================
st.subheader("📊 机床使用频次")

machine_count = df_range["使用设备"].value_counts().sort_values(ascending=False)

col1, col2 = st.columns(2)

# 👉 左：Top15柱状图
with col1:
    top15 = machine_count.head(15)
    df_top15 = top15.reset_index()
    df_top15.columns = ["机床", "使用次数"]

    fig = px.bar(df_top15, x="机床", y="使用次数")
    fig.update_layout(xaxis_tickangle=-30)

    st.plotly_chart(fig, width="stretch")

# 👉 右：完整表格（仍然全量）
with col2:
    df_count = machine_count.reset_index()
    df_count.columns = ["机床", "使用次数"]
    st.dataframe(df_count, width="stretch")

# =====================
# ⭐ Top10
# =====================
st.subheader("🏆 Top10 机床")

top10 = machine_count.head(10)
top10_df = top10.reset_index()
top10_df.columns = ["机床", "次数"]

fig_top10 = px.bar(top10_df, x="机床", y="次数")
fig_top10.update_layout(xaxis_tickangle=-30)

st.plotly_chart(fig_top10, width="stretch")

# =====================
# ⭐ 机床筛选（核心）
# =====================
st.subheader("🔍 机床分析")

# 默认Top5
default_machines = machine_count.head(5).index.tolist()

selected_machines = st.multiselect(
    "选择机床（可多选）",
    options=machine_count.index.tolist(),  # 已按频次排序
    default=default_machines
)

# 防止空
if len(selected_machines) == 0:
    st.warning("请选择至少一个机床")
    st.stop()

df_sel = df_range[df_range["使用设备"].isin(selected_machines)].copy()

# =====================
# ⭐ 月度趋势（可选机床）
# =====================
st.subheader("📈 月度趋势")

df_sel["月份"] = df_sel["委托时间"].dt.to_period("M").dt.to_timestamp()

trend = df_sel.groupby(["月份", "使用设备"]).size().reset_index(name="数量")

fig_trend = px.line(
    trend,
    x="月份",
    y="数量",
    color="使用设备",
    markers=True
)

fig_trend.update_xaxes(tickformat="%Y-%m", tickangle=45)

st.plotly_chart(fig_trend, width="stretch")

# =====================
# ⭐ 热力图（联动筛选）
# =====================
st.subheader("🔥 委托时间分布（热力图）")

df_sel["小时"] = df_sel["委托时间"].dt.hour
df_sel["星期"] = df_sel["委托时间"].dt.dayofweek

week_map = {0:"周一",1:"周二",2:"周三",3:"周四",4:"周五",5:"周六",6:"周日"}
df_sel["星期"] = df_sel["星期"].map(week_map)

heat = df_sel.groupby(["星期", "小时"]).size().reset_index(name="数量")

# 顺序固定
week_order = ["周一","周二","周三","周四","周五","周六","周日"]
heat["星期"] = pd.Categorical(heat["星期"], categories=week_order, ordered=True)

fig_heat = px.density_heatmap(
    heat,
    x="小时",
    y="星期",
    z="数量",
    nbinsx=24,
    color_continuous_scale="Blues"
)

fig_heat.update_xaxes(tickmode="linear", dtick=1)

st.plotly_chart(fig_heat, width="stretch")