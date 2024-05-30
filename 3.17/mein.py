from machine import Pin
import utime,time
turn = 0
up=Pin(27,Pin.IN,Pin.PULL_UP)
# Pin(27,Pin.IN)
# time.sleep_ms(2000)
now_time = utime.ticks_us()
print("初始化完成！")        
while True:
    
    if up.value() ==0:
        last_time =now_time
        now_time = utime.ticks_us()
        if up.value() ==1:
            turn +=1
            print(utime.ticks_us())
            gap = now_time-last_time
            add_count =turn/450
            if gap ==0:
                speed_count=0.0
            else:
                speed_count = (1/450)/gap
            print("用水量："+str(add_count)+" L 流速"+str(speed_count)+"L/s")
#####################

p5 = Pin(5,Pin.OUT)

def control(rad, p_out):
    cat_0 = 340
    cat_180 = 2250
    time_cont = cat_0 + int((cat_180-cat_0)*(rad/180))
    for i in range(5):
        p_out.off()            
        p_out.on()
        time.sleep_us(time_cont)
        p_out.off()
        time.sleep_us(80000)
