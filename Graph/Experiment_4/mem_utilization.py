import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import MultipleLocator

# 每个柱状图的标签
labels = ['20%', '40%', '60%', '80%', '100%']
# 柱的数值
opt = [0.32, 0.633, 0.936, 0.9524, 0.9524]
NS_DTRA = [0.32, 0.634, 0.936, 0.9524, 0.9524]
greedy = [0.21, 0.378, 0.465, 0.505, 0.6135]
# x轴刻度标签位置
x = np.arange(len(labels))
# 柱子宽度
width = 0.25
ax = plt.subplot()
rects1 = ax.bar(x - width, opt, width, label='OPT-DTRA', color=['red', 'red', 'red', 'red', 'red'])
rects2 = ax.bar(x, NS_DTRA, width, label='NS-DTRA',
                color=['mediumseagreen', 'mediumseagreen', 'mediumseagreen', 'mediumseagreen', 'mediumseagreen'])
rects3 = ax.bar(x + width, greedy, width, label='Greedy',
                color=['blue', 'blue', 'blue', 'blue', 'blue'])
# 设置y轴标题
ax.set_ylabel('Utilization of Memory', fontsize=13)
ax.set_xlabel('The Proportion of Throughput', fontsize=13)
ax.set_ylim(0, 1.3)
# 将y轴刻度间隔设置并存在变量中
y_major_locator = MultipleLocator(0.2)
# 设置刻度间隔
axgca = plt.gca()
axgca.yaxis.set_major_locator(y_major_locator)
# x轴刻度不进行计算
ax.set_xticks(x)
ax.set_xticklabels(labels)
plt.title("$M=5$ $N=100$ $THP_m=200Mbps$ $THP_{cloud}=2000Mbps$")
ax.legend()

plt.show()
