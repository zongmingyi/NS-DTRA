import random

with open('train_data.txt', 'r', encoding='utf8') as data:
    # 读取搜集环境数据大小
    n = int(data.readline().rstrip())
    raw_data = []

    # print(n)
    # print(data.readline())
    for i in range(n):
        tmp_list = data.readline().strip("\n").split(',')
        # print(tmp_list)
        # if 60 >= int(tmp_list[1]) >= 30 and int(tmp_list[2]) <= 150:
        if 120 >= int(tmp_list[1]) >= 60:
            raw_data.append(int(tmp_list[1])*10)
    # print(raw_data)
    # print(len(raw_data))
    for i in range(45, 50):
        raw_data.append(random.randint(600, 1200))
    # print(raw_data)
    # print(len(raw_data))
    # print("信道总数：%d" % sum())
    # print(req_channel)
    # print(reward)
    # print(compute_cost)
print("============================================================")
with open('raw_data_10.txt', 'w+', encoding='utf8') as file:
    # file.write('%d\n' % ())
    file.write("%d\n" % 10)
    for i in range(10):
        file.write("%d\n" % (raw_data[i]))
