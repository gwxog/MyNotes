import pandas as pd
import sqlite3
import json, time, os
import matplotlib.pyplot as plt


# 修改文件路径
os.chdir(r'C:\Users\gwxog\Desktop\sensordata')

# 1.建立db连接
conn = sqlite3.connect(r"sensordatagps_2020-11-16_00-00-00.db")

# 2.读取数据
# sql = "select * from sensordatagps where car_no='鲁U-T0767'"
sql = "select * from sensordatagps"
df = pd.read_sql(sql, conn)  # 读取数据

# 3.分析
# 3.1 删除空数据
df[df["pm10"].isnull()].shape  # (16523, 24)
df[df["pm25"].isnull()].shape  # (16523, 24)
df = df[df["pm10"].notnull()]
df.shape
# 3.1 截取car_no,sn,pm10,pm25,lat,lng,latgrid,lnggrid,speed,direction,time

df1 = df[["car_no", "sn", "pm10", "pm25", "lat", "lng", "speed", "direction", "time", "grid_key"]]
df1.columns

df1["latgrid"] = df1["grid_key"].apply(lambda x: x.split(":")[1])
df1["lnggrid"] = df1["grid_key"].apply(lambda x: x.split(":")[0])

df1.head(5)
# del df1["grid_key"]
df1.columns
df1.groupby(["latgrid", "lnggrid"]).count().sort_values("car_no", axis=0, ascending=False).head(10)

pd.date_range(start='20200101',end="20200102",freq='H',closed='left')
df1['time']

plt.plot(df1['pm10'].values)
plt.scatter(range(df1.shape[0]), df1["pm10"])
df1['pm10'].max()

df1.lng.corr(df1.speed)
df1.pm10.mean()
df1.pm25.mean()
df1.pm10.cov(df1.pm25)
df1.pm10.corr(df1.pm25)
df1.var()
df1.std()
df1[df1["sn"] == "B619-008B"].std()