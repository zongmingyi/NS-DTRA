import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import MultipleLocator

# 每个柱状图的标签
labels = ['2', '4', '6', '8', '10']
# 柱的数值
opt = [72, 95, 98, 100, 100]
NS_DTRA = [72, 95, 98, 100, 100]
greedy = [60, 71, 80, 76, 77]
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
ax.set_ylabel('Number of Winners', fontsize=13)
ax.set_xlabel('Number of UAV-BSs', fontsize=13)
ax.set_ylim(40, 130)
# 将y轴刻度间隔设置并存在变量中
y_major_locator = MultipleLocator(20)
# 设置刻度间隔
axgca = plt.gca()
axgca.yaxis.set_major_locator(y_major_locator)
# x轴刻度不进行计算
ax.set_xticks(x)
ax.set_xticklabels(labels)
plt.title("$M=2,4,6,8,10$ $N=100$ $THP_m=400Mbps$ $THP_{cloud}=1000Mbps$")
ax.legend()

plt.show()
