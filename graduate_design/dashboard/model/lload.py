import numpy as np
from visual import visualize_3d_array
# 读取保存的数组
loaded_arr = np.load('../model/arr.npy')
print(loaded_arr.shape)
visualize_3d_array(loaded_arr)