import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "tasks.json"

# =====================
# ⭐ 数据读写
# =====================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

tasks = load_data()

# =====================
# ⭐ 页面标题
# =====================
st.title("📋 不可量化工作统计")

# =====================
# ⭐ 新增 / 编辑
# =====================
st.subheader("➕ 新增 / 编辑任务")

# 当前编辑索引
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

edit_task = {}
if st.session_state.edit_index is not None:
    edit_task = tasks[st.session_state.edit_index]

col1, col2, col3 = st.columns(3)

with col1:
    project = st.text_input("项目名称", value=edit_task.get("项目名称", ""))

with col2:
    owner = st.text_input("负责人", value=edit_task.get("负责人", ""))

with col3:
    status = st.selectbox(
        "当前状态",
        ["在编辑", "在修改", "在校核"],
        index=["在编辑", "在修改", "在校核"].index(edit_task.get("当前状态", "在编辑"))
    )

col4, col5 = st.columns(2)

with col4:
    start_time = st.text_input(
        "模型接到时间",
        value=edit_task.get("模型接到时间", datetime.now().strftime("%Y-%m-%d %H:%M"))
    )

with col5:
    end_time = st.text_input(
        "完成时间",
        value=edit_task.get("完成时间", "")
    )

# =====================
# ⭐ 保存按钮
# =====================
if st.button("💾 保存"):
    if project == "":
        st.warning("项目名称不能为空")
    else:
        if st.session_state.edit_index is None:
            # 新增（插入到最前面）
            new_task = {
                "序号": len(tasks) + 1,
                "项目名称": project,
                "负责人": owner,
                "模型接到时间": start_time,
                "当前状态": status,
                "完成时间": end_time
            }
            tasks.insert(0, new_task)
        else:
            # 编辑
            tasks[st.session_state.edit_index].update({
                "项目名称": project,
                "负责人": owner,
                "模型接到时间": start_time,
                "当前状态": status,
                "完成时间": end_time
            })
            st.session_state.edit_index = None

        save_data(tasks)
        st.rerun()

# =====================
# ⭐ 卡片展示（倒序）
# =====================
st.subheader("📌 任务卡片")

for i, task in enumerate(tasks):
    with st.container():
        st.markdown(f"""
        ### 🧾 {task['项目名称']}
        - 👤 负责人：{task['负责人']}
        - ⏱ 接到时间：{task['模型接到时间']}
        - 🔄 状态：{task['当前状态']}
        - ✅ 完成时间：{task['完成时间']}
        """)

        col1, col2 = st.columns(2)

        # 编辑按钮
        with col1:
            if st.button(f"✏️ 编辑_{i}"):
                st.session_state.edit_index = i
                st.rerun()

        # 删除按钮（可选）
        with col2:
            if st.button(f"🗑 删除_{i}"):
                tasks.pop(i)
                save_data(tasks)
                st.rerun()

        st.divider()