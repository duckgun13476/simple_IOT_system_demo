from ex4nicegui import to_ref, ref_computed
from dashboard.lib.log_color import log


class StrDef:
    Panel1_alarm_1_h = to_ref(40)
    Panel1_alarm_1_l = to_ref(15)
    Panel1_alarm_2_h = to_ref(150)
    Panel1_alarm_2_l = to_ref(10)
    Panel1_alarm_3_h = to_ref(100)
    Panel1_alarm_3_l = to_ref(30)
    Panel1_alarm_4_h = to_ref(1)
    Panel1_alarm_4_l = to_ref(0.2)
    Panel1_alarm_5_h = to_ref(15000)
    Panel1_alarm_5_l = to_ref(5)
    Panel1_alarm_6_h = to_ref(1)
    Panel1_alarm_6_l = to_ref(0)
    Panel1_alarm_7_h = to_ref(108)
    Panel1_alarm_7_l = to_ref(5)
    Panel1_alarm_8_h = to_ref(80)
    Panel1_alarm_8_l = to_ref(5)
    Panel1_alarm_9_h = to_ref(5)
    Panel1_alarm_9_l = to_ref(2)
    Panel1_alarm_10_h = to_ref(800)
    Panel1_alarm_10_l = to_ref(-900)
    Panel1_alarm_11_h = to_ref(115)
    Panel1_alarm_11_l = to_ref(5)
    Panel1_alarm_12_h = to_ref(100)
    Panel1_alarm_12_l = to_ref(0)

    Panel2_alarm_1_h = to_ref(40)
    Panel2_alarm_1_l = to_ref(15)
    Panel2_alarm_2_h = to_ref(150)
    Panel2_alarm_2_l = to_ref(10)
    Panel2_alarm_3_h = to_ref(100)
    Panel2_alarm_3_l = to_ref(30)
    Panel2_alarm_4_h = to_ref(1)
    Panel2_alarm_4_l = to_ref(0.2)
    Panel2_alarm_5_h = to_ref(15000)
    Panel2_alarm_5_l = to_ref(5)
    Panel2_alarm_6_h = to_ref(1)
    Panel2_alarm_6_l = to_ref(0)
    Panel2_alarm_7_h = to_ref(108)
    Panel2_alarm_7_l = to_ref(5)
    Panel2_alarm_8_h = to_ref(80)
    Panel2_alarm_8_l = to_ref(5)
    Panel2_alarm_9_h = to_ref(5)
    Panel2_alarm_9_l = to_ref(2)
    Panel2_alarm_10_h = to_ref(800)
    Panel2_alarm_10_l = to_ref(-900)
    Panel2_alarm_11_h = to_ref(115)
    Panel2_alarm_11_l = to_ref(5)
    Panel2_alarm_12_h = to_ref(100)
    Panel2_alarm_12_l = to_ref(0)

    Panel3_alarm_1_h = to_ref(40)
    Panel3_alarm_1_l = to_ref(15)
    Panel3_alarm_2_h = to_ref(150)
    Panel3_alarm_2_l = to_ref(10)
    Panel3_alarm_3_h = to_ref(100)
    Panel3_alarm_3_l = to_ref(30)
    Panel3_alarm_4_h = to_ref(1)
    Panel3_alarm_4_l = to_ref(0.2)
    Panel3_alarm_5_h = to_ref(15000)
    Panel3_alarm_5_l = to_ref(5)
    Panel3_alarm_6_h = to_ref(1)
    Panel3_alarm_6_l = to_ref(0)
    Panel3_alarm_7_h = to_ref(108)
    Panel3_alarm_7_l = to_ref(5)
    Panel3_alarm_8_h = to_ref(80)
    Panel3_alarm_8_l = to_ref(5)
    Panel3_alarm_9_h = to_ref(5)
    Panel3_alarm_9_l = to_ref(2)
    Panel3_alarm_10_h = to_ref(800)
    Panel3_alarm_10_l = to_ref(-900)
    Panel3_alarm_11_h = to_ref(115)
    Panel3_alarm_11_l = to_ref(5)
    Panel3_alarm_12_h = to_ref(100)
    Panel3_alarm_12_l = to_ref(0)

    content1 = to_ref('')
    content2 = to_ref('')
    content3 = to_ref('')
    ues_checkbox = to_ref(True)

    user_name = to_ref('')
    password = to_ref('')

    level_1 = 0

    panel1_1_visibility = to_ref(False)
    panel1_2_visibility = to_ref(False)  # 控制算法面板1的三个绑定算法可见性
    panel1_3_visibility = to_ref(False)

    panel2_1_visibility = to_ref(False)
    panel2_2_visibility = to_ref(False)  # 控制算法面板2的三个绑定算法可见性
    panel2_3_visibility = to_ref(False)

    panel3_1_visibility = to_ref(False)
    panel3_2_visibility = to_ref(False)  # 控制算法面板3的三个绑定算法可见性
    panel3_3_visibility = to_ref(False)

    select_value = to_ref('')
    select_value_2 = to_ref('')
    select_value_3 = to_ref('')

    Panel1_P = to_ref(1)
    Panel1_I = to_ref(1)  # pid 三个系数，面板1
    Panel1_D = to_ref(1)

    Panel2_P = to_ref(1)
    Panel2_I = to_ref(1)  # pid 三个系数，面板2
    Panel2_D = to_ref(1)

    Panel3_P = to_ref(1)
    Panel3_I = to_ref(1)  # pid 三个系数，面板3
    Panel3_D = to_ref(1)

    control_stat = to_ref(False)  # 控制算法面板1启动变量
    control_stat_2 = to_ref(False)  # 控制算法面板2启动变量
    control_stat_3 = to_ref(False)  # 控制算法面板3启动变量

    Panel1_k = to_ref(1)
    Panel1_b = to_ref(0)  # 线性算法 两系数，面板1
    Panel2_k = to_ref(1)
    Panel2_b = to_ref(0)  # 线性算法 两系数，面板2
    Panel3_k = to_ref(1)
    Panel3_b = to_ref(0)  # 线性算法 两系数，面板3

    rewrite_notify = to_ref(False)
    rewrite_notify_2 = to_ref(False)
    rewrite_notify_3 = to_ref(False)

    # 1
    alarm_state = to_ref(True)  # 报警启动变量
    filter_state_f = to_ref(True)
    filter_state_v = to_ref(False)  # 滤波算法的启用变量
    filter_state_m = to_ref(False)
    battery_low_state = to_ref(False)  # 低耗电模式启动
    mult_state = to_ref(True)
    log_state = to_ref(False)  # 传输是否打印日志
    # 2
    alarm_state_2 = to_ref(True)  # 报警启动变量
    filter_state_f_2 = to_ref(True)
    filter_state_v_2 = to_ref(False)  # 滤波算法的启用变量
    filter_state_m_2 = to_ref(False)
    battery_low_state_2 = to_ref(False)  # 低耗电模式启动
    mult_state_2 = to_ref(True)
    log_state_2 = to_ref(False)  # 传输是否打印日志
    # 3
    alarm_state_3 = to_ref(True)  # 报警启动变量
    filter_state_f_3 = to_ref(True)
    filter_state_v_3 = to_ref(False)  # 滤波算法的启用变量
    filter_state_m_3 = to_ref(False)
    battery_low_state_3 = to_ref(False)  # 低耗电模式启动
    mult_state_3 = to_ref(True)
    log_state_3 = to_ref(False)  # 传输是否打印日志

    log_print_state = to_ref(False)  # 面板是否更新日志
    log_print_state_2 = to_ref(False)  # 面板是否更新日志
    log_print_state_3 = to_ref(False)  # 面板是否更新日志

    number_update_state = to_ref(True)
    number_update_state_2 = to_ref(True)
    number_update_state_3 = to_ref(True)

    auto_update = to_ref(True)

    data_calculate_1 = to_ref(True)
    data_calculate_2 = to_ref(True)
    data_calculate_3 = to_ref(True)

    report_input = to_ref('')
    report_in_change= to_ref(True)
    report_in_alarm = to_ref(False)
    report_in_advice = to_ref(False)

    report_p_input = to_ref('')
    report_p_in_change= to_ref(False)
    report_p_in_alarm = to_ref(False)
    report_p_in_advice = to_ref(True)


