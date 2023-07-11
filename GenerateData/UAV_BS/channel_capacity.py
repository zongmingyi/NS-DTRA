# 生成基站与物联网设备之间、DTC与基站之间的信道容量
import math
import random

with open('../raw_data/aau_dataset_data.txt', 'r', encoding='utf8') as data:
    n = int(data.readline().rstrip('\n'))
    print(n)
# 基站数量
m = 10
# 信道带宽MHZ
B = 1
# 信噪比
s_n = [[0.0 for j in range(n)] for i in range(m)]
# 基站之间的信道容量
channel_capacity = [[0.0 for j in range(n)] for i in range(m)]
# print(channel_capacity)
# print(s_n)
for i in range(m):
    for j in range(n):
        s_n[i][j] = random.randint(20, 30)
# print(s_n)
for i in range(m):
    for j in range(n):
        random_num = random.randint(0, 10)
        if random_num < 0:
            channel_capacity[i][j] = 0
        else:
            channel_capacity[i][j] = B * math.log2((1 + 10 ** (s_n[i][j] / 10)))
# print(channel_capacity)
with open("channel_capacity_2.txt", 'w', encoding='utf8') as file:
    file.write("%d\n" % m)  # 无人机基站数量
    file.write("%d\n" % n)  # 物联网设备数量
    for j in range(n):
        # file.write("%d\n" % (j + 1))
        for i in range(m):
            # 基站 设备 信道容量
            file.write("%d %d %d\n" % (j+1, i+1, channel_capacity[i][j]))
