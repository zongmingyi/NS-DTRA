# 次模函数分配，二分法支付
import copy
import time
import math
from queue import Queue

# 定义一些用到的变量
start_time, end_time = None, None
# 写死的例子
# IoT_size, BS_size = 3, 2  # IoT,基站的数量
IoT_size, BS_size = 0, 0
# DTC_resource = {1: 40, 2: 45}  # DTC的资源总量
DTC_resource = {}
# bids = {1: 17, 2: 12, 3: 15}  # IoT设备的出价
bids = {}
# IoT_bws = {1: 15, 2: 19.5, 3: 5}  # IoT设备请求的带宽
# IoT_bws = {1: 11, 2: 11, 3: 5}
IoT_bws = {}
# IoT_resource = {(1, 1): 12, (1, 2): 15,
#                 (2, 1): 12, (2, 2): 15,
#                 (3, 1): 18, (3, 2): 25}  # IoT设备的资源请求
# IoT_resource = {(1, 1): 12, (1, 2): 15,
#                 (2, 1): 12, (2, 2): 15,
#                 (3, 1): 18, (3, 2): 25}
IoT_resource = {}
# IoT_value = {1: 30, 2: 30, 3: 28}  # IoT设备的图像数据价值
IoT_value = {}
# BS_THP = {1: 20, 2: 20}  # 基站的吞吐量
BS_THP = {}
# DTC_THP = 45  # DTC的吞吐量
DTC_THP = 0.0
# DTC_BS_BWs = {1: 30, 2: 23}  # DTC与基站之间的信道容量
DTC_BS_BWs = {}
# BS_CH = {1: 3, 2: 2}  # 基站信道数量
BS_CH = {}
# IoT_BS_BWs = {(1, 1): 10, (1, 2): 10,
#               (2, 1): 15.5, (2, 2): 10,
#               (3, 1): 8, (3, 2): 0}  # 物联网设备与基站之间的信道容量
IoT_BS_BWs = {}
# cost_uav = 10  # 无人机基站的服务成本
cost_uav = 0.0
cost_uav_unit = 5
with open("../Experiment_3/experiment_3_user.txt", 'r', encoding='utf8') as user_file:
    IoT_size = int(user_file.readline().strip('\n'))
    List_resource = list(user_file.readline().strip('\n').split())
    DTC_resource[1] = int(List_resource[0])
    DTC_resource[2] = int(List_resource[1])
    for i in range(IoT_size):
        List_user = list(user_file.readline().strip('\n').split())
        bids[int(List_user[0])] = float(List_user[1])
        IoT_resource[int(List_user[0]), 1] = int(List_user[2])
        IoT_resource[int(List_user[0]), 2] = int(List_user[3])
        IoT_bws[int(List_user[0])] = int(List_user[4])
        IoT_value[int(List_user[0])] = int(List_user[5])
with open("../Experiment_3/uav_data_10.txt", 'r', encoding="utf8") as uav_file:
    BS_size = int(uav_file.readline().strip('\n'))
    for i in range(BS_size):
        List1 = list(uav_file.readline().strip('\n').split())
        DTC_BS_BWs[int(List1[0])] = int(List1[1])
        BS_THP[int(List1[0])] = int(List1[2])
    DTC_THP = int(uav_file.readline().strip('\n'))
    for i in range(IoT_size):
        for j in range(BS_size):
            List2 = list(uav_file.readline().strip('\n').split())
            IoT_BS_BWs[int(List2[0]), int(List2[1])] = int(List2[2])
    cost_uav = cost_uav_unit * BS_size
# 定义一些全局变量
alloc_ret, pay, social_welfare, total_pay = None, [0.0] * IoT_size, 0.0, 0.0
alloc_f = None
last_winner = set()  # 不改变出价时的胜者集合，用来区分设备是否成为胜者
# 用户下标集合，基站下标集合，资源下标集合
set_IOT, set_BS, set_resource = range(1, IoT_size + 1), range(1, BS_size + 1), range(1, 3)

# # 定义胜者集合,这个是判断元素是否成为胜者
# winner_set = set()
# # 定义胜者列表，用来顺序加入胜者集合的元素
# winner_list = []

# 构建网络拓扑图
# 定义模型中涉及到的节点的数量:物联网设备数量+2*无人机基站数量+2*DTC+开始节点+结束节点
m = IoT_size + 2 * BS_size + 2 + 1 + 1
# print("m",m)
# 残余图的剩余流量 初始化为0
residual = []
# 最大网络流图，初始化为0
max_flow_graph = []
# 记录增广路径前进路程上记录的最小流量
flow = []
# 记录增广路径每个节点的前驱
pre = []
# 队列，用于BFS的寻找增广路径
que = Queue()
Involvement = []

tele_bs = set()

sum_flow = []


