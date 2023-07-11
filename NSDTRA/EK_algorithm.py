# -*- encoding:gbk -*-
from queue import Queue

# n #�ߵĸ���
m = 6  # ��ĸ���

residual = [[0 for i in range(m)] for j in range(m)]
# ����ͼ��ʣ������
maxflowgraph = [[0 for i in range(m)] for j in range(m)]
# ��¼�����ͼ����ʼ��Ϊ0
flow = [0 for i in range(m)]
# ��¼����·��ǰ�����̼�¼����С����
pre = [float('inf') for i in range(m)]
# ��¼����·��ÿ���ڵ��ǰ��
q = Queue()
# ���У�����BFS��Ѱ������·��

# ���ó�ʼͼ����������
residual[0][1] = 3
residual[0][2] = 2
residual[1][2] = 0
residual[1][3] = 0
residual[1][4] = 4
residual[2][4] = 2
residual[3][5] = 2
residual[4][5] = 3


def BFS(source, sink):
    q.empty()  # ��ն���

    for i in range(m):
        pre[i] = float('inf')

    flow[source] = float('inf')  # ����Ҫ�ǲ��ģ���ô�ҵ���·����������Զ��0
    # ���ý�flow����������
    q.put(source)
    while (not q.empty()):
        index = q.get()
        if (index == sink):
            break
        for i in range(m):
            if ((i != source) & (residual[index][i] > 0) & (pre[i] == float('inf'))):
                # i!=source����source��source���÷�����
                # residual[index][i]>0������������������
                # pre[i]==float('inf')������BFS��û�����쵽�������
                pre[i] = index
                flow[i] = min(flow[index], residual[index][i])
                q.put(i)
    if (pre[sink] == float('inf')):
        # ����ǰ�����ǳ�ʼֵ��˵����������·��
        return -1
    else:
        return flow[sink]


def maxflow(source, sink):
    sumflow = 0  # ��¼�������һֱ�ۼ�
    augmentflow = 0  # ��ǰѰ�ҵ�������·������Сͨ������
    while (True):
        augmentflow = BFS(source, sink)
        if (augmentflow == -1):
            break  # ����-1˵����û������·��
        k = sink
        while (k != source):  # k���ݵ���㣬ֹͣ
            prev = pre[k]  # �ߵķ����Ǵ�prev��k
            maxflowgraph[prev][k] += augmentflow
            residual[prev][k] -= augmentflow  # ǰ���������ĵ���
            residual[k][prev] += augmentflow  # �����
            k = prev
        sumflow += augmentflow
    return sumflow


result = maxflow(0, m - 1)
print(result)
print(maxflowgraph)  # �����ͼ
