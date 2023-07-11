# 次模函数分配，二分法支付
import copy
import time
import math
from queue import Queue

# 定义一些用到的变量
start_time, end_time = None, None
# IoT_size, BS_size = 3, 2
# cost_uav = 2
# cost_uav_unit = 5
# # IoT_size, BS_size = 3, 2  # IoT,基站的数量
# DTC_resource = {1: 15, 2: 10}  # DTC的资源总量
# bids = {1: 10, 2: 12, 3: 15}  # IoT设备的出价
# IoT_bws = {1: 7, 2: 8, 3: 6}  # IoT设备请求的带宽
# IoT_resource = {(1, 1): 8, (1, 2): 5,
#                 (2, 1): 4, (2, 2): 6,
#                 (3, 1): 7, (3, 2): 5}  # IoT设备的资源请求
# IoT_value = {1: 15, 2: 16, 3: 15}  # IoT设备的图像数据价值
#
# BS_THP = {1: 10, 2: 12}  # 基站的吞吐量
# DTC_THP = 20  # DTC的吞吐量
# DTC_BS_BWs = {1: 12, 2: 13}  # DTC与基站之间的信道容量
# BS_CH = {1: 3, 2: 2}  # 基站信道数量
# IoT_BS_BWs = {(1, 1): 6, (1, 2): 4,
#               (2, 1): 5, (2, 2): 4,
#               (3, 1): 7, (3, 2): 0}  # 物联网设备与基站之间的信道容量
# cost_uav = 5  # 无人机基站的服务成本
IoT_size, BS_size = 0, 0
DTC_resource = {}
bids = {}
IoT_bws = {}
IoT_resource = {}
IoT_value = {}
BS_THP = {}
DTC_THP = 0
DTC_BS_BWs = {}
BS_CH = {}
IoT_BS_BWs = {}
cost_uav_unit = 5  # 无人机基站的服务成本
cost_uav = 0
with open("../Experiment_1/experiment_1_user.txt", 'r', encoding='utf8') as user_file:
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
with open("../Experiment_1/uav_data.txt", 'r', encoding="utf8") as uav_file:
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
# print(m)
# 残余图的剩余流量 初始化为0
residual = [[0.0 for i in range(m)] for j in range(m)]
# 最大网络流图，初始化为0
max_flow_graph = [[0.0 for i in range(m)] for j in range(m)]
# 记录增广路径前进路程上记录的最小流量
flow = [0.0 for i in range(m)]
# 记录增广路径每个节点的前驱
pre = [float('inf') for i in range(m)]
# 队列，用于BFS的寻找增广路径
que = Queue()


def network():
    global max_flow_graph, residual, flow, pre, social_welfare, DTC_resource, IoT_size, BS_size, bids, IoT_bws, IoT_resource, IoT_value, BS_THP, DTC_THP, DTC_BS_BWs, BS_CH, IoT_BS_BWs, cost_uav

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


# print(residual)


def BFS(source, sink):
    # que.empty()  # 清空队列 这样清空队列是不对的，empty（）只是返回TRUE 或者 false
    while not que.empty():
        que.get()
    # print("source:", source)
    for i in range(m):
        pre[i] = float('inf')

    flow[source] = float('inf')  # 这里要是不改，那么找到的路径的流量永远是0
    # 不用将flow的其他清零
    que.put(source)
    while not que.empty():
        index = que.get()
        if index == sink:
            break
        for i in range(m):
            if (i != source) & (residual[index][i] > 0) & (pre[i] == float('inf')):
                # if (i != source) & (residual[index][i] > 0) & (pre[i] == float('inf')) & (i > index):
                # i!=source，从source到source不用分析了
                # residual[index][i]>0，边上有流量可以走
                # pre[i]==float('inf')，代表BFS还没有延伸到这个点上
                pre[i] = index
                # print(index)
                flow[i] = min(flow[index], residual[index][i])
                que.put(i)
    if pre[sink] == float('inf'):
        # 汇点的前驱还是初始值，说明已无增广路径
        return -1
    else:
        return flow[sink]


def max_flow(source, sink):
    sumflow = 0  # 记录最大流，一直累加
    augmentflow = 0  # 当前寻找到的增广路径的最小通过流量
    while True:
        augmentflow = BFS(source, sink)
        if augmentflow == -1:
            break  # 返回-1说明已没有增广路径
        k = sink
        while k != source:  # k回溯到起点，停止
            prev = pre[k]  # 走的方向是从prev到k
            max_flow_graph[prev][k] += augmentflow
            residual[prev][k] -= augmentflow  # 前进方向消耗掉了
            residual[k][prev] += augmentflow  # 反向边
            k = prev
        sumflow += augmentflow
    return sumflow


# 定义胜者集合,这个是判断元素是否成为胜者
winner_set = set()
# 定义胜者列表，用来顺序加入胜者集合的元素
winner_list = []
# DTC剩余资源不能满足的集合
resource_no_satisfy = set()
# 网络流不存在的集合
network_stream_not_exit = set()
# 数据价值与出价之差
v_d_b = {}


