import torch
import pynvml

# 初始化NVML，这是与NVIDIA GPU驱动交互的前提
pynvml.nvmlInit()

# 获取GPU数量
device_count = torch.cuda.device_count()

for i in range(device_count):
    # 使用PyTorch获取GPU的基本信息
    print(f"GPU {i}:")
    print(f"名称: {torch.cuda.get_device_name(i)}")
    print(f"总显存: {torch.cuda.get_device_properties(i).total_memory / 1024 ** 3:.2f} GB")
    print(f"可用显存: {torch.cuda.memory_reserved(i) / 1024 ** 3:.2f} GB")

    # 使用pynvml获取更详细的信息
    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    print(f"总显存: {info.total / 1024 ** 3:.2f} GB")
    print(f"已用显存: {info.used / 1024 ** 3:.2f} GB")
    print(f"空闲显存: {info.free / 1024 ** 3:.2f} GB")
    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
    print(f"GPU利用率: {util.gpu}%")
    print(f"显存利用率: {util.memory}%")

# 完成NVML的使用后关闭
pynvml.nvmlShutdown()
