import random

raw_data = []
with open('raw_data_500.txt', 'r', encoding='utf8') as data:
    n = int(data.readline().rstrip())
    # print(n)

    for i in range(n):
        tmp = int(data.readline().rstrip())
        raw_data.append(tmp)
    # print(raw_data)
    for i in range(n):
        raw_data.append(raw_data[i] + random.randint(50, 60) * (-1) ** random.randrange(2))
    # print(len(raw_data))
with open('raw_data_1000.txt', 'w', encoding='utf8') as file:
    file.write("%d\n" % len(raw_data))
    for i in range(len(raw_data)):
        file.write('%d\n' % raw_data[i])
