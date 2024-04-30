import numpy as np
from dashboard.lib.sugar import timer

"""
计算温度变化量

参数：
arr : numpy数组
    当前温度场数组
thermal_diffusivity : float
    热扩散系数    0.024 m²/s
temperature_gradient : float
    温度梯度（每米温度变化量）  0.001K/m
time_step : float
    模拟时间步长（秒）  5s
spatial_step : float
    空间步长（米）  0.2

返回：
temperature_change : numpy数组
    温度变化量数组

# 定义混凝土的参数
k = 1.4  # 热导率 W/(m·K)
rho = 2300  # 密度 kg/m³
c_p = 840  # 比热容 J/(kg·K)

# 计算热扩散系数
alpha = k / (rho * c_p)
7.246376811594202e-07
"""


@timer
def calculate_temperature_change(arr, wall, different_neighbours, speed=1.0, thermal_d=0.024,
                                 cement_d=7.246376811594202e-07,
                                 temperature_gradient=0.001, time_step=2.5, spatial_step=0.2):
    temperature_change = np.zeros_like(arr, dtype=float)
    depth, height, width = arr.shape

    for k in range(1, depth - 1):  # 调整循环范围，避免超出数组边界
        for i in range(1, height - 1):  # 调整循环范围，避免超出数组边界
            for j in range(1, width - 1):  # 调整循环范围，避免超出数组边界
                if different_neighbours[k, i, j]:
                    if wall[k, i, j] == 1:  # 如果此点不是墙，则使用空气热扩散系数，否则使用混凝土扩散系数
                        thermal_diffusivity = thermal_d
                    else:
                        thermal_diffusivity = cement_d * 0.1  # 单位换算
                    for dk in [-1, 0, 1]:
                        for di in [-1, 0, 1]:
                            for dj in [-1, 0, 1]:
                                if dk == 0 and di == 0 and dj == 0:
                                    continue
                                nk, ni, nj = k + dk, i + di, j + dj
                                if 0 <= nk < depth and 0 <= ni < height and 0 <= nj < width:
                                    dist = np.sqrt(dk ** 2 + di ** 2 + dj ** 2)
                                    # total_weight += 1 / dist
                                    core_change = speed * (thermal_diffusivity * time_step / (
                                            spatial_step ** 2) * (
                                                                   (arr[k - 1, i, j] + arr[
                                                                       k + 1, i, j] +
                                                                    arr[k, i - 1, j] + arr[
                                                                        k, i + 1, j] +
                                                                    arr[k, i, j - 1] + arr[
                                                                        k, i, j + 1]) -
                                                                   6 * arr[
                                                                       k, i, j]) + temperature_gradient * time_step) / 1000
                                    # arr[k,i,j]+temperature_change[k, i, j]
                                    # print(core_change)
                                    if (core_change + arr[k, i, j]) >= max(arr[k - 1, i, j], arr[k + 1, i, j],
                                                                           arr[k, i, j],
                                                                           arr[k, i - 1, j], arr[k, i + 1, j],
                                                                           arr[k, i, j - 1], arr[k, i, j + 1]):
                                        # print("上限")
                                        temperature_change_pa = max(arr[k - 1, i, j], arr[k + 1, i, j],
                                                                    arr[k, i, j],
                                                                    arr[k, i - 1, j], arr[k, i + 1, j],
                                                                    arr[k, i, j - 1], arr[k, i, j + 1]) - arr[
                                                                    k, i, j]
                                    elif (core_change + arr[k, i, j]) <= min(arr[k - 1, i, j], arr[k + 1, i, j],
                                                                             arr[k, i, j],
                                                                             arr[k, i - 1, j], arr[k, i + 1, j],
                                                                             arr[k, i, j - 1], arr[k, i, j + 1]):
                                        # print("下限")
                                        temperature_change_pa = min(arr[k - 1, i, j], arr[k + 1, i, j],
                                                                    arr[k, i, j],
                                                                    arr[k, i - 1, j], arr[k, i + 1, j],
                                                                    arr[k, i, j - 1], arr[k, i, j + 1]) - arr[
                                                                    k, i, j]
                                    else:
                                        temperature_change_pa = core_change

                                    ek = arr[k - 1, i, j] + arr[k + 1, i, j] + arr[k, i - 1, j] + arr[k, i + 1, j] + \
                                         arr[k, i, j - 1] + arr[k, i, j + 1] - 6 * arr[k, i, j]
                                    if ek != 0:
                                        temperature_change[k - 1, i, j] += (temperature_change_pa / ek) * (
                                                arr[k, i, j] - arr[k - 1, i, j])
                                        temperature_change[k + 1, i, j] += (temperature_change_pa / ek) * (
                                                arr[k, i, j] - arr[k + 1, i, j])
                                        temperature_change[k, i - 1, j] += (temperature_change_pa / ek) * (
                                                arr[k, i, j] - arr[k, i - 1, j])
                                        temperature_change[k, i + 1, j] += (temperature_change_pa / ek) * (
                                                arr[k, i, j] - arr[k, i + 1, j])
                                        temperature_change[k, i, j - 1] += (temperature_change_pa / ek) * (
                                                arr[k, i, j] - arr[k, i, j - 1])
                                        temperature_change[k, i, j + 1] += (temperature_change_pa / ek) * (
                                                arr[k, i, j] - arr[k, i, j + 1])
                                        temperature_change[k, i, j] += temperature_change_pa
                                    elif arr[k - 1, i, j] == arr[k + 1, i, j] and arr[k, i - 1, j] == arr[
                                        k, i + 1, j] and \
                                            arr[k, i, j - 1] == arr[k, i, j + 1] == arr[k, i, j]:

                                        # print("跳过对角边界点")
                                        pass
                                    else:
                                        numbers = [arr[k - 1, i, j], arr[k + 1, i, j], arr[k, i - 1, j],
                                                   arr[k, i + 1, j], arr[k, i, j - 1], arr[k, i, j + 1]]
                                        print(arr[k][i][j])
                                        print(numbers)
                                        result = [num for num in numbers if num > arr[k, i, j]]
                                        print(sum(result))
                                        print(len(result))
                                        total = sum(result) / len(result)
                                        around_change = speed * (thermal_diffusivity * time_step / (
                                                spatial_step ** 2) * (total -
                                                                      arr[
                                                                          k, i, j]) + temperature_gradient * time_step) / 1000

                                        temperature_change[k - 1, i, j] += (around_change / total) * (
                                                arr[k, i, j] - arr[k - 1, i, j])
                                        temperature_change[k + 1, i, j] += (around_change / total) * (
                                                arr[k, i, j] - arr[k + 1, i, j])
                                        temperature_change[k, i - 1, j] += (around_change / total) * (
                                                arr[k, i, j] - arr[k, i - 1, j])
                                        temperature_change[k, i + 1, j] += (around_change / total) * (
                                                arr[k, i, j] - arr[k, i + 1, j])
                                        temperature_change[k, i, j - 1] += (around_change / total) * (
                                                arr[k, i, j] - arr[k, i, j - 1])
                                        temperature_change[k, i, j + 1] += (around_change / total) * (
                                                arr[k, i, j] - arr[k, i, j + 1])

                                    # if temperature_change[k + 1, i, j] >= 0.1:
                                    #  print(f"core{temperature_change[k + 1, i, j]}-{i}-{j}-{k}-{ek}-{core_change}")
                                # if temperature_change[k - 1, i, j] >= 0.1:
                                #  print(f"core{temperature_change[k - 1, i, j]}-{i}-{j}-{k}-{ek}-{core_change}")
                                # if temperature_change[k, i + 1, j] >= 0.1:
                                #   print(f"core{temperature_change[k, i + 1, j]}-{i}-{j}-{k}-{ek}-{core_change}")
                                #  if temperature_change[k, i - 1, j] >= 0.1:
                                #   print(f"core{temperature_change[k, i - 1, j]}-{i}-{j}-{k}-{ek}-{core_change}")
                                # if temperature_change[k, i, j + 1] >= 0.1:
                                #   print(f"core{temperature_change[k, i, j + 1]}-{i}-{j}-{k}-{ek}-{core_change}")
                                #  if temperature_change[k, i, j - 1] >= 0.1:
                                #   print(f"core{temperature_change[k, i, j - 1]}-{i}-{j}-{k}-{ek}-{core_change}")

    return temperature_change


def extract_different_neighbours(arr):
    # 创建一个与原数组形状相同的布尔数组，用于标记不同的点
    different_neighbours = np.zeros_like(arr, dtype=bool)

    # 获取数组的形状
    depth, height, width = arr.shape

    # 遍历数组中的每个位置
    for k in range(depth):
        for i in range(height):
            for j in range(width):
                center_value = arr[k, i, j]

                # 检查周围26个点是否与中心点不同，如果不同则标记为True
                for dk in [-1, 0, 1]:
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if dk == 0 and di == 0 and dj == 0:
                                continue
                            nk, ni, nj = k + dk, i + di, j + dj
                            if 0 <= nk < depth and 0 <= ni < height and 0 <= nj < width and arr[
                                nk, ni, nj] != center_value:
                                different_neighbours[nk, ni, nj] = True
                                different_neighbours[k, i, j] = True  # 将中心点也标记为True
                                break  # 只要找到一个与中心点不同的点，就可以退出内循环
                        if different_neighbours[k, i, j]:  # 如果已经标记为True，则退出外循环
                            break
                    if different_neighbours[k, i, j]:  # 如果已经标记为True，则退出外循环
                        break

    # 返回标记了不同点及其周围26个点的布尔数组
    return different_neighbours

