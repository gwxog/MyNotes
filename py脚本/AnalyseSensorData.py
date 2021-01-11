import pandas as pd
import sqlite3
import json, time, os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 修改文件路径
os.chdir(r'C:\Users\NOVA\Desktop\jinan')

# 1.建立db连接
conn = sqlite3.connect(r"sensordatagps_2020-12-21_00-00-00 - 1.db")

# 2.读取数据
# sql = "select * from sensordatagps where car_no='鲁U-T0767'"
sql = "select * from sensordatagps1"
df = pd.read_sql(sql, conn)  # 读取数据
df.shape
# 3.分析
# 3.1 删除空数据
df[df["speed"] == ""].shape
df[df["speed"] == 0].shape
df[df["speed"].isnull()].shape

df[df["enable_level"] != "1"].shape  # (4526, 24)

df = df[df["enable_level"] == "1"]
df.shape  # (578800, 8)

# 3.2 筛选字段
df1 = df[["car_no", "sn", "lat", "lng", "time", "loc_time", "speed", "content"]]
df1.shape  # (578800, 8)

# 3.3 拆分
# 3.3.1 拆分content
def splitContent(content, n):
    '''
    分解content为vocs_1和vocs_2
    :param content: 字段content
    :param n: 取值1或2
    :return: n=1返回vocs_1，n=2返回vocs_2
    '''
    if n not in [1, 2]:
        raise ValueError("n=1 or n=2, not else")
    contentDict = json.loads(content)
    return contentDict.get("vocs_1", 0.0)/2 if n == 1 else contentDict.get("vocs_2", 0.0)/2
# 3.3.2 拆分time为hour
def splitTime(time, timeUnit):
    '''
    拆分时间
    :param time: 字段time
    :param timeUnit: 拆为hour or minute or date
    :return:
    '''
    if timeUnit not in ["hour", "minute", "date", "hour:minute", "hour:minute:second"]:
        raise ValueError("timeUnit is not desired value, please input hour or minute or date or hour:minute or hour:minute:second")
    if timeUnit == "hour": return int(time.split(" ")[1].split(":")[0])
    if timeUnit == "minute": return int(time.split(" ")[1].split(":")[1])
    if timeUnit == "date": time.split(" ")[0]
    if timeUnit == "hour:minute": return ":".join(time.split(" ")[1].split(":")[:2])
    if timeUnit == "hour:minute:second": return time.split(" ")[1].split["."][0]




df1['vocs1'] = df1['content'].apply(lambda x: splitContent(x, 1))
df1['vocs2'] = df1['content'].apply(lambda x: splitContent(x, 2))
df1[df1["vocs2"] == 0].shape  # (16775, 10)

df1['hour'] = df1['time'].apply(lambda x: splitTime(x, "hour"))
df1['hourminute'] = df1['time'].apply(lambda x: splitTime(x, "hour:minute"))



#####################绘图#######################
# 绘制vocs1,vocs2的散点分布图
# 定义绘制散点图函数
vocs1 = df1[df1["sn"] == "B616-1011"]["vocs1"]
vocs2 = df1[df1["sn"] == "B616-1011"]["vocs2"]
hour = df1[df1["sn"] == "B616-101C"]["hour"]
hourminute = df1[df1["sn"] == "B616-101C"]["hourminute"]


# 以时间为横轴画图
plt.figure(1)
plt.scatter(hour, vocs1, color='r', marker='.', s=2, alpha=0.7, label="vocs1")
plt.scatter(hour, vocs2, color='b', marker='+', s=2, alpha=0.7, label="vocs2")
plt.show()



# 绘制分布直方图




# 绘制时序图
# 图片大小设置
fig = plt.figure(figsize=(15,9), dpi=200)
ax = fig.add_subplot(111)

# X轴时间刻度格式 & 刻度显示
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
# plt.xticks(pd.date_range(table.index[0],table.index[-1],freq='H'), rotation=45)
plt.xticks(pd.date_range(df1["hourminute"][0],df1["hourminute"][df1.shape[0]],freq='T'), rotation=45)

# 绘图
ax.plot(hourminute, vocs1, color='r', label='12月21日 vocs1')
ax.plot(hourminute, vocs2, color='b', label='12月21日 vocs2')
# ax.plot(table.index,df_0915['avg_speed'],color='y', label='9月15日')
# ax.plot(table.index,df_0916['avg_speed'],color='g', label='9月16日')

# 辅助线
# sup_line = [35 for i in range(480)]
# ax.plot(table.index, sup_line, color='black', linestyle='--', linewidth='1', label='辅助线')

plt.xlabel('time_point', fontsize=14)    # X轴标签
plt.ylabel("Vocs", fontsize=16)         # Y轴标签
ax.legend()                              # 图例
plt.title("Vocs时序图", fontsize=25, color='black', pad=20)
plt.gcf().autofmt_xdate()

