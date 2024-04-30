import numpy as np


def calculate_temperature_change(arr, different_neighbours, weight=0.1):
    # 创建一个与原数组形状相同的数组，用于存储每个位置的温度变化量
    temperature_change = np.zeros_like(arr, dtype=float)

    # 获取数组的形状
    height, width = arr.shape

    # 定义权值矩阵，这里简单起见，假设每个相邻点对中心点的影响相同

    # 遍历数组中的每个位置
    for i in range(height):
        for j in range(width):
            if different_neighbours[i, j]:
                # 计算周围8个点对中心点的温度影响，并累加到温度变化数组上
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < height and 0 <= nj < width:
                            temperature_change[i, j] += weight * (arr[ni, nj] - arr[i, j])

    # 返回温度变化数组
    return temperature_change


# 遍历函数
def extract_different_neighbours(arr):
    # 创建一个与原数组形状相同的布尔数组，用于标记不同的点
    different_neighbours = np.zeros_like(arr, dtype=bool)

    # 获取数组的形状
    height, width = arr.shape

    # 遍历数组中的每个位置
    for i in range(height):
        for j in range(width):
            center_value = arr[i, j]

            # 检查周围8个点是否与中心点不同，如果不同则标记为True
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < height and 0 <= nj < width and arr[ni, nj] != center_value:
                        different_neighbours[ni, nj] = True
                        different_neighbours[i, j] = True  # 将中心点也标记为True
                        break  # 只要找到一个与中心点不同的点，就可以退出内循环
                if different_neighbours[i, j]:  # 如果已经标记为True，则退出外循环
                    break

    # 返回标记了不同点及其周围8个点的布尔数组
    return different_neighbours


# 示例数组
#arr = np.array([[1, 1, 1, 1, 1, 5],
  #              [1, 1, 1, 1, 1, 1],
   #             [1, 1, 1, 1, 1, 1],
   #             [1, 1, 1, 1, 1, 1],
   #             [1, 1, 1, 1, 1, 1],
     #           [1, 1, 1, 1, 1, 1]])

# 提取不同的点及其周围8个点
# result = extract_different_neighbours(arr)

# 打印结果
#arr_update = arr
# 运算前
#print(arr_update)
# print(temperature_change)
#for i in range(7):
  #  result = extract_different_neighbours(arr_update)
    #temperature_change = calculate_temperature_change(arr_update, result)
   # arr_update = arr_update + temperature_change
   # print(arr_update)
