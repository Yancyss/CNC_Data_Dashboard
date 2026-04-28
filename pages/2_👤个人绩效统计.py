import streamlit as st
import pandas as pd
from io import BytesIO
from utils.data_loader import load_data

st.set_page_config(page_title="个人绩效统计", layout="wide")

st.header("👤 个人绩效统计")
st.markdown("""
<div style='color:gray; font-size:14px; margin-top:-10px; margin-bottom:10px;'>
说明：可修改“程序数目”，用于绩效统计，导出后将按当前数值计算
</div>
""", unsafe_allow_html=True)
# =====================
# ⭐ 数据加载
# =====================
df = load_data()
time_col = "委托时间"

# =====================
# ⭐ Sidebar 筛选
# =====================
st.sidebar.header("筛选条件")

person_list = ["李树伟","薛爱迪","杨雪","徐雷","季嗣珉","朱强","孙波","戴鼎章"]
selected_person = st.sidebar.selectbox("选择人员", person_list)

# 月份
df["年月"] = df[time_col].dt.to_period("M").astype(str)
month_list = sorted(df["年月"].dropna().unique(), reverse=True)
selected_month = st.sidebar.selectbox("选择月份", month_list)

# 角色
roles = st.sidebar.multiselect(
    "选择角色",
    ["编制","校核","审定"],
    default=["编制"]
)

# 无角色提示
if len(roles) == 0:
    st.warning("⚠️ 请选择至少一个角色")
    st.stop()

# =====================
# ⭐ 数据筛选
# =====================
df_filtered = df[df["年月"] == selected_month]

mask = False
if "编制" in roles:
    mask = mask | (df_filtered["编制"] == selected_person)
if "校核" in roles:
    mask = mask | (df_filtered["校核人"] == selected_person)
if "审定" in roles:
    mask = mask | (df_filtered["审定人"] == selected_person)

# ⭐ 关键：重置索引（防止 None）
df_filtered = df_filtered[mask].copy().reset_index(drop=True)

# =====================
# ⭐ 构造展示表（彻底避免None）
# =====================
df_show = pd.DataFrame({
    "序号": range(1, len(df_filtered) + 1),
    "委托单编号": df_filtered["委托单编号"],
    "图号": df_filtered["图号"],
    "工件名称": df_filtered["工件名称"],
    "日期": df_filtered[time_col].dt.strftime("%Y-%m-%d"),
    "程序数目": 1
})

# =====================
# ⭐ 可编辑表格
# =====================
st.subheader("📋 绩效明细 ")

edited_df = st.data_editor(
    df_show,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "程序数目": st.column_config.NumberColumn(
            "程序数目",
            min_value=1,
            step=1
        )
    }
)

# =====================
# ⭐ 汇总
# =====================
total_programs = edited_df["程序数目"].sum()
st.metric("📊 程序总数", total_programs)

# =====================
# ⭐ Excel 导出（openpyxl版）
# =====================
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='绩效统计')
    return output.getvalue()

excel_data = to_excel(edited_df)

st.download_button(
    label="📥 导出 Excel",
    data=excel_data,
    file_name=f"{selected_person}_{selected_month}_绩效统计.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

from utils.time import get_update_time
update_time = get_update_time(df)
st.caption(f"📌 数据更新至：{update_time.strftime('%Y-%m-%d %H:%M:%S')}")