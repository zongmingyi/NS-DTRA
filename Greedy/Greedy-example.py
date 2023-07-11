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
bids = {1: 17, 2: 12, 3: 15}  # IoT设备的出价
# IoT_bws = {1: 15, 2: 19.5, 3: 5}  # IoT设备请求的带宽
IoT_bws = {1: 11, 2: 11, 3: 5}
# IoT_resource = {(1, 1): 12, (1, 2): 15,
#                 (2, 1): 12, (2, 2): 15,
#                 (3, 1): 18, (3, 2): 25}  # IoT设备的资源请求
IoT_resource = {(1, 1): 12, (1, 2): 15,
                (2, 1): 12, (2, 2): 15,
                (3, 1): 18, (3, 2): 25}
IoT_value = {1: 30, 2: 30, 3: 28}  # IoT设备的图像数据价值
# IoT_value = {}
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
# 定义模型中涉及到的节点的数量:物联网设备数量+无人机基站数量+DTC+开始节点+结束节点
m = IoT_size + BS_size + 1 + 1 + 1

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
    DTC_resource = {1: 40, 2: 45}  # DTC的资源总量
    # bids = {1: 10, 2: 12, 3: 15}  # IoT设备的出价

    BS_THP = {1: 20, 2: 20}  # 基站的吞吐量
    DTC_THP = 45  # DTC的吞吐量
    DTC_BS_BWs = {1: 30, 2: 23}  # DTC与基站之间的信道容量
    BS_CH = {1: 3, 2: 2}  # 基站信道数量
    IoT_BS_BWs = {(1, 1): 10, (1, 2): 10,
                  (2, 1): 15.5, (2, 2): 12,
                  (3, 1): 8, (3, 2): 0}  # 物联网设备与基站之间的信道容量
    cost_uav = 10  # 无人机基站的服务成本
    # 最大网络流图，初始化为0
    max_flow_graph = [[0.0 for i in range(m)] for j in range(m)]
    # 残余图的剩余流量 初始化为0
    residual = [[0.0 for i in range(m)] for j in range(m)]
    # 记录增广路径前进路程上记录的最小流量
    flow = [0.0 for i in range(m)]
    # 记录增广路径每个节点的前驱
    pre = [float('inf') for i in range(m)]
    # 记录每个节点的吞吐量
    THP = [0.0 for i in range(m)]
    # 读取初始图的流量走向，在我们设计的模型中是各节点之间的信道容量，start与设备之间的连线是设备请请求的带宽，DTC与end之间的连线是DTC的吞吐量
    # 给定start节点与设备之间的初始流量
    for i in set_IOT:
        # residual[0][i] = IoT_bws[i]
        residual[0][i] = 0
    #  给定物联网设备与无人机基站之间信道容量作为流量走向
    for i in set_IOT:
        for j in set_BS:
            residual[i][j + IoT_size] = IoT_BS_BWs[i, j]
    # 给基站与DTC之间的流量赋初始值，其值为信道容量
    for i in set_BS:
        residual[i + IoT_size][BS_size + IoT_size + 1] = DTC_BS_BWs[i]
    # DTC与end节点之间赋初始值
    residual[BS_size + IoT_size + 1][BS_size + IoT_size + 1 + 1] = DTC_THP
    # 为节点的吞吐量赋初值
    for i in range(1, m):
        if i <= IoT_size:
            THP[i] = IoT_bws[i]
        if IoT_size < i <= IoT_size + BS_size:
            THP[i] = BS_THP[i - IoT_size]
        if i > BS_size + IoT_size:
            THP[i] = DTC_THP


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

Involvement = {}

tele_bs = set()

sum_flow = [0 for i in range(m)]


