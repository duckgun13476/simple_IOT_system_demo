from datetime import datetime, timedelta

# 给定的时间列表
time_list = ['debug: 芯片温度正常 2024-03-17 12:09:45', 'info: 读取数据。。 2024-03-17 12:09:45',
             'debug: WLAN已连接 2024-03-17 12:09:45']


# 定义函数将时间字符串转换为datetime对象，加8小时，再转换回字符串
def convert_time_and_add_eight_hours(time_str):
    # 提取时间字符串中的时间部分
    time_part = time_str.split()[-1]

    # 将时间字符串转换为datetime对象
    time_obj = datetime.strptime(time_part, "%H:%M:%S")

    # 加上8小时
    updated_time = time_obj + timedelta(hours=8)

    # 将更新后的时间转换为字符串
    updated_time_str = updated_time.strftime("%H:%M:%S")

    # 替换原时间字符串中的时间部分
    updated_time_str_full = time_str.replace(time_part, updated_time_str)

    return updated_time_str_full


def time_8(time_list):
    # 循环处理时间列表中的每个时间字符串
    updated_time_list = [convert_time_and_add_eight_hours(time_str) for time_str in time_list]
    return updated_time_list

if __name__ == '__main__':
    #前时间表
    updated_time_list = time_8(time_list)
    # 打印更新后的时间列表
    for updated_time_str in updated_time_list:
        print(updated_time_str)