@ref_computed()
def visitable_1():  # 算法部分的面板可见性函数
    log.debug("visitable被调用")
    if StrDef.control_stat:
        if StrDef.select_value.value == 1:
            StrDef.panel1_1_visibility.value = True
            StrDef.panel1_2_visibility.value = False
            StrDef.panel1_3_visibility.value = False
        elif StrDef.select_value.value == 2:
            StrDef.panel1_1_visibility.value = False
            StrDef.panel1_2_visibility.value = True
            StrDef.panel1_3_visibility.value = False
        elif StrDef.select_value.value == 3:
            StrDef.panel1_1_visibility.value = False
            StrDef.panel1_2_visibility.value = False
            StrDef.panel1_3_visibility.value = True


@ref_computed()
def visitable_2():  # 算法部分的面板可见性函数
    log.debug("visitable被调用")
    if StrDef.control_stat_2:
        if StrDef.select_value_2.value == 1:
            StrDef.panel2_1_visibility.value = True
            StrDef.panel2_2_visibility.value = False
            StrDef.panel2_3_visibility.value = False
        elif StrDef.select_value_2.value == 2:
            StrDef.panel2_1_visibility.value = False
            StrDef.panel2_2_visibility.value = True
            StrDef.panel2_3_visibility.value = False
        elif StrDef.select_value_2.value == 3:
            StrDef.panel2_1_visibility.value = False
            StrDef.panel2_2_visibility.value = False
            StrDef.panel2_3_visibility.value = True


