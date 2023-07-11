# -*- encoding:gbk -*-
from queue import Queue

# n #边的个数
m = 6  # 点的个数

residual = [[0 for i in range(m)] for j in range(m)]
# 残余图的剩余流量
maxflowgraph = [[0 for i in range(m)] for j in range(m)]
# 记录最大流图，初始都为0
flow = [0 for i in range(m)]
# 记录增广路径前进过程记录的最小流量
pre = [float('inf') for i in range(m)]
# 记录增广路径每个节点的前驱
q = Queue()
# 队列，用于BFS地寻找增广路径

# 设置初始图的流量走向
residual[0][1] = 3
residual[0][2] = 2
residual[1][2] = 0
residual[1][3] = 0
residual[1][4] = 4
residual[2][4] = 2
residual[3][5] = 2
residual[4][5] = 3


def BFS(source, sink):
    q.empty()  # 清空队列

    for i in range(m):
        pre[i] = float('inf')

    flow[source] = float('inf')  # 这里要是不改，那么找到的路径的流量永远是0
    # 不用将flow的其他清零
    q.put(source)
    while (not q.empty()):
        index = q.get()
        if (index == sink):
            break
        for i in range(m):
            if ((i != source) & (residual[index][i] > 0) & (pre[i] == float('inf'))):
                # i!=source，从source到source不用分析了
                # residual[index][i]>0，边上有流量可以走
                # pre[i]==float('inf')，代表BFS还没有延伸到这个点上
                pre[i] = index
                flow[i] = min(flow[index], residual[index][i])
                q.put(i)
    if (pre[sink] == float('inf')):
        # 汇点的前驱还是初始值，说明已无增广路径
        return -1
    else:
        return flow[sink]


def maxflow(source, sink):
    sumflow = 0  # 记录最大流，一直累加
    augmentflow = 0  # 当前寻找到的增广路径的最小通过流量
    while (True):
        augmentflow = BFS(source, sink)
        if (augmentflow == -1):
            break  # 返回-1说明已没有增广路径
        k = sink
        while (k != source):  # k回溯到起点，停止
            prev = pre[k]  # 走的方向是从prev到k
            maxflowgraph[prev][k] += augmentflow
            residual[prev][k] -= augmentflow  # 前进方向消耗掉了
            residual[k][prev] += augmentflow  # 反向边
            k = prev
        sumflow += augmentflow
    return sumflow


result = maxflow(0, m - 1)
print(result)
print(maxflowgraph)  # 最大流图
