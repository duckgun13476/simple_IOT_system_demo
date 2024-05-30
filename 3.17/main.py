import network,time,onewire
import ds18x20,usocket
import bmp280,re,ujson
import gc,fn,function,font
from machine import SoftI2C,Pin,Timer,WDT,RTC
from ssd1306 import SSD1306_I2C
from PCF8591 import PCF8591 
from log import Logger
import aes
ID = "TILGF41238"
Pin(5,Pin.IN) # 切断dht11和18b20 他们与互联网模块冲突
#初始化日志  Pin(5,Pin.OUT)
log = Logger()
#初始化oled
i2c = SoftI2C(sda=Pin(13), scl=Pin(14))
log.debug("i2c线路定义完成")
try:
    oled = SSD1306_I2C(128, 64, i2c, addr=0x3c)
    log.debug("OLED正常")
except:
    log.error("找不到OLED")
#开机logo
fn.logo(oled)
oled.show()


# 定义芯片掉电存储函数：
# 存储参数到 RTC 内存
rtc = RTC()
def save_params_to_rtc(data):
    json_data = ujson.dumps(data)
    rtc.memory(json_data)

# 从 RTC 内存读取参数
def load_params_from_rtc():
    try:
        json_data = rtc.memory()
        if json_data:
            return ujson.loads(json_data)
            log.warning("芯片重启！")
            
        else:
            log.info("芯片初始化中")
            return {}
    except ValueError:
        return {}
#定义按键
up=Pin(25,Pin.IN,Pin.PULL_UP)
left=Pin(26,Pin.IN,Pin.PULL_UP)
shift = Pin(16,Pin.IN,Pin.PULL_UP)
down=Pin(17,Pin.IN,Pin.PULL_UP)
confirm=Pin(21,Pin.IN,Pin.PULL_UP)
right=Pin(33,Pin.IN,Pin.PULL_UP)
#初始化控制参数：
try:
    loaded_data = load_params_from_rtc()
    
    P = loaded_data.get('P',1)
    I = loaded_data.get('I',1)
    D = loaded_data.get('D',1)
    S = loaded_data.get('S',600) 
    PID_f, LIN_f, alarm_f, filter_f, filter_A, filter_middle, filter_average,H, battery_save, J= bool(S & (1 << 9)), bool(S & (1 << 8)), bool(S & (1 << 7)), bool(S & (1 << 6)), bool(S & (1 << 5)), bool(S & (1 << 4)), bool(S & (1 << 3)), bool(S & (1 << 2)), bool(S & (1 << 1)), bool(S & 1)
    WLAN = 0
    socket_link = 0 #c初始化为未连接socket
    reconnect_count = 0  # 互联网的重连接次数

    log.info("参数初始化完成")
except:    
    log.error("参数初始化失败")
#初始化位图
if fn.battery0_s != []:
    log.debug("位图处理完成")
else:
    log.error("位图处理失败")
#初始化看门狗
wdt=WDT(timeout=60000) # 40s看门狗
#初始化相关模块
pcf8591 = PCF8591(0x48, i2c)  
if pcf8591.begin():
    log.debug("PCF8591正常")
else:
    log.error("PCF8591绑定失败")
i2c2 = SoftI2C(sda=Pin(19), scl=Pin(18))
try:
    BMP = bmp280.BMP280(i2c2,address = 0x76)
    #log.info("bmp280正常")
except:
    log.error("bmp280绑定失败")
##
#控制模块
def Socket_fun(tim):  
    print("控制："+str(I),end="")
    if alarm_f:
        
        alarm=Pin(22,Pin.OUT)
        time.sleep_ms(100)
        alarm=Pin(22,Pin.IN)
#初始化DHT11
from dht import DHT11
try:
    dt=DHT11(Pin(15))
    #log.info("DHT11正常")
except:
    log.error("DHT11绑定失败")
