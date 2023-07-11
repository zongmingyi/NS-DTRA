import random

# 物联网设备数量
n = 1000
raw_data = []
data_value = []
for i in range(n):
    raw_data.append(random.randint(6, 20))
# print(raw_data)
for i in range(n):
    data_value.append(random.randint(50, 90))
print(data_value)
with open("aau_dataset_data.txt", 'w', encoding="utf8") as file:
    file.write("%d\n" % n)
    # 写入原始数据大小以及数据价值
    for i in range(n):
        file.write("%d %d %d\n" % (i + 1, raw_data[i], data_value[i]))
