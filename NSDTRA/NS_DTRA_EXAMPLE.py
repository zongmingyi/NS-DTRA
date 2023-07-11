# 次模函数分配，二分法支付
import copy
import time
import math
from queue import Queue

# 定义一些用到的变量
start_time, end_time = None, None
# 写死的例子
IoT_size, BS_size = 3, 2  # IoT,基站的数量
# DTC_resource = {1: 40, 2: 45}  # DTC的资源总量
DTC_resource = {}
bids = {1: 4, 2: 6, 3: 4}  # IoT设备的出价
# IoT_bws = {1: 15, 2: 19.5, 3: 5}  # IoT设备请求的带宽
IoT_bws = {}
# IoT_resource = {(1, 1): 12, (1, 2): 15,
#                 (2, 1): 12, (2, 2): 15,
#                 (3, 1): 18, (3, 2): 25}  # IoT设备的资源请求
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
# 记录每个节点的吞吐量
THP = []


def network():
    global max_flow_graph, residual, flow, THP, pre, social_welfare, DTC_resource, IoT_size, BS_size, bids, IoT_bws, IoT_resource, IoT_value, BS_THP, DTC_THP, DTC_BS_BWs, BS_CH, IoT_BS_BWs, cost_uav
    # IoT_size, BS_size = 3, 2  # IoT,基站的数量
    DTC_resource = {1: 15, 2: 10}  # DTC的资源总量
    # bids = {1: 10, 2: 12, 3: 15}  # IoT设备的出价
    IoT_bws = {1: 7, 2: 8, 3: 6}  # IoT设备请求的带宽
    IoT_resource = {(1, 1): 8, (1, 2): 5,
                    (2, 1): 4, (2, 2): 6,
                    (3, 1): 7, (3, 2): 5}  # IoT设备的资源请求
    IoT_value = {1: 15, 2: 16, 3: 13}  # IoT设备的图像数据价值

    BS_THP = {1: 10, 2: 12}  # 基站的吞吐量
    DTC_THP = 20  # DTC的吞吐量
    DTC_BS_BWs = {1: 12, 2: 13}  # DTC与基站之间的信道容量
    BS_CH = {1: 3, 2: 2}  # 基站信道数量
    IoT_BS_BWs = {(1, 1): 6, (1, 2): 4,
                  (2, 1): 5, (2, 2): 4,
                  (3, 1): 7, (3, 2): 0}  # 物联网设备与基站之间的信道容量
    cost_uav = 5  # 无人机基站的服务成本
    # 最大网络流图，初始化为0
    max_flow_graph = [[0.0 for i in range(m)] for j in range(m)]
    # 残余图的剩余流量 初始化为0
    residual = [[0.0 for i in range(m)] for j in range(m)]
    # 记录增广路径前进路程上记录的最小流量
    flow = [0.0 for i in range(m)]
    # 记录增广路径每个节点的前驱
    pre = [float('inf') for i in range(m)]
    # 记录每个节点的吞吐量
    # THP = [0.0 for i in range(m)]
    # THP = [0.0]
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
    residual[2 * BS_size + IoT_size + 1][2 * BS_size + IoT_size + 1 + 1] = DTC_THP
    residual[m - 2][m - 1] = float('inf')
    # # 为节点的吞吐量赋初值
    # for i in range(1, m):
    #     if i <= IoT_size:
    #         THP[i] = IoT_bws[i]
    #     if IoT_size < i <= IoT_size + BS_size:
    #         THP[i] = BS_THP[i - IoT_size]
    #     if i > BS_size + IoT_size:
    #         THP[i] = DTC_THP
    # print("THP",THP)


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


# 广度优先搜索
def bfs(source, sink):
    # 清空队列
    que.empty()

    for i in range(m):
        pre[i] = float('inf')

    flow[source] = float('inf')
    que.put(source)
    while not que.empty():
        index = que.get()
        if index == sink:
            break
        for i in range(m):
            if i != source and residual[index][i] > 0 and pre[i] == float('inf'):
                # i!=source，从source到source不用分析了
                # residual[index][i]>0，边上有流量可以走
                # pre[i]==float('inf')，代表BFS还没有延伸到这个点上
                pre[i] = index
                # flow[i] = min(flow[index], residual[index][i])
                flow[i] = min(flow[index], residual[index][i])
                que.put(i)
    if pre[sink] == float('inf'):
        # 汇点的前置还是初始值，说明已无增广路径
        return -1
    else:
        return flow[sink]


# 最大流函数
def max_flow(source, sink):
    # network()
    # 记录最大流，一直累加
    sum_flow = 0
    # 当前寻找到的增广路径的最小通过流量
    augment_flow = 0
    while True:
        augment_flow = bfs(source, sink)
        # print(augment_flow)
        if augment_flow == -1:
            # 返回-1说明已无增广路径
            break
        k = sink
        while k != source:  # k回溯到起点，停止
            prev = pre[k]  # 走的方向是从prev到k
            # print("----", prev)
            max_flow_graph[prev][k] += augment_flow
            residual[prev][k] -= augment_flow  # 前进方向消耗掉
            residual[k][prev] += augment_flow  # 反向边
            k = prev
        sum_flow += augment_flow
        # print("-------", pre)
    # if max_flow_graph[0][max_iot] != IoT_bws[max_iot]:
    #     return 0
    # if sum_flow != IoT_bws[max_iot]:
    #     return 0
    # print("---", sum_flow)
    # print("-------", IoT_bws[max_iot])
    # 保证物联网设备释放的网络流总和等于其请求带宽
    # if sum_flow != IoT_bws[max_iot]:
    #     return 0
    return sum_flow