#初始化DS18B20
try:
    ow= onewire.OneWire(Pin(4)) #使能单总线
    ds = ds18x20.DS18X20(ow)        #传感器是DS18B20
    rom = ds.scan()         #扫描单总线上的传感器地址，支持多个传感器同时连接
    #log.info("DS18B20正常")
except:
    log.error("DS18B20绑定失败")
##
# 初始化WLAN相关参数
WIFI_LED=Pin(2, Pin.OUT) #初始化WIFI指示灯
wlan = network.WLAN(network.STA_IF) #STA模式
if not wlan.isconnected():
    wlan.active(0)                   #关闭接口
else:
    print("互联网已在启动时连接")
    wlan.active(1)  
log.info("初始化完成")
time.sleep_ms(2000)         #首次启动停顿2秒然传感器稳定
oled.fill(0)
#############################################################################
#WIFI连接函数
def WIFI_Connect():



    if not wlan.isconnected():
        print('连接到WLAN中...')
        if wlan.active() == False:
            wlan.active(True)
        else:
            wlan.active(False)
            time.sleep_ms(3000)
            wlan.active(True)
        k=wlan.scan()
        for j_1 in range(10):
            for i_1 in range(9):
                try:
                    if k[i_1][0].decode('uft-8') == font.wlansave[j_1][0]:
                        print("匹配到记录WLAN：",str(font.wlansave[j_1]))
                        start_time=time.time()              #记录时间做超时判断
                        for g_34 in range(2):
                            try:
                                print("连接中：")
                                wlan.connect(font.wlansave[j_1][0], font.wlansave[j_1][1]) #输入WIFI账号密码
                                break
                            except Exception as e:
                                print(e)
                                if str(e)=="Wifi Internal Error":
                                    print("WLAN 模块异常，可能是密码错误或协议不匹配，正在重连，请稍等。。。")
                                    wlan.active(False)
                                    for i_12 in range(5):
                                        time.sleep_ms(1000)
                                        print(str(5-i_12)+'s')
                                    wlan.active(True)
                                    if wlan.scan() == []:
                                        print("WLAN 异常 错误码001")
                                    else:
                                        print("WLAN 模块恢复")
                                        continue
                        while not wlan.isconnected():

                            #LED闪烁提示
                            WIFI_LED.value(1)
                            time.sleep_ms(300)
                            wdt.feed()
                            boot_1()
                            WIFI_LED.value(0)
                            time.sleep_ms(300)

                            #超时判断,15秒没连接成功判定为超时
                            if time.time()-start_time > 15 :
                                print('WIFI 连接超时!')
                                break
                except Exception as e:
                    print(e)
                    print(str(i_1)+str(j_1))
    if wlan.isconnected():
        #LED点亮
        WIFI_LED.value(1)

        #串口打印信息
        print('network information:', wlan.ifconfig())
        print('IP/Subnet/GW:')
        print(wlan.ifconfig()[0])
        print(wlan.ifconfig()[1])
        print(wlan.ifconfig()[2])
        
        
