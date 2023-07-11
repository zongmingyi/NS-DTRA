user = []
bids = []
cpu = []
mem = []
bw = []
data_value = []
# 物联网设备数量
n = 100
with open("../GenerateData/pretreat_data/auu_user_parameter.txt") as data:
    data.readline().strip('\n')
    for i in range(n):
        List = list(data.readline().strip('\n').split())
        user.append(int(List[0]))
        bids.append(float(List[1]))
        cpu.append(int(List[2]))
        mem.append(int(List[3]))
        bw.append(int(List[4]))
        data_value.append(int(List[5]))
total_cpu = 0
total_mem = 0
for i in range(n):
    total_cpu += cpu[i]
    total_mem += mem[i]
print(total_cpu)
print(total_mem)
with open("experiment_3_user.txt", 'w', encoding="utf8") as file:
    file.write("%d\n" % n)
    file.write("%d %d\n" % (total_cpu, total_mem))
    for i in range(n):
        # 用户 出价 cpu 内存 带宽 数据价值
        file.write("%d %.2f %d %d %d %d\n" % (i + 1, bids[i], cpu[i], mem[i], bw[i], data_value[i]))
print(bids)