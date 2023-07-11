import math
import random

# 物联网设备数量
n = 10
# 基站数量
m = 2
channel_capacity = {}
with open("../GenerateData/UAV_BS/channel_capacity.txt", 'r', encoding="utf8") as data:
    data.readline().strip('\n')
    data.readline().strip('\n')
    for i in range(n):
        for i in range(m):
            List1 = list(data.readline().strip('\n').split())
            # List2 = list(data.readline().strip('\n').split())
            channel_capacity[int(List1[0]), int(List1[1])] = int(List1[2])
            # channel_capacity[int(List2[0]), int(List2[1])] = int(List2[2])
        for i in range(10-m):
            data.readline().strip('\n')
# print(channel_capacity)
# 带宽
B = 20

# 信噪比
# s_n = []
BS_channel_capacity = [0 for i in range(m)]
# for i in range(m):
#     s_n.append(random.randint(30, 50))
# for i in range(m):
#     BS_channel_capacity.append(B * math.log2(1 + 10 ** (s_n[i] / 10)))
# print(BS_channel_capacity)
THP_BS = [0 for i in range(m)]
THP_DTC = 0
with open("../GenerateData/DTC_BS/BS_channel_capacity.txt", 'r', encoding="utf8") as data_dtc:
    data_dtc.readline().strip('\n')
    THP_DTC = int(data_dtc.readline().strip('\n'))
    for i in range(m):
        List = list(data_dtc.readline().strip('\n').split())
        THP_BS[i] = int(List[1])
        BS_channel_capacity[i] = int(List[2])
# print(BS_channel_capacity)
with open("uav_data_10.txt", 'w', encoding='utf8') as file:
    # 写入基站数量
    file.write("%d\n" % m)
    # 写入基站吞吐量和信道容量
    for i in range(m):
        # 基站 信道容量 吞吐量
        file.write("%d %d %d\n" % (i + 1, (BS_channel_capacity[i]*5), (THP_BS[i]*5)))
    # 写入DTC的吞吐量
    file.write("%d\n" % (THP_DTC*5))
    # 写入基站与无人机之间的信道容量
    for i in range(n):
        for j in range(m):
            file.write("%d %d %d\n" % (i + 1, j + 1, channel_capacity[i + 1, j + 1]))
            # file.write()
