import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data
from utils.preprocess import get_valid_data, add_duration

st.set_page_config(page_title="委托单看板", layout="wide")

# =====================
# ⭐ Sidebar
# =====================
st.sidebar.header("全局设置")

range_option = st.sidebar.selectbox(
    "数据范围",
    ["近5年", "近3年", "近1年", "全部数据"],
    index=0
)

theme_mode = st.sidebar.selectbox("主题模式", ["浅色模式", "暗色模式"])

# =====================
# ⭐ 主题
# =====================
if theme_mode == "暗色模式":
    template = "plotly_dark"
    bg = "rgba(0,0,0,0)"
    font_color = "white"
    card_bg ="#1f2933"
    card_font = "white"

    st.markdown("""
    <style>
    .stApp {background-color:#0e1117;color:white;}
    </style>
    """, unsafe_allow_html=True)
else:
    template = "plotly_white"
    bg = "white"
    font_color = "black"
    card_bg = "#f8f9fa"
    card_font = "black"

# =====================
# ⭐ 卡片容器（新增）
# =====================
def card_start():
    return f"""
    <div style="
        background:{card_bg};
        padding:15px;
        border-radius:14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom:15px;
    ">
    """

def card_end():
    return "</div>"

# =====================
# ⭐ 图表统一风格
# =====================
def style(fig):
    fig.update_layout(
        template=template,
        plot_bgcolor=bg,
        paper_bgcolor=bg,
        font=dict(color=font_color, size=14),
        margin=dict(t=40, b=30, l=30, r=30),
        xaxis=dict(title=""),
        yaxis=dict(title="")
    )
    return fig

# =====================
# ⭐ 数据
# =====================
df = load_data()
df["委托时间"] = pd.to_datetime(df["委托时间"], errors="coerce")

if range_option != "全部数据":
    year_map = {"近1年":1,"近3年":3,"近5年":5}
    years = year_map[range_option]
    max_time = df["委托时间"].max()
    df = df[df["委托时间"] >= max_time - pd.DateOffset(years=years)]

df_valid = get_valid_data(df)
df_valid = add_duration(df_valid)

# =====================
# ⭐ 标题
# =====================
st.markdown("""
<h1 style='text-align:center;
           font-size:48px;
           font-weight:800;
           letter-spacing:1px;
           margin-bottom:10px;'>
📊 委托单全局分析看板
</h1>
""", unsafe_allow_html=True)

# =====================
# ⭐ KPI
# =====================
total = len(df)
done = df["接收时间"].notna().sum()
todo = df["接收时间"].isna().sum()
avg_time = df_valid["处理时长(小时)"].mean()

col1,col2,col3,col4 = st.columns(4)