#设置界面
k = False
def boot_1():
    print("进入设置")
    if shift.value() == 0:
        time.sleep_ms(1000)
        if shift.value() == 0:
            time_boot = 0
            choose_on = 1
            while True:
                time_boot+=1
                time.sleep_ms(100)
                if time_boot>=50:
                    # 此时判断是否退出
                    if shift.value() == 0:
                        oled.fill(0) # 退出前先把屏幕清除
                        break
                    
                # 放置设置界面
                oled.fill(0)

                oled.line(0,13,64,13,1)

                #设置
                fn.oled_12_s(fn.shezhi_icon_s,0,0,1,oled)
                fn.oled_12_s(fn.she_s,14,0,1,oled)
                fn.oled_12_s(fn.zhi_s,30,0,1,oled)
                
                
                #网络
                if choose_on == 1:
                    fn.square_s(1,19,45,14,oled)
                fn.oled_12_s(fn.wlan1_s,2,20,1,oled)
                fn.oled_12_s(fn.wang_s,16,20,1,oled)
                fn.oled_12_s(fn.luo_s,32,20,1,oled)
                #参数
                if choose_on == 2:
                    fn.square_s(1,39,45,14,oled)
                fn.oled_12_s(fn.canshu_icon_s,2,40,1,oled)
                fn.oled_12_s(fn.can_s,16,40,1,oled)
                fn.oled_12_s(fn.shu_s,32,40,1,oled)
                #功能
                if choose_on == 3:
                    fn.square_s(65,19,45,14,oled)
                fn.oled_12_s(fn.gongneng_icon_s,66,20,1,oled)
                fn.oled_12_s(fn.gong_s,80,20,1,oled)
                fn.oled_12_s(fn.neng_s,96,20,1,oled)
                #关于
                if choose_on == 4:
                    fn.square_s(65,39,45,14,oled)
                fn.oled_12_s(fn.guanyu_icon_s,66,40,1,oled)
                fn.oled_12_s(fn.guan_s,80,40,1,oled)
                fn.oled_12_s(fn.yu_s,96,40,1,oled)
                
                if choose_on == 0 or choose_on == -1:
                    choose_on = 4
                if choose_on == 5 or choose_on == 6:
                    choose_on = 1
                    
                # 选择状态 初始为1
                if up.value() == 0:
                    time.sleep_ms(100)
                    if up.value() == 1:
                        choose_on -= 1
                        
                if down.value() == 0:
                    time.sleep_ms(100)
                    if down.value() == 1:
                        choose_on += 1
                        
                if left.value() == 0:
                    time.sleep_ms(100)
                    if left.value() == 1:
                        choose_on -= 2
                        
                if right.value() == 0:
                    time.sleep_ms(100)
                    if right.value() == 1:
                        choose_on += 2
                
                if confirm.value() == 0: 
                    time.sleep_ms(100)
                    if confirm.value() == 1:
                        oled.fill(0)
                        boot_2(choose_on)
                       
                oled.show()
                
                
                
                
        else:
            pass
        



