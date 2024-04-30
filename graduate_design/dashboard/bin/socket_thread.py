import socket, select
import threading
import time

from dashboard.bin.datawrite import insert_data
import re
from dashboard.lib.log_color import log
from dashboard.lib.update_read import get_latest_update_data
from dashboard.bin.log_write import insert_logs
from dashboard.bin import aes
import os
from dashboard.variables.variable import Var

# !pip install pycryptodome
port = Var.SERVER_listen_port
thread_timeout = 5  # 设定线程超时时间，例如60秒

key = Var.AES_key
iv = Var.AES_iv
try:
    key = os.getenv('KEY', b'\x16\xee\r\x8d<8\xfc\xef>\xeb\xa1(\x9eOr\xcd')
    iv = os.getenv('IV', b'\x02M\x9c\x04\x0bCg\x88\xf5\x17#\xa7 }\xe0\xd7')
except Exception as e:
    log.error(e)


# 分割提取日志字符串
def extract_logs(receive_string):
    # 根据"--"分割字符串
    split_logs = receive_string.split("--")

    # 去除每个元素两侧的破折号，并过滤掉空字符串
    log_data = [log.strip("-") for log in split_logs if log.strip("-")]

    return log_data


def handle_client(client_socket, ):
    try:
        client_socket.settimeout(20)
        # 从客户端接收数据

        data = client_socket.recv(300)
        log.debug(f"解码前: {data}")

        receive = aes.aes_decode(data)
        log.debug(f"解码后:{receive}")
        receive = receive.decode()
        log.info(f"接收: {receive}")

        # 设置超时时间
        timeout = 5  # 秒

        # 用于存储接收到的所有数据片段
        total_data = ""

        # 记录开始时间
        start_time = time.time()

        while True:
            # 检查自开始以来是否已经超过5秒
            if time.time() - start_time > timeout:
                log.debug("超时退出")
                break

            # 使用 select 来检查 socket 是否可读
            readable, _, _ = select.select([client_socket], [], [], 1)

            if readable:
                data_piece = client_socket.recv(1080)
                data_piece = aes.aes_decode(data_piece)

                try:
                    data_piece = data_piece.decode('utf-8', errors='ignore')
                    if data_piece:
                        total_data = total_data + data_piece

                    else:
                        # 如果接收到的数据为空，说明连接已经被远端关闭
                        break
                except Exception as e:
                    log.error(f"错误: {e}")
                # print(data_piece)

        # 合并所有接收到的数据片段

        # 打印或处理接收到的数据
        # print(total_data)
        receive2 = total_data
        # print(receive2)
        log_data = extract_logs(receive2)
        log.info(f"接收: {log_data}")

        # insert_logs(log_data)
        match = re.search(r"T(\d+\.\d+)H(\d+\.\d+)BP(\d+\.\d+)W(\d+\.\d+)"
                          r"A(\d+\.\d+)L(\d+\.\d+)R(\d+\.\d+)"
                          r"V(\d+\.\d+)E(\d+\.\d+)CT(\d+\.\d+)", receive)
        ID = receive[4:14]
        log.info(ID)

        if match:
            # 将匹配的字符串转换为浮点数
            temperature = float(match.group(1))
            wet = float(match.group(2))
            press = float(match.group(3))
            power = float(match.group(4))
            panel_A = float(match.group(5))
            light = float(match.group(6))
            T_2 = float(match.group(7))
            core_V = float(match.group(8))
            high = float(match.group(9)) - 100
            chip_temp = float(match.group(10))
            log.info(f'温度为：{temperature}°C,湿度为：{wet}%,压力为：{press}mPa,功率为：{power}W')
            log.info(f'仪表电流为：{panel_A}mA,光照度为：{light}lux,通道2为：{T_2}°C,核心电压为：{core_V}V')
            log.info(f'海拔为：{high}，芯片温度为：{chip_temp}')
            read_data = True
        else:
            log.error("没有找到数据")
            read_data = False

        match2 = re.search(r"P(\d+\.\d+)I(\d+\.\d+)D(\d+\.\d+)S(\d+\.\d+)", receive)
        if match2:
            P_read = float(match2.group(1))
            I_read = float(match2.group(2))
            D_read = float(match2.group(3))
            S_read = float(match2.group(4))
            log.info(f"仪表参数:P={P_read}{I_read}{D_read}{S_read}，ID：{ID}")
            panel_data = True
        else:
            log.error("没有找到仪表参数")
            panel_data = False
        # 发送数据回客户端
        if panel_data + read_data == 2:
            threading.Thread(target=insert_data, args=(
                temperature, wet, power, press, panel_A, light, core_V, T_2, high, chip_temp, ID, P_read,
                I_read, D_read, S_read)).start()
            # insert_data(temperature, wet, power, press, panel_A, light, core_V, T_2, high, chip_temp, ID, P_read,
            # I_read, D_read, S_read)
        else:
            log.warning(f"有部分数据未找到，将跳过数据库存储")
        latest_data = get_latest_update_data(ID)
        P_con = latest_data[1]
        I_con = latest_data[2]
        D_con = latest_data[3]
        S_con = latest_data[4]
        k_con = latest_data[5]
        b_con = latest_data[6]
        feedback = f"服务端成功接收数据，控制参数-P_f={P_con}-I_f={I_con}-D_f={D_con}-k_f={k_con}-b_f={b_con}-S_f={'%.1f' % S_con}"
        feedback_bytes = feedback.encode()

        client_socket.sendall(feedback_bytes)

        log.info(f"插入日志中")

        if ID == "TILGF87080":
            # insert_logs(log_data, "logs_1")
            threading.Thread(target=insert_logs, args=(log_data, "logs_1")).start()
        elif ID == "TILGF37102":
            # insert_logs(log_data, "logs_2")
            threading.Thread(target=insert_logs, args=(log_data, "logs_2")).start()
        elif ID == "TILGF41238":
            # insert_logs(log_data, "logs_3")
            threading.Thread(target=insert_logs, args=(log_data, "logs_3")).start()
        else:
            # insert_logs(log_data, "logs_1")
            threading.Thread(target=insert_logs, args=(log_data, "logs_1")).start()
    except Exception as e:
        # print(e)
        if str(e) == "'NoneType' object is not subscriptable":
            log.warning(f"本次解码发生错误,本次接受将不会存储")
        elif str(e) == "Data must be padded to 16 byte boundary in CBC mode":
            log.warning(f"解密来自仪表的数据时数据不完整，将忽略本次数据！")
        else:
            log.error(f"处理客户端时发生错误: {e}")
    finally:
        # 关闭连接
        client_socket.close()
        log.info(f"连接已关闭")