def metric(col, title, value):
    col.markdown(f"""
    <div style="
        background:{card_bg};
        padding:20px;
        border-radius:12px;
        text-align:center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    ">
        <div style="font-size:16px; color:{card_font}; opacity:0.7">
            {title}
        </div>
        <div style="font-size:42px; font-weight:bold; color:{card_font}; margin-top:6px">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)

metric(col1,"总委托单",total)
metric(col2,"已完成",done)
metric(col3,"未完成",todo)
metric(col4,"平均时长(h)",round(avg_time,2) if pd.notna(avg_time) else 0)

st.divider()

# =====================
# ⭐ 趋势图（增强版）
# =====================
st.markdown(card_start(), unsafe_allow_html=True)

st.subheader("📈 委托量趋势（月度）")

df["月份"] = df["委托时间"].dt.to_period("M").dt.to_timestamp()
trend = df.groupby("月份").size().reset_index(name="数量")

fig_trend = px.line(
    trend,
    x="月份",
    y="数量",
    markers=True,
    labels={"月份":"", "数量":""}
)

fig_trend.update_traces(
    line=dict(width=4, color="#4A90E2"),
    marker=dict(size=7)
)

fig_trend = style(fig_trend)

fig_trend.update_xaxes(tickformat="%Y-%m", tickangle=45)

st.plotly_chart(fig_trend, use_container_width=True)
st.markdown(card_end(), unsafe_allow_html=True)

# =====================
# ⭐ 饼图函数（增强）
# =====================
def pie_top(series, title, topn=7):
    data = series.value_counts().head(topn)

    fig = px.pie(names=data.index, values=data.values)

    fig.update_traces(
        textinfo="percent+label",
        textfont_size=16,
        pull=[0.05]*len(data)
    )

    st.markdown(card_start(), unsafe_allow_html=True)
    st.subheader(title)
    st.plotly_chart(style(fig), use_container_width=True)
    st.markdown(card_end(), unsafe_allow_html=True)

# =====================
# ⭐ 饼+柱模块（增强）
# =====================
def block(series, title, colname):
    c1,c2 = st.columns(2)

    with c1:
        pie_top(series, f"{title}分布")

    with c2:
        top = series.value_counts().head(7).reset_index()
        top.columns=[colname,"数量"]

        fig = px.bar(
            top,
            x=colname,
            y="数量",
            labels={colname:"", "数量":""}
        )

        # ⭐ 渐变蓝色
        fig.update_traces(
            marker=dict(
                color=top["数量"],
                colorscale="Blues"
            )
        )

        st.markdown(card_start(), unsafe_allow_html=True)
        st.subheader(f"{title} TOP7")
        st.plotly_chart(style(fig), use_container_width=True)
        st.markdown(card_end(), unsafe_allow_html=True)

# =====================
# ⭐ 委托单位
# =====================
block(df["委托单位"],"委托单位","单位")

# =====================
# ⭐ 机床
# =====================
c1,c2 = st.columns(2)

with c1:
    data = df_valid["使用设备"].value_counts()
    top = data.head(7)
    other = data.iloc[7:].sum()
    if other > 0:
        top["其他"] = other

    fig = px.pie(names=top.index, values=top.values)
    fig.update_traces(textinfo="percent+label", textfont_size=16)

    st.markdown(card_start(), unsafe_allow_html=True)
    st.subheader("⚙️ 机床使用分布")
    st.plotly_chart(style(fig), use_container_width=True)
    st.markdown(card_end(), unsafe_allow_html=True)

with c2:
    top = df_valid["使用设备"].value_counts().head(7).reset_index()
    top.columns=["设备","数量"]

    fig = px.bar(top,x="设备",y="数量",labels={"设备":"","数量":""})

    fig.update_traces(
        marker=dict(color=top["数量"], colorscale="Blues")
    )

    st.markdown(card_start(), unsafe_allow_html=True)
    st.subheader("机床 TOP7")
    st.plotly_chart(style(fig), use_container_width=True)
    st.markdown(card_end(), unsafe_allow_html=True)

# =====================
# ⭐ 接收人
# =====================
block(df_valid["接收人"],"接收人","人员")

# =====================
# ⭐ 委托人
# =====================
block(df["委托人"],"委托人","委托人")

# =====================
# ⭐ 时间分析
# =====================
st.subheader("📅 时间行为分析")

c1,c2 = st.columns(2)

with c1:
    week_map = {0:"周一",1:"周二",2:"周三",3:"周四",4:"周五",5:"周六",6:"周日"}
    df["星期"] = df["委托时间"].dt.dayofweek.map(week_map)

    order = ["周一","周二","周三","周四","周五","周六","周日"]
    data = df["星期"].value_counts().reindex(order)

    fig = px.pie(names=data.index, values=data.values)
    fig.update_traces(textinfo="percent+label", textfont_size=16)

    st.markdown(card_start(), unsafe_allow_html=True)
    st.subheader("周几分布")
    st.plotly_chart(style(fig), use_container_width=True)
    st.markdown(card_end(), unsafe_allow_html=True)

with c2:
    df["小时"] = df["委托时间"].dt.hour
    hour = df["小时"].value_counts().reindex(range(24), fill_value=0)

    hour_df = pd.DataFrame({"小时": hour.index, "数量": hour.values})

    fig = px.bar(hour_df,x="小时",y="数量",labels={"小时":"","数量":""})
    fig.update_traces(marker=dict(color=hour_df["数量"], colorscale="Blues"))

    st.markdown(card_start(), unsafe_allow_html=True)
    st.subheader("24小时分布")
    st.plotly_chart(style(fig), use_container_width=True)
    st.markdown(card_end(), unsafe_allow_html=True)