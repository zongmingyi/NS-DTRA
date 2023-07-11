# 处理raw_data
# 收集环境数据的成本
cost_col = []
# 预处理数据的成本
cost_pre = []
# 预处理数据之后数据的大小
pre_data = []
# 物联网设备请求的带宽
require_bw = []
# 请求内存资源
mem = []
# 请求CPU资源
cpu = []
# 物联网设备的通信成本
cost_comm = []
# 物联网设备的总服务成本
cost_user = []
# 物联网设备的数据价值
data_value = []
# raw_data的大小
raw_data = []
with open('../raw_data/aau_dataset_data.txt', 'r', encoding='utf8') as data:
    n = int(data.readline().rstrip())
    for i in range(n):
        List = list(data.readline().rstrip('\n').split())
        raw_data.append(int(List[1]))
        data_value.append(int(List[2]))

    # 物联网设备收集环境数据的单位成本
    a = 1
    # 预处理数据的单位成本
    r = 0.5
    # 预处理数据之后数据的压缩率
    l = 0.5
    # dtc广播的传输时间
    t = 1
    # 处理单位数据所需要的CPU指令周期数 单位：KIPS，MIPS  MHZ
    tao = 1.5
    # 处理单位用户数据所需要的内存数量
    rho = 1
    # 物联网设备的单位时间通信成本
    beta = 5
    for i in range(n):
        pre_data.append(raw_data[i] * l)
        cost_pre.append(raw_data[i] * r)
        cost_col.append(raw_data[i] * a)
        cost_comm.append(t * beta)
    for i in range(n):
        require_bw.append(pre_data[i] / t)
        cpu.append(pre_data[i] * tao)
        mem.append(pre_data[i] * rho)
    for i in range(n):
        cost_user.append(cost_comm[i] + cost_col[i] + cost_pre[i])
print(cost_pre)
print(cost_col)
print(pre_data)
print(require_bw)
print(mem)
print(cpu)
print(cost_comm)
print(cost_user)
print(raw_data)
print(data_value)
with open("auu_user_parameter.txt", 'w', encoding='utf8') as file:
    file.write("%d\n" % n)
    for i in range(n):
        # 用户 出价 cpu 内存 带宽 数据价值
        file.write("%d %.2f %d %d %d %d\n" % (i+1, cost_user[i], cpu[i], mem[i], require_bw[i], data_value[i]))
