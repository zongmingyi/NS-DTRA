import docplex.mp.model as cpx
# import cplex as cpx
import time
import copy
import math
import pandas as pd
import numpy as np

# 定义一些用到的变量
start_time, end_time = None, None
# 写死的例子
# IoT_size, BS_size = 3, 2  # IoT,基站的数量
# DTC_resource = {1: 40, 2: 45}  # DTC的资源总量
# bids = {1: 10, 2: 12, 3: 15}  # IoT设备的出价
# IoT_bws = {1: 15, 2: 19.5, 3: 5}  # IoT设备请求的带宽
# IoT_resource = {(1, 1): 12, (1, 2): 15,
#                 (2, 1): 12, (2, 2): 15,
#                 (3, 1): 18, (3, 2): 25}  # IoT设备的资源请求
# IoT_value = {1: 30, 2: 30, 3: 28}  # IoT设备的图像数据价值
#
# BS_THP = {1: 30, 2: 20}  # 基站的吞吐量
# DTC_THP = 45  # DTC的吞吐量
# DTC_BS_BWs = {1: 30, 2: 23}  # DTC与基站之间的信道容量
# BS_CH = {1: 3, 2: 3}  # 基站信道数量
# IoT_BS_BWs = {(1, 1): 10, (1, 2): 10,
#               (2, 1): 15.5, (2, 2): 10,
#               (3, 1): 8, (3, 2): 15}  # 物联网设备与基站之间的信道容量
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
with open("../Experiment_5/experiment_5_user_10.txt", 'r', encoding='utf8') as user_file:
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
with open("../Experiment_5/uav_data_10.txt", 'r', encoding="utf8") as uav_file:
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
# 用户下标集合，基站下标集合，资源下标集合
set_IOT, set_BS, set_resource = range(1, IoT_size + 1), range(1, BS_size + 1), range(1, 3)

for j in range(BS_size):
    channel = 0
    for i in range(IoT_size):
        if IoT_BS_BWs[i + 1, j + 1] > 0:
            channel += 1
    BS_CH[j + 1] = channel


# 混合整数线性规划的分配函数
def opt_alloc():
    # 创建MIP模型
    opt_model = cpx.Model(name="MIP Model")

    # 定义IoT设备决策变量
    x_vars = {i: opt_model.binary_var(name="x_{0}".format(i)) for i in set_IOT}

    # 在定义的时候约束了网络流决策变量的取值范围
    # 定义物联网设备与基站之间网络流决策变量
    f_IOT_var = {(u, v): opt_model.continuous_var(lb=0, ub=IoT_BS_BWs[u, v], name="f_IOT_var_{0}_{1}".format(u, v)) for
                 u in set_IOT for v in set_BS}

    # 定义基站与DTC之间的网络流决策变量
    f_BS_var = {u: opt_model.continuous_var(lb=0, ub=DTC_BS_BWs[u], name="f_BS_VAR_{0}".format(u)) for u in set_BS}

    # 添加约束条件
    # 物联网设备的请求资源总和要小于等于DTC拥有的资源总量
    constraint1 = {r: opt_model.add_constraint(
        ct=opt_model.sum(IoT_resource[i, r] * x_vars[i] for i in set_IOT) <= DTC_resource[r],
        ctname="constraint_a_{0}".format(r)) for r
        in set_resource
    }
    # 基站的吞吐量大于接受的网络流总和
    constraint2 = {v: opt_model.add_constraint(ct=opt_model.sum(f_IOT_var[u, v] for u in set_IOT) <= BS_THP[v],
                                               ctname="constraint_c_{0}".format(v)) for v in set_BS}
    # 胜者集合中的物联网设备的带宽需求小于等于云端的吞吐量
    constraint3 = {opt_model.add_constraint(ct=opt_model.sum(IoT_bws[i] * x_vars[i] for i in set_IOT) <= DTC_THP,
                                            ctname="constraint_d_{0}".format(1))}
    # 基站接受的网络流等于释放的网络流
    constraint4 = {v: opt_model.add_constraint(ct=opt_model.sum(f_IOT_var[u, v] for u in set_IOT) == f_BS_var[v]
                                               , ctname="constraint_e_{0}".format(v)) for v in set_BS}
    # 云端接受的网络流等于胜者设备的带宽
    constraint5 = {opt_model.add_constraint(
        ct=opt_model.sum(f_BS_var[u] for u in set_BS) == opt_model.sum(IoT_bws[i] * x_vars[i] for i in set_IOT),
        ctname="constraint_f")}
    # 对于物联网设备来说，分流的带宽要等于请求的带宽
    constraint6 = {
        i: opt_model.add_constraint(ct=opt_model.sum(f_IOT_var[i, v] for v in set_BS) == x_vars[i] * IoT_bws[i],
                                    ctname="constrain_g_{0}".format(i)) for i
        in set_IOT}
    # 基站接受的网络分流小于等于其信道数量
    # 指示函数决策变量，用来记录网络流决策变量中不为0的变量
    indicator_var = {(u, v): opt_model.binary_var(name="indicator_var_{0}_{1}".format(u, v)) for u in set_IOT for v in
                     set_BS}
    # 求指示函数的约束
    constraint7 = {(u, v): opt_model.add_indicator(indicator_var[u, v], f_IOT_var[u, v] == 0, 1)
                   for u in set_IOT for v in set_BS}
    # 判断基站接受的网络分流小于其信道数量
    constraint8 = {v: opt_model.add_constraint(ct=opt_model.sum(indicator_var[u, v] for u in set_IOT) <= BS_CH[v],
                                               ctname="constrain_h_{0}".format(v)) for v in set_BS}

    # 定义胜者集合
    # winner_set = []
    # for i in set_IOT:
    #     if 1 is x_vars[i]:
    #         winner_set.append(i)
    # 定义目标函数
    # objective = opt_model.sum(IoT_value[winner_set[i]] / math.log(1 + i, math.e) for i in winner_set) - opt_model.sum(
    #     x_vars[i] * bids[i] for i in set_IOT) - cost_uav
    objective = opt_model.sum(x_vars[i] * IoT_value[i] for i in set_IOT) - opt_model.sum(
        x_vars[i] * bids[i] for i in set_IOT) - cost_uav

    # 最大化目标
    opt_model.maximize(objective)
    # 求解模型
    opt_model.solve()

    # 获取求解的目标值
    val = opt_model.objective_value
    # print("objective", objective)
    # print("决策变量", x_vars)
    # 处理求解结果：将cplex求解的分配结果转换成list并返回
    opt_df = pd.DataFrame.from_dict(x_vars, orient="index", columns=["variable_object"])
    # print("--------", opt_df.index)
    opt_df.index = pd.Int64Index.tolist(opt_df.index)
    # print(opt_df)
    opt_df.reset_index(inplace=True)
    # print(opt_df)
    opt_df["solution_value"] = opt_df["variable_object"].apply(lambda item: item.solution_value)
    # print(opt_df)
    opt_df.drop(columns=["variable_object"], inplace=True)
    tmp_alloc = opt_df['solution_value'].tolist()

    # 将cplex的网络流结果转换成list并返回
    opt_f = pd.DataFrame.from_dict(f_IOT_var, orient="index", columns=["variable_object"])
    # print("--------------------",opt_f.index)
    opt_f.index = pd.MultiIndex.from_tuples(opt_f.index, names=["column_i", "column_j"])
    # print("**************",opt_f)
    opt_f.reset_index(inplace=True)
    # print("**************", opt_df)
    opt_f["solution_value"] = opt_f["variable_object"].apply(lambda item: item.solution_value)
    # print("**************", opt_df)
    opt_f.drop(columns=["variable_object"], inplace=True)
    t_alloc = opt_f['solution_value'].tolist()
    # 返回一个(N)和（N*M)的list,即分配结果
    return val, np.array(tmp_alloc).reshape(IoT_size).astype(int).tolist(), np.array(t_alloc).reshape(IoT_size,
                                                                                                      BS_size).astype(
        float).tolist()


