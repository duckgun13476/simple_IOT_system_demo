# wlan数据

wlansave = [[0 for _ in range(2)] for _ in range(10)]
wlansave[1] = ['TP-LINK_1974', '43673036jiaoshuo']
wlansave[2] = ['P30Pro', '45454545']
# 给定的字模数据

def dzip_chin(data_123):
    # 将数据转换为12x12的二维数组
    n = 12
    array = [[0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            byte_index = i * 2 + j // 8
            bit_index = 7 - j % 8
            pixel_value = (data_123[byte_index] >> bit_index) & 0x01
            array[i][j] = pixel_value
    return array
def Ptct_16(array,x,y,nu,oled):
    for i in range(0,16):
        for j in range(0,16):
            k=array[i][j]
            if nu==0:
                if k==0:
                    k=1
                else:
                    k=0
            oled.pixel(j+x,i+y,k)