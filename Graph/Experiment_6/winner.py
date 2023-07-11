import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

# 设备出价
x = [16.5, 20, 22, 22.4, 22.49,22.51,22.6,24 , 28]
# 设备效用
y = [4, 4, 4, 4,4,0, 0, 0, 0]

fig = plt.figure(facecolor="white", figsize=(8, 5))

ax = plt.subplot()
# ax.grid()

plt.rcParams['figure.dpi'] = 300
# 设置x，y轴坐标刻度，范围,名称
ax.set_xlim([15, 30])
ax.set_ylim([-2, 6])
ax.set_xlabel("Bid of Device 2(Win)", fontsize=12)
ax.set_ylabel("Utility of Device 2(Win) ", fontsize=11)
# 将x轴的刻度间隔设置为1，并存在变量里
x_major_locator = MultipleLocator(3)
y_major_locator = MultipleLocator(2)
# 设置刻度间隔
axgca = plt.gca()
axgca.xaxis.set_major_locator(x_major_locator)
axgca.yaxis.set_major_locator(y_major_locator)
# 添加数据并设置线的格式 markerfacecolor='white'使节点为空心
ax.plot(x, y, color='red', marker='*', markerfacecolor='white', linestyle='--', linewidth=2)
plt.title("$M=2$ $N=20$ $THP_m=800Mbps$ $THP_{cloud}=2000Mbps$")
# ax.legend(loc='upper left')
plt.show()