@ref_computed()
def visitable_3():  # 算法部分的面板可见性函数
    log.debug("visitable被调用")
    if StrDef.control_stat_3:
        if StrDef.select_value_3.value == 1:
            StrDef.panel3_1_visibility.value = True
            StrDef.panel3_2_visibility.value = False
            StrDef.panel3_3_visibility.value = False
        elif StrDef.select_value_3.value == 2:
            StrDef.panel3_1_visibility.value = False
            StrDef.panel3_2_visibility.value = True
            StrDef.panel3_3_visibility.value = False
        elif StrDef.select_value_3.value == 3:
            StrDef.panel3_1_visibility.value = False
            StrDef.panel3_2_visibility.value = False
            StrDef.panel3_3_visibility.value = True


@ref_computed()
def pid_show():  # PID部分的反馈函数
    log.debug("pid_show被调用")
    if StrDef.Panel1_P.value or StrDef.Panel1_I.value or StrDef.Panel1_D.value:
        return str(f'更改：P ') + str(StrDef.Panel1_P.value) + str(f' I ') + str(StrDef.Panel1_I.value) + str(
            f' D ') + str(StrDef.Panel1_D.value)


@ref_computed()
def pid_show_2():  # PID部分的反馈函数
    log.debug("pid_show被调用")
    if StrDef.Panel2_P.value or StrDef.Panel2_I.value or StrDef.Panel2_D.value:
        return str(f'更改：P ') + str(StrDef.Panel2_P.value) + str(f' I ') + str(StrDef.Panel2_I.value) + str(
            f' D ') + str(StrDef.Panel2_D.value)


@ref_computed()
def pid_show_3():  # PID部分的反馈函数
    log.debug("pid_show被调用")
    if StrDef.Panel3_P.value or StrDef.Panel3_I.value or StrDef.Panel3_D.value:
        return str(f'更改：P ') + str(StrDef.Panel3_P.value) + str(f' I ') + str(StrDef.Panel3_I.value) + str(
            f' D ') + str(StrDef.Panel3_D.value)


@ref_computed()
def kb_show():  # PID部分的反馈函数
    log.info("kb_show被调用")
    if StrDef.Panel1_k.value or StrDef.Panel1_b.value:
        return str(f'更改：k ') + str(StrDef.Panel1_k.value) + str(f' b ') + str(StrDef.Panel1_b.value)


@ref_computed()
def kb_show_2():  # PID部分的反馈函数
    log.info("kb_show_2被调用")
    if StrDef.Panel2_k.value or StrDef.Panel2_b.value:
        return str(f'更改：k ') + str(StrDef.Panel2_k.value) + str(f' b ') + str(StrDef.Panel2_b.value)


@ref_computed()
def kb_show_3():  # PID部分的反馈函数
    log.info("kb_show_3被调用")
    if StrDef.Panel3_k.value or StrDef.Panel3_b.value:
        return str(f'更改：k ') + str(StrDef.Panel3_k.value) + str(f' b ') + str(StrDef.Panel3_b.value)


if __name__ == '__main__':
    log.warning("这是一个class文件")
