import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable


def visualize_3d_array(array):
    # 创建一个三维坐标轴对象
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # 创建一个网格
    z, x, y = np.meshgrid(np.arange(array.shape[0]), np.arange(array.shape[1]), np.arange(array.shape[2]))

    # 使用scatter函数绘制三维散点图，颜色表示数值
    scatter = ax.scatter(z, x, y, c=array.flatten(), cmap='viridis')

    # 创建颜色映射对象
    sm = ScalarMappable(cmap='viridis')
    sm.set_array(array.flatten())

    # 添加颜色条，从三维坐标轴对象中"窃取"空间
    cbar = plt.colorbar(sm, ax=ax, ticks=np.linspace(array.min(), array.max(), num=12))

    # 设置颜色条标签
    cbar.set_label('Temperature')

    # 添加标题
    plt.title('3D Visualization')

    # 显示图形
    plt.show()

# 示例数组
#awe = np.random.rand(10, 10, 2)
#print(awe.shape)
# 调用函数进行可视化
#visualize_3d_array(awe)
