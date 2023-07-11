DTC_resource = {}
bids = {}
IoT_resource = {}
IoT_bws = {}
IoT_value = {}
DTC_BS_BWs={}
BS_THP={}
IoT_BS_BWs={}
BS_CH={}
with open("experiment_1_user.txt", 'r', encoding='utf8') as user_file:
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
with open("uav_data.txt", 'r', encoding="utf8") as uav_file:
    BS_size = int(uav_file.readline().strip('\n'))
    for i in range(BS_size):
        List1 = list(uav_file.readline().strip('\n').split())
        DTC_BS_BWs[int(List1[0])] = int(List1[1])
        BS_THP[int(List1[0])] = int(List1[2])
    DTC_THP = int(uav_file.readline().strip('\n'))
    for i in range(IoT_size):
        for j in range(BS_size):
            List2 = list(uav_file.readline().strip('\n').split())
            IoT_BS_BWs[int(List2[0]),int(List2[1])]=int(List2[2])
    for j in range(BS_size):
        channel = 0
        for i in range(IoT_size):
            if IoT_BS_BWs[i + 1, j + 1] > 0:
                channel += 1
        BS_CH[j] = channel

print(bids)
print(IoT_value)
print(IoT_bws)
print(DTC_resource)
print(IoT_BS_BWs)
print(BS_CH)