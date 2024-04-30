import os
import psutil
from dashboard.bin.log_write import log
# 获取当前脚本的进程ID
pid = os.getpid()
# 通过进程ID获取进程对象
process = psutil.Process(pid)
# 使用进程对象获取内存信息
memory_info = process.memory_info()

# 打印内存使用信息
log.info(f"物理内存: {memory_info.rss / 1024 ** 2:.2f} MB 虚拟内存: {memory_info.vms / 1024 ** 2:.2f} MB")
