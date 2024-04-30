import subprocess
import platform
import re
from dashboard.lib.log_color import log


def ping(host):
    # 根据操作系统调整ping命令
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '4', host]

    try:
        # 执行ping命令
        output = subprocess.run(command, stdout=subprocess.PIPE, text=True, check=True)
        print(output.stdout)

        # 根据操作系统调整正则表达式来提取延迟信息
        if platform.system().lower() == "windows":
            # Windows系统通常显示 "时间=<delay>ms"
            match = re.search(r'时间=(\d+)ms', output.stdout)
        else:
            # Unix/Linux系统通常显示 "time=<delay> ms"
            match = re.search(r'time=(\d+\.\d+) ms', output.stdout)

        if match:
            delay = match.group(1)
            return f'{delay} ms'
        else:
            return '无法解析延迟'
    except subprocess.CalledProcessError:
        return '连接失败'


if __name__ == '__main__':
    # 测试一个地址，比如 "google.com"
    result = ping("google.com")
    log.info(result)