def network():
    global max_flow_graph, residual, flow, pre, social_welfare, DTC_resource, IoT_size, BS_size, bids, IoT_bws, IoT_resource, IoT_value, BS_THP, DTC_THP, DTC_BS_BWs, BS_CH, IoT_BS_BWs, cost_uav, Involvement, tele_bs, sum_flow

    # 最大网络流图，初始化为0
    max_flow_graph = [[0.0 for i in range(m)] for j in range(m)]
    # 残余图的剩余流量 初始化为0
    residual = [[0.0 for i in range(m)] for j in range(m)]
    # 记录增广路径前进路程上记录的最小流量
    flow = [0.0 for i in range(m)]
    # 记录增广路径每个节点的前驱
    pre = [float('inf') for i in range(m)]
    # 读取初始图的流量走向，在我们设计的模型中是各节点之间的信道容量，start与设备之间的连线是设备请请求的带宽，DTC与end之间的连线是DTC的吞吐量
    # 给定start节点与设备之间的初始流量
    for i in set_IOT:
        # residual[0][i] = IoT_bws[i]
        residual[0][i] = 0
    # 给定物联网设备与无人机基站之间信道容量作为流量走向
    for i in set_IOT:
        for j in set_BS:
            residual[i][j + IoT_size] = IoT_BS_BWs[i, j]
    # 给基站input节点与基站output节点之间的流量赋初始值，其值为基站吞吐量
    for i in set_BS:
        residual[i + IoT_size][i + IoT_size + BS_size] = BS_THP[i]
        # residual[i + IoT_size][BS_size + IoT_size + 1] = DTC_BS_BWs[i]
    # 给基站output节点与DTC节点赋值，其值为信道容量
    for i in set_BS:
        residual[i + IoT_size + BS_size][2 * BS_size + IoT_size + 1] = DTC_BS_BWs[i]
    # DTC的input与output节点之间赋初始值，其值为DTC的吞吐量
    # residual[2 * BS_size + IoT_size + 1][2 * BS_size + IoT_size + 1 + 1] = DTC_THP
    residual[m - 3][m - 2] = DTC_THP
    residual[m - 2][m - 1] = float('inf')
    # Involvement = [0 for i in range(m)]
    # tele_bs.clear()
    sum_flow = [0 for i in range(m)]


# print(THP)
# print(residual)

# 计算每个节点的入度
# Involvement = {}
# for j in range(m):
#     sum_involvement = 0
#     for i in range(m):
#         if residual[i][j] > 0:
#             sum_involvement += 1
#     Involvement[j] = sum_involvement


# print(Involvement)
def match(node):
    global DTC_THP, residual, IoT_bws, DTC_BS_BWs, sum_flow, Involvement, tele_bs
    # print(node)
    tele_bs.clear()
    Involvement = [0 for i in range(m)]
    # 计算每个节点的入度
    for j in range(m):
        sum_involvement = 0
        for i in range(m):
            if residual[i][j] > 0:
                sum_involvement += 1
        Involvement[j] = sum_involvement
    # print(Involvement)
    # 先找到与该节点通信的基站
    for i in range(m):
        if residual[node][i] > 0:
            tele_bs.add(i)
    # print(tele_bs)
    min_bs = -1
    min_num = float('inf')
    for i in tele_bs:
        # print(Involvement[i])
        if Involvement[i] <= min_num:
            min_num = Involvement[i]
            min_bs = i
    # 基站min_bs接受的流量和
    sum_flow[min_bs] += IoT_bws[node]
    # DTC接受的流量和
    sum_flow[m - 2] += IoT_bws[node]
    # 设备请求的带宽大于设备与基站之间的信道容量时退出
    if IoT_bws[node]>residual[node][min_bs]:
        sum_flow[min_bs] -= IoT_bws[node]
        sum_flow[m - 2] -= IoT_bws[node]
        return -1
    # 设备请求的带宽大于基站的吞吐量时退出
    if IoT_bws[node]>residual[min_bs][min_bs+BS_size]:
        sum_flow[min_bs] -= IoT_bws[node]
        sum_flow[m - 2] -= IoT_bws[node]
        return -1
    # 基站接受的流量总和大于基站到DTC之间的信道容量时退出
    if sum_flow[min_bs]>residual[min_bs+BS_size][m-3]:
        sum_flow[min_bs] -= IoT_bws[node]
        sum_flow[m - 2] -= IoT_bws[node]
        return -1
    # DTC接受的流量总和大于DTC的吞吐量时退出
    if sum_flow[m-3]>residual[m-3][m-2]:
        sum_flow[min_bs] -= IoT_bws[node]
        sum_flow[m - 2] -= IoT_bws[node]
        return -1

    # if IoT_bws[node] > residual[node][min_bs] or IoT_bws[node] > residual[min_bs][min_bs + BS_size] \
    #         or sum_flow[min_bs] > residual[min_bs + BS_size][min_bs + BS_size + 1] or residual[m - 3][m - 2] < sum_flow[
    #     m - 2]:
    #     sum_flow[min_bs] -= IoT_bws[node]
    #     sum_flow[m - 2] -= IoT_bws[node]
    #     return -1
    residual[min_bs][min_bs + BS_size] -= IoT_bws[node]
    # DTC_THP -= IoT_bws[max_iot]
    # 返回基站
    return min_bs


