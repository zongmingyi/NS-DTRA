import math
import random

# 带宽
B = 20
m = 10
# 信噪比
s_n = []
BS_channel_capacity = []
for i in range(m):
    s_n.append(random.randint(30, 40))
for i in range(m):
    BS_channel_capacity.append(B * math.log2(1 + 10 ** (s_n[i] / 10)))
# print(BS_channel_capacity)
THP_BS = [800 for i in range(m)]
THP_DTC = 2000

with open("BS_channel_capacity.txt", 'w', encoding="utf8") as file:
    # 写入基站数量
    file.write("%d\n" % m)
    # DTC的吞吐量
    file.write("%d\n" % THP_DTC)
    # 基站 吞吐量 基站与DTC之间的信道容量
    for i in range(m):
        file.write("%d %d %d\n" % (i + 1, THP_BS[i], BS_channel_capacity[i]))

