import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import MultipleLocator

# 每个柱状图的标签
labels = ['10', '50', '100', '200', '300']
# 柱的数值
opt = [293.5, 1645.5, 3224.5, 6973.5, 10573.5]
NS_DTRA = [293.5, 1645.5, 3224.5, 6973.5, 10573.5]
greedy = [241, 1545,2824.5, 6248, 9741.5]
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
ax.set_ylabel('Total Utility ', fontsize=13)
ax.set_xlabel('Number of IoT devices', fontsize=13)
ax.set_ylim(0, 11000)
# 将y轴刻度间隔设置并存在变量中
y_major_locator = MultipleLocator(2000)
# 设置刻度间隔
axgca = plt.gca()
axgca.yaxis.set_major_locator(y_major_locator)
# x轴刻度不进行计算
ax.set_xticks(x)
ax.set_xticklabels(labels)
plt.title("$M=2$ $N=10,50,100,200,300$ $THP_m=4000Mbps$ $THP_{cloud}=10000Mbps$")
ax.legend()

plt.show()