def boot_2(choose_on):
    choose_on2 = 0 # wlan处的选择变量

    kin = 1 # 参数的选择变量
    while True:
        
        if shift.value() == 0:
            break
        oled.line(0,13,64,13,1)
        #网络
        if choose_on == 1:
            oled.fill(0)
            oled.line(0,13,64,13,1)
            params = [
                (fn.wlan1_s, 0, 0), (fn.wang_s, 14, 0), (fn.luo_s, 30, 0),
                (fn.ming_s, 10, 17), (fn.cheng_s, 22, 17), (fn.mi_s, 10, 29),
                (fn.ma_s, 22, 29), (fn.di2_s, 10, 41), (fn.zhi2_s, 22, 41),
                (fn.duan2_s, 10, 53), (fn.kou2_s, 22, 53), (fn.que1_s, 100, 1),
                (fn.ren1_s, 112, 1)
            ] 

            # 遍历参数列表，对每个元素调用 oled_12_s
            for data_123, x, y in params:
                fn.oled_12_s(data_123, x, y, 1, oled)
            oled.text(fn.wlan_SSID,47,19)
            oled.text(fn.wlan_PASS,47,31)
            oled.text(fn.wlan_IPCI,47,43)
            oled.text(fn.wlan_PORT,47,55)
            

            # 按键选择
            if up.value()*down.value()*right.value()*left.value() == 0:
                time.sleep_ms(100)
                if up.value()*down.value()*right.value()*left.value() == 0:
                    choose_on2 += 1
                    if choose_on2 >= 6:
                        choose_on2 = 1
            
            # 绘制账号密码框与选项
            if choose_on2 == 1:
                fn.square_s(46,18,80,10,oled)
            elif choose_on2 == 2:
                fn.square_s(46,30,80,10,oled)
            elif choose_on2 == 3:
                fn.square_s(46,42,80,10,oled)
            elif choose_on2 == 4:
                fn.square_s(46,54,80,10,oled)
            else:
                fn.square_s(99,0,26,14,oled)
            # 进入账号密码设置界面
            if confirm.value()==0:
                oled.fill(0)
                oled.show()
                time.sleep_ms(400)
                if choose_on2 == 1:
                    fn.wlan_SSID=boot_3(fn.wlan_SSID)
                elif choose_on2 == 2:
                    fn.wlan_PASS=boot_3(fn.wlan_PASS)
                elif choose_on2 == 3:
                    fn.wlan_IPCI=boot_3(fn.wlan_IPCI)
                elif choose_on2 == 4:
                    fn.wlan_PORT=boot_3(fn.wlan_PORT)
                else:
                    font.wlansave[9] = [fn.wlan_SSID, fn.wlan_PASS] # 保存账号和密码，运行时匹配
                    
                    
        #参数
        if choose_on == 2:
            fn.oled_12_s(fn.canshu_icon_s,0,0,1,oled)
            fn.oled_12_s(fn.can_s,14,0,1,oled)
            fn.oled_12_s(fn.shu_s,30,0,1,oled)
            fn.limit(oled)


        # 这里的在choose.py内  


        #功能
        if choose_on == 3:
            fn.limit(oled)
           
           # import fm
           # fn.oled_12_s(fn.gongneng_icon_s,0,0,1,oled)
           # fn.oled_12_s(fn.gong_s,14,0,1,oled)
           # fn.oled_12_s(fm.neng_s,30,0,1,oled)         
           # fn.oled_12_s(fm.lv_s,10,17,1,oled)
           # fn.oled_12_s(fm.bo_s,22,17,1,oled)  
           # fn.oled_12_s(fm.bao_s,74,17,1,oled)
           # fn.oled_12_s(fm.jing_s,86,17,1,oled)    
           # fn.oled_12_s(fm.sheng_s,10,37,1,oled)
           # fn.oled_12_s(fm.dian_s,22,37,1,oled)
           # fn.oled_12_s(fm.kong_s,74,37,1,oled)
           # fn.oled_12_s(fm.zhi_s,86,37,1,oled)
           
            
        #关于
        if choose_on == 4:
            import fm
            fn.version(oled)
            oled.text(fm.ID,46,22)
        oled.show()
        time.sleep_ms(200)

# 执行修改变更
def boot_3(STR_S):
    choose_3 = 1 # 定义选择参数变量
    grout = True  # 定义标识符变量
    STR_Ssave = STR_S
    while True:
        if shift.value() == 0:
            STR_S = STR_Ssave # 不执行更改
            oled.fill(0)
            break
        # 绘制界面
        oled.fill(0)
        oled.text(STR_S,8,0)
        oled.line(0,10,64,10,1)
        
        fn.keyboard(oled)
        fn.oled_12_s(fn.chexiao_s,114,38,1,oled)
        fn.oled_12_s(fn.queren_s,114,50,1,oled)
        if grout==True:
            oled.fill_rect(8*len(STR_S)+8,0,1,8,1)
        else:
            oled.fill_rect(8*len(STR_S)+8,0,1,8,0)
        grout = not grout
        # 选择判断
        if up.value() == 0:
            time.sleep_ms(100)
            if up.value() == 1:
                choose_3 -= 12
                
        if down.value() == 0:
            time.sleep_ms(100)
            if down.value() == 1:
                choose_3 += 12
                
        if left.value() == 0:
            time.sleep_ms(100)
            if left.value() == 1:
                choose_3 -= 1
                
        if right.value() == 0:
            time.sleep_ms(100)
            if right.value() == 1:
                choose_3 += 1
        #判断数值意义
        if choose_3 <= 0:
            choose_3 += 48
        if choose_3 >= 51:
            choose_3 -= 48
            
        #绘制选择的字符
        if choose_3==49:
            fn.square_s(113,37,14,14,oled)
        elif choose_3==50:    
            fn.square_s(113,49,14,14,oled)
        else:
            raw_3 = (choose_3 - 1) // 12 + 1
            hei_3 = (choose_3 - 1) % 12 + 1          
            fn.square_s((hei_3-1)*8,(raw_3-1)*13+12,8,10,oled)
            
        #确认将选择字符键入
        if confirm.value() == 0:
            time.sleep_ms(100)
            if confirm.value() == 1:
                if choose_3 <= 48 and choose_3 >= 1:
                    num_to_char = {v: k for k, v in fn.char_to_num.items()} # 定义键值
                    add_key = num_to_char.get(choose_3, "?")
                    print(add_key)
                    STR_S = STR_S+add_key
                elif choose_3==49:
                    STR_S = STR_S[:len(STR_S)-1]
                elif choose_3==50:
                    oled.fill(0)
                    break
            else:
                time.sleep_ms(200)
                if choose_3 <= 48 and choose_3 >= 1:
                    num_to_char2 = {v: k for k, v in fn.char_to_num_min.items()} # 定义小写键值
                    add_key2 = num_to_char2.get(choose_3, "?")
                    print(add_key2)
                    STR_S = STR_S+add_key2
                elif choose_3==49:
                    STR_S = STR_S[:len(STR_S)-1]
                elif choose_3==50:
                    oled.fill(0)
                    break
                
        time.sleep_ms(100)
        oled.show()
        
        
    return STR_S