# 定义胜者集合,这个是判断元素是否成为胜者
winner_set = set()
# 定义胜者列表，用来顺序加入胜者集合的元素
winner_list = []
# DTC剩余资源不能满足的集合
resource_no_satisfy = set()
# 网络流不存在的集合
network_stream_not_exit = set()
# 存放边际密度
v_to_b = {}

max_iot = 0


# 分配函数
def allocate():
    global social_welfare, last_winner, winner_set, winner_list, resource_no_satisfy, max_flow_graph, max_iot, network_stream_not_exit
    # print(DTC_THP)
    network()
    # print(DTC_THP)
    # max_flow_graph.clear()
    winner_set.clear()
    resource_no_satisfy.clear()
    network_stream_not_exit.clear()
    # 计算物联网设备的v/b
    for i in set_IOT:
        v_to_b[i] = IoT_value[i] / bids[i]
    while True:
        # v_to_b.clear()
        max_iot = 0
        max_increase = 0
        for key, value in v_to_b.items():
            if value > max_increase:
                max_increase = value
                max_iot = key
        if len(winner_set) + len(resource_no_satisfy) + len(network_stream_not_exit) == IoT_size:
            break
        del v_to_b[max_iot]
        # print(v_to_b)
        # print(bids)
        total_cpu = 0
        total_mem = 0
        # print(winner_set)
        for i in winner_set:
            total_cpu += IoT_resource[i, 1]
            total_mem += IoT_resource[i, 2]
        total_cpu += IoT_resource[max_iot, 1]
        total_mem += IoT_resource[max_iot, 2]
        # 如果DTC的资源不能满足物联网设备的需求就退出循环
        if DTC_resource[1] < total_cpu or DTC_resource[2] < total_mem:
            # 将max_Iot纳入资源不能满足集合
            resource_no_satisfy.add(max_iot)
            continue
        # 将start与max_IoT之间的流量从0设置为请求带宽
        residual[0][max_iot] = IoT_bws[max_iot]
        # 判断网络流路径是否存在，如果不存在跳过
        result = match(max_iot)
        if -1 == result:
            network_stream_not_exit.add(max_iot)
            continue
        # 将增长最大的纳入胜者集合中
        winner_set.add(max_iot)
        winner_list.append(max_iot)
        # 消除物联网设备max-iot的连线
        for i in range(m):
            residual[max_iot][i] = 0

        # winner_list与resource_no_satisfy的并集，用来筛选物联网设备是否已全部验证
        verify_set = winner_set.union(resource_no_satisfy).union(network_stream_not_exit)
        # 终止条件 物联网设备已经都在胜者集合与资源不能满足的集合
        # print(len(verify_set))
        if IoT_size == len(verify_set):
            break
    # print("---", winner_set)


# 二分法计算支付价格
def price():
    global last_winner, winner_set, pay, bids
    lb = 0
    ub = 0
    temp_bid = 0
    # 遍历物联网设备，已计算支付价格
    for i in last_winner:
        # 如果物联网设备i不是胜者，就直接跳过这一个
        # if i not in last_winner:
        #     continue
        # print(last_winner)
        # 暂存用户的出价，以便于之后恢复原先的出价
        temp_bid = bids[i]
        # print(temp_bid)
        # 设置下界
        lb = bids[i]
        # 设置上界
        # while i in winner_set:
        bids[i] = 4 * bids[i]
        ub = bids[i]
            # allocate()
            # print(winner_set)
        while True:
            # print("lb",lb)
            # print("ub",ub)
            # 如果用户i在胜者集合中就改变出价试探
            if i in winner_set:
                # ub = 2 * bids[i]
                # bids[i] = ub
                # 设置下界
                lb = bids[i]
                # 更新出价
                bids[i] = (ub + lb) / 2
                # 二分法结束条件，将上界作为支付，出价也改回原来的出价
                if ub - lb <= 1e-6:
                    pay[i - 1] = bids[i]
                    bids[i] = temp_bid
                    allocate()
                    break
                # print(residual)
                allocate()
            elif i not in winner_set:
                # print(winner_set)
                ub = bids[i]
                bids[i] = (lb + ub) / 2.0
                # print(residual)
                allocate()


print("---------------------------------------------------")
start_time = time.perf_counter()
allocate()
last_winner = winner_set
# price()
end_time = time.perf_counter()
total_winner = 0
resource_utilization1 = 0.0
resource_utilization2 = 0.0
total_cpu = 0
total_mem = 0
for i in last_winner:
    social_welfare += IoT_value[i] - bids[i]
    total_winner += 1
    total_cpu += IoT_resource[i, 1]
    total_mem += IoT_resource[i, 2]
social_welfare -= cost_uav
resource_utilization1 = total_cpu / DTC_resource[1]
resource_utilization2 = total_mem / DTC_resource[2]
# for i in last_winner:
#     total_pay += pay[i - 1]
print("社会福利：", social_welfare)
print("算法运行时间：", (end_time - start_time))
print("胜者数量：", total_winner)
print("cpu资源利用率：", resource_utilization1)
print("mem资源利用率", resource_utilization1)
# print("支付总额：", total_pay)
# print(pay)
# print(IoT_value)
# print(bids)
