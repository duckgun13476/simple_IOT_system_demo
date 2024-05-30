from machine import SoftI2C,Pin         #从machine模块导入I2C、Pin子模块
from ssd1306 import SSD1306_I2C     #从ssd1306模块中导入SSD1306_I2C子模块
import urandom
################################################################
#一阶惯性滤波#
def first_order_filter(alpha, input_signal_1, input__signal_0):
    output = alpha * input_signal_1 + (1 - alpha) * input__signal_0
    return output
#input_signal_1 前一刻的采样
#input_signal_0 当前时刻的采样
#output         输出
#################################################################
#模拟随机数函数
def inc_r():
    return urandom.randint(1, 100)*0.00001
################################################################
#限幅滤波#
def limit_n(input, high_limit, low_limit):
    if input > high_limit:
        output = high_limit
    if input < low_limit:
        output =low_limit
    return output
#input  输入值
#high/low 高低限幅
#output 输出
################################################################
#存储池右移#
def right_shift_2d_array(array):
    for row in array:
        for j in range(len(row) - 1, 0, -1):
            row[j] = row[j - 1]
        row[0] = 0  # Fill the leftmost element with 0
################################################################
#绘制图表#
def chart_show(array_10x20,oled,channel,size):
    oled.line(19,channel*12+5,19,channel*12+16,1) #画出边界线
    cc=12
   # size = 0.2 #5分0.5刻度的数值变化
    E1  = array_10x20[channel*2-2][0] - array_10x20[channel*2-2][1]
    EP1 = int( E1/(size/5) )#这里8是图表y的坐标##1 2 3 4   2 4 6 8   0 2 4 6      1 3 5 7
    if EP1 >= 5:
        EP1 = 5
    if EP1 <= -5:
        EP1 = -5
    if EP1 <= 5 and EP1 >= -5:
        EP1 = int(EP1)
    array_10x20[channel*2-1][0] = - EP1 +11+channel*cc
    
    #oled.fill_rect(68,0,48,8,0)
    #oled.text(str('%.2f'%array_10x20[channel*2-2][0]),68,0) #此处用于显示实时的坐标
    
    oled.line(17,6+channel*cc,17,5+(channel+1)*cc,0)
    oled.line(17,11+channel*cc,17,array_10x20[channel*2-1][0],1)
    
    oled.line(16,6+channel*cc,16,5+(channel+1)*cc,0)
    oled.line(16,11+channel*cc,16,array_10x20[channel*2-1][1],1)
    
    oled.line(15,6+channel*cc,15,5+(channel+1)*cc,0)
    oled.line(15,11+channel*cc,15,array_10x20[channel*2-1][2],1)
    
    oled.line(14,6+channel*cc,14,5+(channel+1)*cc,0)
    oled.line(14,11+channel*cc,14,array_10x20[channel*2-1][3],1)
    
    oled.line(13,6+channel*cc,13,5+(channel+1)*cc,0)
    oled.line(13,11+channel*cc,13,array_10x20[channel*2-1][4],1)
    
    oled.line(12,6+channel*cc,12,5+(channel+1)*cc,0)
    oled.line(12,11+channel*cc,12,array_10x20[channel*2-1][5],1)
    
    oled.line(11,6+channel*cc,11,5+(channel+1)*cc,0)
    oled.line(11,11+channel*cc,11,array_10x20[channel*2-1][6],1)
    
    oled.line(10,6+channel*cc,10,5+(channel+1)*cc,0)
    oled.line(10,11+channel*cc,10,array_10x20[channel*2-1][7],1)
    
    oled.line(9,6+channel*cc,9,5+(channel+1)*cc,0)
    oled.line(9,11+channel*cc,9,array_10x20[channel*2-1][8],1)
    
    oled.line(8,6+channel*cc,8,5+(channel+1)*cc,0)
    oled.line(8,11+channel*cc,8,array_10x20[channel*2-1][9],1)
    
    oled.line(7,6+channel*cc,7,5+(channel+1)*cc,0)
    oled.line(7,11+channel*cc,7,array_10x20[channel*2-1][10],1)
    
    oled.line(6,6+channel*cc,6,5+(channel+1)*cc,0)
    oled.line(6,11+channel*cc,6,array_10x20[channel*2-1][11],1)
    
    oled.line(5,6+channel*cc,5,5+(channel+1)*cc,0)
    oled.line(5,11+channel*cc,5,array_10x20[channel*2-1][12],1)
    
    oled.line(4,6+channel*cc,4,5+(channel+1)*cc,0)
    oled.line(4,11+channel*cc,4,array_10x20[channel*2-1][13],1)
    
    oled.line(3,6+channel*cc,3,5+(channel+1)*cc,0)
    oled.line(3,11+channel*cc,3,array_10x20[channel*2-1][14],1)
    
    oled.line(2,6+channel*cc,2,5+(channel+1)*cc,0)
    oled.line(2,11+channel*cc,2,array_10x20[channel*2-1][15],1)
    
    oled.line(1,6+channel*cc,1,5+(channel+1)*cc,0)
    oled.line(1,11+channel*cc,1,array_10x20[channel*2-1][16],1)
    oled.show()
#################################
#汉字绘制
def Chin_text(array,x,y,nu,oled):
    for i in range(0,12):
        for j in range(0,12):
            k=array[i][j]
            if nu==0:
                if k==0:
                    k=1
                else:
                    k=0
            oled.pixel(j+x,i+y,k)
    #oled.show()
#图标绘制
def Ptct_text(array,x,y,nu,oled):
    for i in range(0,8):
        for j in range(0,8):
            k=array[i][j]
            if nu==0:
                if k==0:
                    k=1
                else:
                    k=0
            oled.pixel(j+x,i+y,k)
    #oled.show()
#16*16绘制
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
    #oled.show()
#####################################
#PID控制单元
def PID_con():
    Ek1=Kp(1+1/Ti*Ek0+1/Td*Ek0)