# 定义胜者集合,这个是判断元素是否成为胜者
winner_set = set()
# 定义胜者列表，用来顺序加入胜者集合的元素
winner_list = []
# DTC剩余资源不能满足的集合
resource_no_satisfy = set()
# 网络流不存在的集合
network_stream_not_exit = set()
# 存放边际密度
# margin_density = {}
# 数据价值与出价之差
v_d_b = {}

max_iot = 0


# 分配函数
def allocate():
    global social_welfare, last_winner, winner_set, winner_list, resource_no_satisfy, max_flow_graph, max_iot, network_stream_not_exit
    # network()
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
        # max_iot = -1
        # 对剩余物联网设备计算边际密度
        # print(winner_set)
        # print(resource_no_satisfy)
        # print(winner_list)
        tmp_social_welfare = 0.0
        # if 0 != len(winner_set):
        for i in winner_set:
            tmp_social_welfare += IoT_value[i] - bids[i]
        tmp_social_welfare -= cost_uav
        for i in set_IOT:
            # 若是物联网设备i已经进入胜者结合，则不计算他的边际密度
            if i in winner_set or i in resource_no_satisfy or i in network_stream_not_exit:
                continue
            else:
                v_d_b[i] = IoT_value[i] - bids[i]

        # 计算物联网设备的边际密度
        # margin_density[i] = IoT_value[i] / math.log((1 + order), math.e)
        # order = order + 1
        # print(margin_density)
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
        # print("max_iot",max_iot)
        # print("max_increase",max_increase)
        # print("tmp_soc",tmp_social_welfare)
        if tmp_social_welfare < 0 or max_increase < 0:
            break
        # print("max_iot",max_iot)
        # print("max_increase",max_increase)
        # for key, value in margin_density.items():
        #     if value > max_increase:
        #         max_iot = key
        #         max_increase = value
        # 终止条件 当增长小于等于0结束循环
        # if max_increase <= 0:
        #     break
        # print(max_iot)
        # if max_increase - bids[max_iot] <= 0:
        #     break
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
        # print("-----", residual)
        # 将start与胜者集合中的设备之间的流量设置
        # print(residual)
        # print(IoT_bws[max_iot])
        # 网络流算法分流
        # 判断网络流路径是否存在，如果不存在跳过
        # print("residual", residual)
        result = max_flow(0, m - 1)
        # print(total_bw)
        # print(result)
        if 0 == result or total_bw != result:
            # residual[0][max_iot] = 0
            # THP[0] -= IoT_bws[max_iot]
            network_stream_not_exit.add(max_iot)
            # print('dddd', max_flow_graph)
            network()
            continue
        # print("max_iot", max_iot)
        # print("max_increase", max_increase)
        print('----', max_flow_graph)
        # if max_flow_graph[0][max_iot]!=IoT_bws[max_iot]:
        #     continue
        # print(max_flow_graph[0][max_iot])
        # print(IoT_bws[max_iot])
        # print("--", max_flow(0, m - 1))
        # print(flow[max_iot])
        # print(IoT_bws[max_iot])
        # if flow[max_iot]!=IoT_bws[max_iot]:
        #     continue
        # 分流之后将将start与max_IoT之间的流量设置为0，以便对的胜者进行分流
        # residual[0][max_iot] = 0
        # THP[0] = 0
        # 将增长最大的纳入胜者集合中
        # print(winner_set)
        winner_set.add(max_iot)
        winner_list.append(max_iot)
        # 因为添加进胜者集合中一个元素，所以顺序加1
        # order = order + 1
        # 更新DTC资源量
        # DTC_resource[1] -= IoT_resource[max_iot, 1]
        # DTC_resource[2] -= IoT_resource[max_iot, 2]
        # print(residual)
        # print(max_flow_graph)
        # winner_list与resource_no_satisfy的并集，用来筛选物联网设备是否已全部验证
        verify_set = winner_set.union(resource_no_satisfy).union(network_stream_not_exit)
        # 终止条件 物联网设备已经都在胜者集合与资源不能满足的集合
        # print(len(verify_set))
        if IoT_size == len(verify_set):
            break
        # 刷新网络
        # network()
    # print("---", winner_set)
    # 计算社会福利
    for i in winner_list:
        social_welfare += IoT_value[i] - bids[i]
    social_welfare -= cost_uav
    # 拷贝胜者集合
    # last_winner = winner_set.copy()


# 计算社会福利
# def social_wel():
#     global social_welfare
#     for i in winner_list:
#         social_welfare += IoT_value[i] - bids[i]
#     social_welfare -= cost_uav

lb, ub = 0.0, 0.0


# 二分法计算支付价格
def price():
    global lb, ub
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
allocate()
last_winner = winner_set.copy()
print(last_winner)
# print(last_winner)
print("社会福利：", social_welfare)

price()
print("price:", pay)
print(bids)
print(IoT_value)