# 隐藏-上&右边线
# ax.spines['right'].set_color('none')
# ax.spines['top'].set_color('none')

# plt.savefig('speed.png')
plt.show()





#####################求统计指标#######################
df1.columns
# 相关系数
vocs1.corr(vocs2)
df1.vocs1.corr(df1.vocs2)
# 协方差
vocs1.cov(vocs2)
df1.vocs1.cov(df1.vocs2)

import math
def computeCosSimilar(seq1, seq2):
    '''
    计算余弦相似度
    :param seq1:
    :param seq2:
    :return:
    '''
    mod1 = 0
    mod2 = 0
    sum12 = 0
    for i, j in zip(seq1, seq2):
        sum12 += i * j
        mod1 += i**2
        mod2 += j**2
    # 余弦相似度
    cosVocs12 = sumVocs12 / math.sqrt(modVocs1 * modVocs2)
    return cosVocs12
print(computeCosSimilar(df1.vocs1, df1.vocs2))
print(computeCosSimilar(vocs1, vocs2))



# 计算平均连续运行时长






# 计算每30条数据的corr
df1011 = df1[df1["sn"] == "B616-106D"]
df1011["corr"] = 0
df1011.index = range(df1011.shape[0])
df1011.columns
df1011.shape

j = 0
for i in range(df1011.shape[0]):
# for i in range(100):
    if i % 30 == 0 and i != 0:
        vocs1i = df1011.iloc[j:i, -5]
        if vocs1i.sum() == 0:
            vocs1i += 0.1  # 防止作为分母为0的错误
        vocs2i = df1011.iloc[j:i, -4]
        if vocs2i.sum() == 0:
            vocs2i += 0.1  # 防止作为分母为0的错误
        print(i, j)
        j = i
        corr = vocs1i.corr(vocs2i)
        if pd.isna(corr):
            df1011.iloc[i, -1] = 0
        else:
            df1011.iloc[i, -1] = corr
df1011[df1011["corr"] != 0]

df1011[df1011["corr"] != 0]["corr"].mean()


fig, ax1 = plt.subplots()

plt.title("12月21日B616-106D设备VOCS和CORR走势图")
ax1.plot(range(df1011.shape[0]), df1011['vocs1'], color='r', label='12月21日 vocs1')
ax1.plot(range(df1011.shape[0]), df1011['vocs2'], color='b', label='12月21日 vocs2')
ax1.set_ylabel("Vocs")
ax1.legend()

ax2 = ax1.twinx()
# ax2.scatter(range(df1011.shape[0]), df1011['corr'], color='k', s=5, marker="+", label='12月21日 corr')

x = [i for i in range(df1011.shape[0]) if i % 30 == 0 and i != 0]
y = df1011[(df1011.index % 30 == 0).reshape(-1, 1) * (df1011.index != 0).reshape(-1, 1)]['corr']
ax2.scatter(x, y, color='k', s=5, marker="+", label='12月21日 corr')
ax2.set_ylabel("Corr")
ax2.legend()
ax2.set_ylim(-1, 1)
plt.show()




# 绘制时序图
# 图片大小设置
fig = plt.figure(figsize=(15,9), dpi=200)
ax = fig.add_subplot(111)

# X轴时间刻度格式 & 刻度显示
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
# plt.xticks(pd.date_range(table.index[0],table.index[-1],freq='H'), rotation=45)
plt.xticks(pd.date_range(df1011[["hourminute"]].iloc[0, 0],df1011[["hourminute"]].iloc[-1, 0],freq='T'), rotation=45)

# 绘图
ax.plot(hourminute, df1011['vocs1'], color='r', label='12月21日 vocs1')
ax.plot(hourminute, df1011['vocs2'], color='b', label='12月21日 vocs2')
ax.plot(hourminute, df1011['corr'], color='b', label='12月21日 vocs2')
# ax.plot(table.index,df_0915['avg_speed'],color='y', label='9月15日')
# ax.plot(table.index,df_0916['avg_speed'],color='g', label='9月16日')

# 辅助线
# sup_line = [35 for i in range(480)]
# ax.plot(table.index, sup_line, color='black', linestyle='--', linewidth='1', label='辅助线')

plt.xlabel('time_point', fontsize=14)    # X轴标签
plt.ylabel("Vocs", fontsize=16)         # Y轴标签
ax.legend()                              # 图例
plt.title("Vocs时序图", fontsize=25, color='black', pad=20)
plt.gcf().autofmt_xdate()

# 隐藏-上&右边线
# ax.spines['right'].set_color('none')
# ax.spines['top'].set_color('none')

# plt.savefig('speed.png')
plt.show()