turn = 0
#执行总循环
while True:

    boot_1()  # 菜单判断函数
    turn+=1
    if turn>=3:
        turn=1
    if not wlan.isconnected():
        Pin(5,Pin.IN)
        WLAN = 0
        log.warning("WLAN未连接")

        fn.oled_12_s(fn.wlan0_s,104,0,1,oled)

        oled.show()
        WIFI_Connect()
        if wlan.isconnected():
            Pin(5,Pin.OUT)
    else:
        Pin(5,Pin.OUT)
        WLAN = 1
        log.debug("WLAN已连接")
        
        
        
        fn.oled_12_s(fn.wlan1_s,104,0,1,oled)
        oled.show()
    ############################################################################
    #初始化socket通信

    ##############################################################
    if WLAN == 1:
        
        fn.oled_12_s(fn.wlan1_s,104,0,1,oled)
        oled.show()
        
        log.info("读取数据。。")
        
        try:
            ds.convert_temp()
            if rom == [] :
                rom = ds.scan()
            temp = ds.read_temp(rom[0])
            try:
                temp1 = ds.read_temp(rom[1])
            except Exception as e:
                print(e)
                temp1 = temp
            #log.info("DS18B20采集成功")
        except Exception as e:
            print(e)
            temp  = 0
            temp1 = temp
            log.error("DS18B20异常")
        #温度显示,rom[0]为第1个DS18B20
        
        
        
        #通道9,10,11,12
        try: #异常处理
            dt.measure()         #温湿度采集
            te=dt.temperature()  #获取温度值
            dh=dt.humidity()     #获取湿度值
            #温度显示

        except Exception as e: #异常提示

            log.error(e)#'DHT11 超时'

        if (abs(temp-temp1)+abs(te-temp1)+abs(te-temp))/3>=3:
            log.debug("温度计异常")
        else: 
            #log.info("温度计正常")
            pass
        temp=(temp1 + temp +te)/3
        # 温度显示
        BMP_temp = BMP.getTemp()
        print('芯片温度：'+str(BMP_temp) + ' °C  ',end="")
        log.debug("芯片温度正常")
        # 压强显示
        BMP_press = BMP.getPress()/1000
        # 海拔显示
        BMP_read = float(BMP.getAltitude())
        print('海拔:'+str(BMP_read) + ' m')
        log.debug("海拔正常")
        #输出
        
        #通道1,2,3,4
        ain0, ain1, ain2, ain3 = pcf8591.analog_read_all()
        ain1 = ain1 /256 *15000
        ain2=ain2 * (-91/160) + (157 * 161 /160)
        A_get = (ain0 /256 * 5/10000)*1000 + function.inc_r()
        U_get = ain0  /256  * 5
        W_get= A_get * U_get + function.inc_r()
        ain3 = ain3/256 *5
        #print("仪表电流:", '%.3f'%A_get, "mA 光照强度:", '%1.f'%ain1, "lux 热敏电阻:", '%.2f'%ain2, "°C 芯片电压:", '%.2f'%ain3,"V")
        #log.debug("仪表电流正常")
        #log.debug("光照强度正常")
        #log.debug("热敏电阻正常")
        #log.debug("芯片电压正常")
        #log.debug("1234通道正常")
        # 121 -27.5°   111-33.1875
        # k = -91/160 b = 96*163/160
        
        
        #电池判断
        if ain3>=3:
            fn.oled_12_s(fn.battery2_s,116,0,1,oled)
        elif 3>=ain3 and ain3>=2:
            fn.oled_12_s(fn.battery1_s,116,0,1,oled)
        else:
            fn.oled_12_s(fn.battery0_s,116,0,1,oled)
        #
        
        #通道5，6,7,8
        #print("环境温度："+str('%.2f'%temp),end=" ")
        #log.debug("环境温度正常")
        #print("°C 环境湿度："+str(dh),end=" ")
        #log.debug("环境湿度正常")
        #print("% 大气压强："+str(BMP_press),end=" ")
        #log.debug("大气压强正常")
        #print("kPa 仪表功率："+str('%.3f'%W_get)+'W')
        #log.debug("仪表功率正常")
        log.debug("5678通道正常")
        
        oled.fill_rect(0,14,128,50,0)
        if turn==1:
            oled.text(str('%.2f'%temp)+'C',0,16) #显示温度,保留2位小数 
            oled.text(str('%.1f'%dh)+' %',0,24) #显示湿度,保留1位小数 
            oled.text(str('%.3f'%BMP_press)+'mPa',0,32) #显示压力,保留3位小数 
            oled.text(str('%.3f'%W_get)+' W',0,40) #显示功率   
            oled.text(str('%.3f'%A_get)+' mA',0,48) #显示电流，保留3位小数
            oled.text(str('%.2f'%(ain3/3.6*100))+'%',0,56) #显示电量,保留2位小数
        if turn==2:
            oled.text(str('%.1f'%ain1)+'Lux',0,16) #显示光照,保留1位小数 
            oled.text(str('%.2f'%ain2)+'C',0,24) #显示温度,保留2位小数 
            oled.text(str('%.2f'%ain3)+' V',0,32) #显示电压,保留2位小数 
            oled.text(str('%.1f'%BMP_read)+' m',0,40) #显示海拔,保留1位小数
            oled.text(str('%.2f'%BMP_temp)+'C',0,48) #显示温度,保留2位小数 
            #oled.text(str('%.2f'%temp)+' C',0,40) #保留通道
        oled.show()
        log.debug(wlan.ifconfig())
        log.info("发送数据中！")
        # 数据处理：
        BMP_read=BMP_read+100 #跳过负值
        # 状态参数打包：
        S_con = (int(PID_f) << 9 | int(LIN_f) << 8 | int(alarm_f) << 7 | int(filter_f) << 6 | int(filter_A) << 5 |
         int(filter_middle) << 4 | int(filter_average) << 3 | int(H) << 2 | int(battery_save) << 1 | int(J))
        
        
        log.info("连接到服务器。。。")
        fn.oled_12_s(fn.chuanshu_s,92,0,1,oled)
        oled.show()
        try:
            s=usocket.socket()
            s.settimeout(25)
            addr=(fn.wlan_IPCI,int(fn.wlan_PORT)) #服务器IP和端口
            s.connect(addr)
            log.info("已连接,正在向服务器发送数据：")
            try:
                
                # 定义一个紧凑的格式化字符串，减少不必要的文本和格式化操作
                format_str = "-ID-{0}T{1:.2f}H{2:.1f}BP{3:.3f}W{4}A{5:.3f}L{6:.1f}R{7:.2f}V{8:.2f}E{9:.1f}CT{10:.2f}P{11:.2f}I{12:.2f}D{13:.2f}S{14:.2f}"
                compact_data = format_str.format(ID, temp, dh, BMP_press, W_get, A_get, ain1, ain2, ain3, BMP_read, BMP_temp, P, I, D, S_con)
                compact_data = compact_data.encode('utf-8')
                # 加密并发送数据
                s.send(aes.aes_encode(message=compact_data))
                #日志封装
                log.info("日志发送成功")
                for item in log.messages:
                    #print(item)
                    #s.send("-"+str(item)+"-")
                    time.sleep_ms(20)
                    s.send(aes.aes_encode(message="-"+str(item)+"-"))
                #s.send("-_-") #结束标志位
                #清除日志 
                log.messages=[]
                log.info("发送成功")
            except Exception as e:
                print(e)
                log.error("发送失败")
            # s.close()
            wdt.feed()
            log.debug("到达复位")
            socket_link = 1
        except Exception as e:
            print(e)
            # 如果上面的代码块引发异常，则执行此处的代码
            log.warning("服务器异常,跳过数据发送")
            socket_link = 0
        
        fn.oled_12_s(fn.chuanshu1_s,92,0,1,oled)
        #oled.line(124,14,124,22,1)
        oled.show()

        #创建socket连接TCP类似，连接成功后发送数据给服务器
        
        if socket_link == 1:
            try:
                log.info("接收数据")
                text = s.recv(128)  
                log.info(" 接收完成")
                if not text:  # 检查是否接收到空字节串
                    log.warning("连接关闭，无接收。")
                    s.close()  # 关闭 socket
                    
                else:
                    # 处理接收到的数据
                    receive = text.decode('utf-8')
                    print(receive)
                    print(gc.mem_free())
                    fn.oled_12_s(fn.chuanshu2_s,92,0,1,oled)
                    oled.show()
                    
                    # 将接收的参数存储到仪表
                    try:
                        P=float(re.search(r"-P_f=(\d+\.\d+)",receive).group(1))
                        I=float(re.search(r"-I_f=(\d+\.\d+)",receive).group(1))
                        D=float(re.search(r"-D_f=(\d+\.\d+)",receive).group(1))
                        S=int(float(re.search(r"-S_f=(\d+\.\d+)",receive).group(1)))
                        PID_f, LIN_f, alarm_f, filter_f, filter_A, filter_middle, filter_average,H, battery_save, J= bool(S & (1 << 9)), bool(S & (1 << 8)), bool(S & (1 << 7)), bool(S & (1 << 6)), bool(S & (1 << 5)), bool(S & (1 << 4)), bool(S & (1 << 3)), bool(S & (1 << 2)), bool(S & (1 << 1)), bool(S & 1)
                        log.info("布尔参数："+str(S)+"A:"+str(alarm_f))
                        # 将接收的参数存储到仪表
                        data_to_save = {
                                        'ID': ID,
                                        'P': P,
                                        'I': I,
                                        'D': D,
                                        'S': S
                                        }
                        save_params_to_rtc(data_to_save)
                        
                    except:
                        log.error("参数匹配失败")
                    s.close()

            except OSError as e:
                log.error("错误代码:"+str(e)+"socket接收异常")
                s.close()  # 在发生异常时关闭 socket
        
        
        if socket_link == 1:
            
            #开启RTOS定时器，编号为-1,周期300ms，执行控制通道参数控制
            tim = Timer(-1)
            tim.init(period=3000, mode=Timer.PERIODIC,callback=Socket_fun)
                
               
        if not wlan.isconnected():
            WLAN = 0
        
        time.sleep_ms(200)
        oled.fill_rect(92,0,12,12,0)
        oled.show()
    wdt.feed()
    log.info("进入休眠 ")
    gc.collect()
    for i in range(0,5):
        oled.line(127,i*6+14,127,i*6+19,1)
        oled.line(126,i*6+14,126,i*6+19,1)
        oled.show()
        time.sleep_ms(1000)
    log.info("休眠解除")
    #################################################################







