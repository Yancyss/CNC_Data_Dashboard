import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data
from utils.preprocess import get_valid_data

# =====================
# ⭐ 页面标题
# =====================
st.header("👤 个人工作量看板")
st.subheader("月度 / 年度工作量统计")

df = load_data()
df_valid = get_valid_data(df)

# =====================
# ⭐ Sidebar 控制区
# =====================
st.sidebar.header("筛选条件")

# 1️⃣ 角色选择
role_options = ["编制", "校核", "审定"]
selected_roles = st.sidebar.multiselect(
    "选择统计角色",
    role_options,
    default=role_options
)

if len(selected_roles) == 0:
    st.warning("请选择统计角色")
    st.stop()

# 2️⃣ 人员筛选
all_people = pd.unique(
    df_valid[["编制", "校核人", "审定人"]].values.ravel()
)
all_people = [p for p in all_people if pd.notna(p)]

default_people = ["徐雷","李树伟","朱强","孙波","薛爱迪","季嗣珉","杨雪","戴鼎章"]
selected_people = st.sidebar.multiselect(
    "选择人员",
    all_people,
    default=default_people
)

# 3️⃣ 时间（近6个月）
max_time = df_valid["接收时间"].max()
current_month_start = pd.Timestamp(max_time.year, max_time.month, 1)
end_default = current_month_start - pd.Timedelta(days=1)
start_default = current_month_start - pd.DateOffset(months=6)

start_date = st.sidebar.date_input("开始日期", start_default.date())
end_date = st.sidebar.date_input("结束日期", end_default.date())

# 4️⃣ 周期
period = st.sidebar.radio("统计周期", ["按年", "按月"], index=1)

# 5️⃣ 颜色风格
theme = st.sidebar.selectbox(
    "图表风格",
    ["默认", "蓝色系", "绿色系", "橙色系"]
)

color_map = {
    "默认": None,
    "蓝色系": px.colors.sequential.Blues,
    "绿色系": px.colors.sequential.Greens,
    "橙色系": px.colors.sequential.Oranges
}

# =====================
# ⭐ 数据筛选
# =====================
df_filtered = df_valid[
    (df_valid["接收时间"].dt.date >= start_date) &
    (df_valid["接收时间"].dt.date <= end_date)
].copy()

# =====================
# ⭐ 构造长表
# =====================
records = []

for _, row in df_filtered.iterrows():
    if "编制" in selected_roles and pd.notna(row.get("编制")):
        records.append([row["编制"], "编制", row["接收时间"]])

    if "校核" in selected_roles and pd.notna(row.get("校核人")):
        records.append([row["校核人"], "校核", row["接收时间"]])

    if "审定" in selected_roles and pd.notna(row.get("审定人")):
        records.append([row["审定人"], "审定", row["接收时间"]])

df_long = pd.DataFrame(records, columns=["人员", "角色", "接收时间"])

# =====================
# ⭐ 人员筛选应用（关键新增）
# =====================
df_long = df_long[df_long["人员"].isin(selected_people)]

if df_long.empty:
    st.warning("当前筛选条件下没有数据")
    st.stop()

# =====================
# ⭐ 周期处理
# =====================
if period == "按年":
    df_long["周期"] = df_long["接收时间"].dt.year.astype(str)
else:
    df_long["周期"] = df_long["接收时间"].dt.to_period("M")
    df_long = df_long.sort_values("周期")

period_order = sorted(df_long["周期"].unique())

# =====================
# ⭐ 工作量统计
# =====================
workload = df_long.groupby(["人员", "周期"]).size().reset_index(name="工作量")

# =====================
# ⭐ KPI
# =====================
total = workload["工作量"].sum()
people_count = workload["人员"].nunique()

col1, col2 = st.columns(2)
col1.metric("总工作量", int(total))
col2.metric("参与人数", int(people_count))

st.divider()

# =====================
# ⭐ 图表（改为堆叠）✅
# =====================
fig = px.bar(
    workload,
    x="人员",
    y="工作量",
    color="周期",
    barmode="stack",   # ✅ 核心改动：堆叠
    color_discrete_sequence=color_map[theme],
    category_orders={"周期":period_order}
)

st.plotly_chart(fig, use_container_width=True)

# =====================
# ⭐ 表格
# =====================
pivot_table = workload.pivot_table(
    index="人员",
    columns="周期",
    values="工作量",
    fill_value=0
)

st.dataframe(pivot_table)