def opt_vcg():
    global alloc_ret, pay, total_pay, social_welfare
    for i in set_IOT:
        if 1 == alloc_ret[i - 1]:  # 判断物联网设备i是否成为胜者
            # 保存物联网设备i的出价
            temp_bids = bids[i]
            bids[i] = 10000

            # 计算将第i个用户提出之后的最优分配和社会福利
            val_except_i, temp_alloc, temp_f = opt_alloc()

            # 恢复物联网设备i的出价
            bids[i] = temp_bids

            # 不包含第i个用户时的社会福利
            social_welfare_except_i = val_except_i

            # 计算DTC支付给物联网设备i的费用
            pay[i - 1] = round(social_welfare - social_welfare_except_i + bids[i] * alloc_ret[i - 1])

            # 计算总支出
            # for i in set_IOT:
            total_pay += pay[i - 1]


def opt_alloc_and_vcg():
    global alloc_ret, social_welfare, alloc_f, start_time, end_time
    start_time = time.perf_counter()
    social_welfare, alloc_ret, alloc_f = opt_alloc()
    end_time = time.perf_counter()
    print('包含所有用户时的最优分配：', alloc_ret)
    print("基站与物联网设备之间的网络流", alloc_f)
    print()
    print('最大社会福利：', social_welfare)
    print("###############基站为获胜用户支付金额#################")

    # 计算基站为用户支付金额
    opt_vcg()


def show_info():
    print("分配结果：", alloc_ret)
    print("基站给用户的支付结果：", pay)
    print("基站给用户的总支付金额：%f,社会福利：%f" % (total_pay, round(social_welfare, 1)))
    total_number = 0
    for i in set_IOT:
        total_number = total_number + alloc_ret[i - 1]
    print("选中的胜者数量为:%d" % total_number)


print()
print('所有用户的出价：', list(bids.values()))
# 计算算法执行时间
# start_time = time.perf_counter()
opt_alloc_and_vcg()
# end_time = time.perf_counter()

print()
print("############## 最终结果如下 ###################")
show_info()
print("算法执行时间：{}".format(end_time - start_time))
# 资源利用率
winner_cpu = 0
winner_mem = 0
for i in range(IoT_size):
    winner_cpu += alloc_ret[i] * IoT_resource[i + 1, 1]
    # print(winner_cpu)
    winner_mem += alloc_ret[i] * IoT_resource[i + 1, 2]
# print(winner_cpu)
# print(winner_mem)
resource_utilization1 = winner_cpu / DTC_resource[1]
resource_utilization2 = winner_mem / DTC_resource[2]
print("cpu资源利用率:", resource_utilization1)
print("mem资源利用率:", resource_utilization2)