# 分配函数
def allocate():
    global social_welfare, last_winner, winner_set, winner_list, resource_no_satisfy, max_flow_graph, network_stream_not_exit
    network()
    # max_flow_graph.clear()
    winner_set.clear()
    resource_no_satisfy.clear()
    network_stream_not_exit.clear()
    # 设备加入胜者集合的顺序
    # order = 1
    while True:
        # margin_density.clear()
        network()
        v_d_b.clear()
        tmp_social_welfare = 0.0
        # if 0 != len(winner_set):
        for i in winner_set:
            tmp_social_welfare += IoT_value[i] - bids[i]
        tmp_social_welfare -= cost_uav
        print(winner_set)
        for i in set_IOT:
            # 若是物联网设备i已经进入胜者结合，则不计算他的边际密度
            if i in winner_set or i in resource_no_satisfy or i in network_stream_not_exit:
                continue
            else:
                v_d_b[i] = IoT_value[i] - bids[i]
        if 0 == len(v_d_b):
            break
        max_iot = -1
        max_increase = -1
        # 寻找出使社会福利增长最大的物联网设备
        for key, value in v_d_b.items():
            if value > max_increase:
                max_iot = key
                max_increase = value
        tmp_social_welfare += max_increase
        if tmp_social_welfare < 0 or max_increase < 0:
            break
        total_cpu = 0
        total_mem = 0
        total_bw = 0
        for i in winner_set:
            total_cpu += IoT_resource[i, 1]
            total_mem += IoT_resource[i, 2]
            total_bw += IoT_bws[i]
        # print(max_iot)
        total_cpu += IoT_resource[max_iot, 1]
        total_mem += IoT_resource[max_iot, 2]
        total_bw += IoT_bws[max_iot]
        # 如果DTC的资源不能满足物联网设备的需求就退出循环
        if DTC_resource[1] < total_cpu or DTC_resource[2] < total_mem:
            # 将max_Iot纳入资源不能满足集合
            resource_no_satisfy.add(max_iot)
            # network()
            continue
        # 将start与max_IoT之间的流量从0设置为请求带宽
        residual[0][max_iot] = IoT_bws[max_iot]
        # THP[0] += IoT_bws[max_iot]
        # print("bw",IoT_bws[max_iot])
        for i in winner_set:
            residual[0][i] = IoT_bws[i]
            # THP[0] += IoT_bws[i]
        # print(winner_set)
        # print(max_iot)
        # print("-----", residual)
        # 网络流算法分流
        # 判断网络流路径是否存在，如果不存在跳过
        result = max_flow(0, m - 1)
        if 0 == result or total_bw != result:
            # residual[0][max_iot] = 0
            # THP[0] -= IoT_bws[max_iot]
            network_stream_not_exit.add(max_iot)
            # print('dddd', max_flow_graph)
            network()
            continue
        winner_set.add(max_iot)
        winner_list.append(max_iot)
        # winner_list与resource_no_satisfy的并集，用来筛选物联网设备是否已全部验证
        verify_set = winner_set.union(resource_no_satisfy).union(network_stream_not_exit)
        # 终止条件 物联网设备已经都在胜者集合与资源不能满足的集合
        # print(len(verify_set))
        if IoT_size == len(verify_set):
            break
        # 刷新网络
        # network()


# lb, ub = 0.0, 0.0


# 二分法计算支付价格
def price():
    lb = 0
    ub = 0
    # 遍历物联网设备，已计算支付价格
    for i in set_IOT:
        # 如果物联网设备i不是胜者，就直接跳过这一个
        if i not in last_winner:
            continue
        # 暂存用户的出价，以便于之后恢复原先的出价
        temp_bid = bids[i]
        # 设置下界
        lb = bids[i]
        # 设置上界
        while i in winner_set:
            ub = 2 * bids[i]
            bids[i] = ub
            allocate()
        while True:
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
print("last_winner：", last_winner)
end_time = time.perf_counter()
# 计算社会福利
# social_welfare = 0
for i in last_winner:
    social_welfare += IoT_value[i] - bids[i]
social_welfare -= cost_uav
print("社会福利：", social_welfare)
# print("price:", pay)
print("算法执行时间：", (end_time - start_time))
total_number = 0
final_total_cpu = 0
final_total_mem = 0
for i in last_winner:
    # total_pay += pay[i]
    total_number += 1
    final_total_cpu += IoT_resource[i , 1]
    final_total_mem += IoT_resource[i , 2]
# print("支付总额：", total_pay)
print("胜者数量：", total_number)
resource_utilization1 = final_total_cpu / DTC_resource[1]
resource_utilization2 = final_total_mem / DTC_resource[2]
print("cpu资源利用率:", resource_utilization1)
print("mem资源利用率:", resource_utilization2)
