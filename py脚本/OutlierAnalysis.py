'''
莱芜VOCS异常点分析
'''

import pandas as pd
import sqlite3
import json, time, os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 修改文件路径
os.chdir(r'C:\Users\NOVA\Desktop\jinan\1221-0103')

# 1.建立db连接，读取数据  "car_no", "sn", "lat", "lng", "time", "loc_time", "speed", "content"
sql = "select car_no, sn, lat, lng, time, loc_time, speed, content from sensordatagps where content is not null"
allData = pd.DataFrame()
for dir in os.listdir():
    conn = sqlite3.connect(dir)
    df = pd.read_sql(sql, conn)  # 读取数据
    allData = pd.concat([allData, df])

allData.shape
allData.columns

# 2 拆分字段
# 2.1 拆分content
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
    return contentDict.get("vocs_1", 0.1) if n == 1 else contentDict.get("vocs_2", 0.1)  # 此处0.1为之后作为分母不为0做准备
# 2.2 拆分time为hour
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

allData['vocs1'] = allData['content'].apply(lambda x: splitContent(x, 1))
allData['vocs2'] = allData['content'].apply(lambda x: splitContent(x, 2))



# 3. 抽样检测不同设备的数据分布
allSN = allData[['sn']].drop_duplicates()  # 过去2周产生数据的全部sn

## 3.1 分布直方图函数
def plotHist(sn):
    dataSingleSn = allData[allData['sn'] == sn]
    fig, axs = plt.subplots(2, 1)
    plt.title(sn)
    vocs1 = dataSingleSn['vocs1']
    vocs2 = dataSingleSn['vocs2']

    axs[0].plot(range(vocs1.shape[0]), vocs1, c='b', label='vocs1', alpha=0.7)
    axs[0].plot(range(vocs2.shape[0]), vocs2, c='r', label='vocs2', alpha=0.5)
    axs[0].set_ylabel("Vocs")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].hist(vocs1, bins=50, density=False, color='b', alpha=0.7)
    axs[1].hist(vocs2, bins=50, density=False, color='r', alpha=0.5)
    axs[1].set_xlabel("Vocs")
    axs[1].set_ylabel("数量")
    plt.show()

# sns = ["B616-104C",
#        "B616-101D",
#        "B616-1016",
#        "B616-1011",
#        "B616-1036",
#        "B616-1058",
#        "B616-1034",
#        "B616-1043",
#        "B616-1022",
#        "B616-1023"]

sns = ["B616-1013",
       "B616-106D",
       "B616-1011",
       "B616-1020",
       "B61A-10E7",
       "B616-101D"]

for sn in sns:
    plotHist(sn)

# 4. 检测正常设备
allData.describe()
staticBySn = allData.groupby('sn').count().sort_values("vocs1", ascending=False)
staticBySn.describe()
staticBySn[staticBySn['vocs1'] < 120000]

## 4.1 检测每个sn宕机数据占比
# sn = "B616-1036"
dictTemp = {"sn":[], "zeroDataPercent":[]}
sindex = staticBySn.index
for sn in sindex:
    # dataSingleSn = allData[allData['sn'] == sn][['sn', 'lat', 'lng', 'time', 'vocs1', 'vocs2']]
    dataSingleSn = allData[allData['sn'] == sn][['sn', 'vocs1', 'vocs2']]
    # dataSingleSn.index = range(dataSingleSn.shape[0])
    dataSingleSn["vocs12iszero"] = dataSingleSn.apply(lambda x: 1 if x['vocs1'] > 11 and x['vocs2'] > 11 else 0, axis=1)
    # zeroIndex = dataSingleSn[dataSingleSn['vocs12iszero'] == 0].index
    # dataSingleSn.shape

    zeroDataPercent = dataSingleSn[dataSingleSn['vocs12iszero'] == 0].shape[0] / dataSingleSn.shape[0]
    print(sn, "：宕机数据占比--->", zeroDataPercent)
    dictTemp['sn'] += [sn]
    dictTemp['zeroDataPercent'] += [zeroDataPercent]

zeroDataPercentDF = pd.DataFrame(dictTemp)
zeroDataPercentDF.describe()
zeroDataPercentDF.sort_values("zeroDataPercent", ascending=False, inplace=True)

# fig, ax = plt.subplots()
# ax.barh(zeroDataPercentDF.shape[0], zeroDataPercentDF['zeroDataPercent'], align='center')
# ax.set_yticks(range(zeroDataPercentDF.shape[0]))
# ax.set_yticklabels(zeroDataPercentDF['sn'])
# ax.invert_yaxis()
# ax.set_xlabel("ZeroDataPercent")
# ax.set_title("All SN zero data percent")
# plt.show()

# plt.rcParams['savefig.dpi'] = 300 #图片像素
plt.rcParams['figure.dpi'] = 300 #分辨率
plt.bar(range(zeroDataPercentDF.shape[0]), zeroDataPercentDF['zeroDataPercent'], 0.2, tick_label=zeroDataPercentDF['sn'])
plt.xticks(rotation=45, fontsize=5)
plt.title("宕机数据占比")
plt.savefig(r'C:\Users\NOVA\Desktop\jinan\宕机数据占比.jpg')
plt.show()

### 删除宕机100%的5台设备
zeroSn = zeroDataPercentDF[zeroDataPercentDF['zeroDataPercent'] == 1]['sn'].values

allData.shape  # (8275150, 10)
allData[allData['sn'].apply(lambda x: x in zeroSn)].shape  # 宕机设备数据 (532780, 10)
allData.drop(allData[allData['sn'].apply(lambda x: x in zeroSn)].index, inplace=True)
allData.shape

## 4.2 通过相关系数corr判断设备的正常指数 文中3.1.1 （二）部分