# print(Involvement)
def match(node):
    global DTC_THP, residual, IoT_bws, DTC_BS_BWs, THP
    # 计算每个节点的入度
    for j in range(m):
        sum_involvement = 0
        for i in range(m):
            if residual[i][j] > 0:
                sum_involvement += 1
        Involvement[j] = sum_involvement
    # 先找到与该节点通信的基站
    for i in range(m):
        if residual[node][i] > 0:
            tele_bs.add(i)
    min_bs = -1
    min_num = float('inf')
    for i in tele_bs:
        if Involvement[i] <= min_num:
            min_num = Involvement[i]
            min_bs = i
    # 基站min_bs接受的流量和
    sum_flow[min_bs] += IoT_bws[node]
    # DTC接受的流量和
    sum_flow[m - 2] += IoT_bws[node]
    # print(sum_flow[m-2])
    if IoT_bws[max_iot] > residual[max_iot][min_bs] or IoT_bws[max_iot] > THP[min_bs] or sum_flow[min_bs] > \
            DTC_BS_BWs[min_bs - IoT_size] or DTC_THP<sum_flow[m-2]:
        sum_flow[min_bs] -= IoT_bws[node]
        sum_flow[m - 2] -= IoT_bws[node]
        return -1
    THP[min_bs] -= IoT_bws[max_iot]
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
    # 设备加入胜者集合的顺序
    order = 1
    for i in set_IOT:
        # 若是物联网设备i已经进入胜者结合，则不计算他的
        v_to_b[i] = IoT_value[i] / bids[i]
    while True:
        # v_to_b.clear()
        # 对剩余物联网设备计算v/b
        # print(winner_set)
        # print(resource_no_satisfy)
        # print(winner_list)

        # print(margin_density)
        # print(v_to_b)
        max_iot = 0
        max_increase = 0
        for key, value in v_to_b.items():
            if value > max_increase:
                max_increase = value
                max_iot = key
        if 0 == len(v_to_b):
            break
        del v_to_b[max_iot]
        # 寻找出使社会福利增长最大的物联网设备
        # for key, value in margin_density.items():
        #     if value - bids[key] - cost_uav > max_increase:
        #         max_iot = key
        #         max_increase = value - bids[key] - cost_uav
        # print(margin_density)
        # for key, value in margin_density.items():
        #     if value > max_increase:
        #         max_iot = key
        #         max_increase = value
        # 终止条件 当增长小于等于0结束循环
        # if max_increase <= 0:
        #     break
        # print(max_iot)
        # if IoT_value[max_iot] - bids[max_iot] - cost_uav <= 0:
        #     break
        # 如果DTC的资源不能满足物联网设备的需求就退出循环
        if DTC_resource[1] < IoT_resource[max_iot, 1] or DTC_resource[2] < IoT_resource[max_iot, 2]:
            # 将max_Iot纳入资源不能满足集合
            resource_no_satisfy.add(max_iot)
            continue
        # 将start与max_IoT之间的流量从0设置为请求带宽
        residual[0][max_iot] = IoT_bws[max_iot]
        THP[0] = IoT_bws[max_iot]
        # print(residual)
        # print(IoT_bws[max_iot])
        # 网络流算法分流
        # 判断网络流路径是否存在，如果不存在跳过
        result = match(max_iot)
        if -1 == result:
            network_stream_not_exit.add(max_iot)
            continue
        # 消除物联网设备max-iot的连线
        for i in range(m):
            residual[max_iot][i] = 0
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
        winner_set.add(max_iot)
        winner_list.append(max_iot)

        # 因为添加进胜者集合中一个元素，所以顺序加1
        order = order + 1
        # 更新DTC资源量
        DTC_resource[1] -= IoT_resource[max_iot, 1]
        DTC_resource[2] -= IoT_resource[max_iot, 2]
        # print(residual)
        # print(max_flow_graph)
        # winner_list与resource_no_satisfy的并集，用来筛选物联网设备是否已全部验证
        verify_set = winner_set.union(resource_no_satisfy).union(network_stream_not_exit)
        # 终止条件 物联网设备已经都在胜者集合与资源不能满足的集合
        # print(len(verify_set))
        if IoT_size == len(verify_set):
            break
    # print("---", winner_set)
    # 计算社会福利
    for i in winner_list:
        social_welfare += IoT_value[i] - bids[i]
    social_welfare -= cost_uav
    # 拷贝胜者集合
    # last_winner = winner_set.copy()


print("---------------------------------------------------")
allocate()
print("社会福利：", social_welfare)
print(max_flow_graph)
print(winner_set)
# print(sum_flow)
