

#过滤掉接收人为空行的数据
def get_valid_data(df):
    return df.dropna(subset=["接收人"])

def add_duration(df):
    df = df.copy()#复制一份，不改变原始数据
    df["处理时长(小时)"] = (
        (df["接收时间"] - df["委托时间"])
        .dt.total_seconds() / 3600
    ) #把秒转化成小时
    return df