def socket_listen():  # 超时时间

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = ('0.0.0.0', 9945)
    server_socket.bind(server_addr)
    server_socket.listen(5)  # 增加监听的数量
    # server_socket.setblocking(False)
    # 开始监听传入的连接请求
    server_socket.listen(1)

    log.info(f"正在监听端口： {server_addr}")

    try:
        while True:
            log.debug(f"当前活跃线程数: {threading.active_count()}")
            client_socket, client_address = server_socket.accept()
            log.info(f"连接到： {client_address}")

            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    except Exception as e:
        log.error(f"发生错误: {e}")
    finally:
        server_socket.close()
        log.debug("Socket 已关闭")


# 返回控制参数
P_con = 12.45
I_con = 1.34
D_con = 0.42
k_con = 1.23
b_con = 2.13

# PID启用 线性启动  报警启动  滤波启动   限幅限速        中位值            平均值
(PID_f, LIN_f, alarm_f, filter_f, filter_A,
 filter_middle, filter_average, H, battery_save, J) = (True, False, False, False, True,
                                                       False, True, False, True, False)

# Pack the boolean values into a single integer
S_con = (int(PID_f) << 9 | int(LIN_f) << 8 | int(alarm_f) << 7 | int(filter_f) << 6 | int(filter_A) << 5 |
         int(filter_middle) << 4 | int(filter_average) << 3 | int(H) << 2 | int(battery_save) << 1 | int(J))

if __name__ == "__main__":
    socket_listen()
