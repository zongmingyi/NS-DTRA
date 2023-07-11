import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import MultipleLocator

# 每个柱状图的标签
labels = ['10', '50', '100', '200', '300']
# 柱的数值
opt = [7, 37, 72, 152, 232]
NS_DTRA = [7, 37, 72, 152, 232]
greedy = [6, 34, 60, 134, 207]
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
ax.set_xlabel('Number of IoT devices', fontsize=13)
ax.set_ylim(0, 240)
# 将y轴刻度间隔设置并存在变量中
y_major_locator = MultipleLocator(40)
# 设置刻度间隔
axgca = plt.gca()
axgca.yaxis.set_major_locator(y_major_locator)
# x轴刻度不进行计算
ax.set_xticks(x)
ax.set_xticklabels(labels)
plt.title("$M=2$ $N=10,50,100,200,300$ $THP_m=4000Mbps$ $THP_{cloud}=10000Mbps$")
ax.legend()

plt.show()
