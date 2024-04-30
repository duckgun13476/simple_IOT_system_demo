import datetime
import enum
import os
import threading
import time
from random import random
from typing import Annotated
from api_get import get_report
import numpy as np
import plotly.graph_objects as go
import psutil
from ex4nicegui import rxui
from ex4nicegui.reactive import rxui
from fastapi import Depends
from nicegui import ui, app, run
from plotly.basedatatypes import BaseTraceType
from pydantic import BaseModel
from picture_find import find_newest_file
from bin.data_update_choose import update_data
from bin.dataread import get_latest_data
from bin.log_read import fetch_latest_logs
from bin.minio_read import read_bucket_size
from bin.socket_thread import socket_listen
from email_alarm import send_email
from variables.model_board import calculate_temperature_change, extract_different_neighbours
from lib.log_color import log
from lib.ping_t import ping
from variables.class_1 import StrDef, visitable_1, visitable_2, visitable_3
from variables.class_1 import pid_show, kb_show, pid_show_2, kb_show_2, pid_show_3, kb_show_3
from cv_read_minio_save import read_camera_and_upload
# from api_picture import picture_api_analy
from dashboard.variables.variable import Var

###########################################
picture = ui.image()
battery1, battery2, battery3 = 100.0, 100.0, 100.0


# from niceguiToolkit.layout import inject_layout_tool
###############################################################
# 定义列表来存储报错信息
class ContentManager:
    def __init__(self):
        self.content = ""
        self.insert_count = 0
        self.last_insert = ""

    def insert_string(self, string_to_insert):
        self.content += string_to_insert + "\n"
        self.insert_count += 1
        self.last_insert = string_to_insert

    def print_content(self):
        print(self.content)
        return self.content

    def clear_content(self):
        self.content = ""
        self.insert_count = 0
        self.last_insert = ""

    def get_insert_count(self):
        return self.insert_count

    def get_last_insert(self):
        return self.last_insert


# 创建 ContentManager 实例
manager = ContentManager()

manager.insert_string("警报信息")


# 插入字符串到内容中  manager.insert_string("Hello, ")

# 打印内容  manager.print_content()

# 获取插入次数  manager.get_insert_count()

# 清空内容  manager.clear_content()
# 得到最后一次警报内容  manager.get_last_insert()
###############################################################
class LoginRequired(Exception):
    pass


class InsufficientPermissions(Exception):
    pass


class Config:
    from_attributes = True  # Updated from 'orm_mode'
    frozen = True  # So they can be JSON Serialized to local files.


class Role(enum.IntFlag):
    """Oversimplified permissions/role structure."""

    StandardUser = enum.auto()
    Moderator = enum.auto()
    Admin = enum.auto()


class User(BaseModel):
    name: str
    role: Role = Role.StandardUser

    def to_dict(self):
        return {"name": self.name, "role": self.role.value}

    @classmethod
    def from_dict(cls, data):
        return cls(name=data["name"], role=Role(data["role"]))

    class Config:
        from_attributes = True
        frozen = True


# 用户权限
users = {
    1: User(name="管理员", role=Role.Admin),
    2: User(name="高级用户", role=Role.Moderator),
    3: User(name="标准用户", role=Role.StandardUser),
}


async def login(user_id: int) -> None:
    if user := users.get(user_id):
        app.storage.user["user"] = user.to_dict()  # 使用 to_dict 方法
        ui.notify(f"现在以 {user.name} 登入", type="positive")
    else:
        app.storage.user.pop("user", None)
        ui.notify("已登出", type="warning")


async def current_authenticated_user() -> User:
    user_dict = app.storage.user.get("user")
    if user_dict is None:
        raise LoginRequired("此页面需要登录")
    return User.from_dict(user_dict)


async def current_admin_user(
        user: Annotated[User, Depends(current_authenticated_user)]
):
    """A dependency relying on another for verifying admin permissions."""

    if user.role == Role.Admin:
        return user
    raise InsufficientPermissions("需要管理员账号.")


#################
input1 = rxui.input()
input2 = rxui.input()

# 从环境变量读取配置，如果环境变量不存在，则使用默认值
USER_NAME = os.getenv('USER_NAME', '1234')
USER_PASSWORD = os.getenv('USER_PASSWORD', '1234')
PANEL_IP = os.getenv('PANEL_IP', 'localhost')

print(USER_NAME, USER_PASSWORD)


async def on_log():
    global input1, input2
    # print(label1.text())
    value1 = StrDef.user_name.value
    value2 = StrDef.password.value
    if value1 == USER_NAME:
        if value2 == USER_NAME:

            ui.notify("登录成功")
            try:
                StrDef.level_1 = 3
                print(StrDef.level_1)
                await login(1)
            except Exception as e:
                print(e)

            def redirect():
                ui.notify('跳转中')
                ui.open("/control/board")

            print('定时器设置为3秒')
            ui.timer(3, redirect, once=True)

        else:
            pass
    elif value1 == "12345":
        if value2 == "12345":

            ui.notify("登录成功")
            try:
                StrDef.level_1 = 2
                print(StrDef.level_1)
                await login(2)
            except Exception as e:
                print(e)

            def redirect():
                ui.notify('跳转中')
                ui.open("/control/board")

            print('定时器设置为3秒')
            ui.timer(3, redirect, once=True)
        else:
            pass
    elif value1 == "123456":
        if value2 == "123456":

            ui.notify("登录成功")
            try:
                StrDef.level_1 = 1
                print(StrDef.level_1)
                await login(3)
            except Exception as e:
                print(e)

            def redirect():
                ui.notify('跳转中')
                ui.open("/control/board")

            print('定时器设置为3秒')
            ui.timer(3, redirect, once=True)

        else:
            pass
    else:
        ui.notify("账号或密码错误")
        print(value1, value2)
        # login(0)
    print("wa", value1, "wb", value2)


#################


@ui.page("/login")
async def home_page():
    global img, label1, input1, input2, link1, link2, button1
    # log ui
    img = ui.image('bin/scene.jpg').props("absolute-top text-center").tailwind('h-screen')
    with ui.label('').classes("absolute top-1/4 inset-x-1/3 w-1/3 rounded bg-slate-300 shadow-2xl bg-white opacity-80"):
        with ui.grid().style("font-size:0.8rem"):
            label1 = ui.label('欢迎访问！').tailwind("text-center text-2xl text-dark my-2")
            input1 = rxui.input('账号/邮箱', value=StrDef.user_name).props("outlined").style(
                'color: rgb(37 99 235);padding-left: 2.5rem;padding-right: 2.5rem;')
            input2 = rxui.input('密码', password=True, value=StrDef.password).props("outlined").style(
                'padding-left: 2.5rem;padding-right: 2.5rem;')

            with ui.row().style('gap:12em;font-size:1.4rem'):
                link1 = ui.link('忘记密码').tailwind('ml-10 w-1/3 text-left')
                link2 = ui.link('注册账号').tailwind('ml-9 text-right')
                # 单个空间用mx
            with ui.row().style("flex-direction:column;gap:0rem"):
                with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                    with ui.row():
                        button1 = ui.button('登录', on_click=on_log).style('width: 145px; ')
                        ui.label(" ")

                        async def log_out_2():
                            StrDef.level_1 = 0
                            try:
                                await login(0)
                            except Exception as e:
                                log.error(e)

                        ui.button("登出", on_click=lambda: log_out_2()).style('width: 145px; ')
    with ui.column().classes("w-2/3 p-8 self-center items-center"):
        # ui.label("使用按钮切换不同用户").classes("text-h4")
        # with ui.row():

        # ui.button("标准用户 Sally", on_click=lambda: login(3))
        # ui.button("高级用户 Mark", on_click=lambda: login(2))
        # ui.button("管理员 Andy", on_click=lambda: login(1))
        ui.label("尝试直接访问？").classes("text-h4")
        with ui.row():
            ui.button("标准页面", on_click=lambda: ui.open("/portal"))
            ui.button("高级用户页面", on_click=lambda: ui.open("/moderation"))
            ui.button("管理员页面", on_click=lambda: ui.open("/admin"))


@ui.page("/portal")
async def user_portal(user: Annotated[User, Depends(current_authenticated_user)]):
    """Accessible to all authenticated users"""
    ui.label("欢迎来到公开页面!")
    ui.button("返回主菜单", on_click=lambda: ui.open("/login"))


@ui.page("/moderation")
async def moderator_dashboard(
        user: Annotated[User, Depends(current_authenticated_user)]
):
    """Example of allowing user but differing page content based on role."""
    if user.role >= Role.Moderator:
        ui.label("欢迎来到高级用户界面!")
        ui.button("返回主菜单", on_click=lambda: ui.open("/login"))
    else:
        ui.label("你似乎不是高级用户, 你还要在这里发呆嘛?")
        ui.button("返回主菜单", on_click=lambda: ui.open("/login"))


@ui.page("/admin")
async def admin_center(user: Annotated[User, Depends(current_admin_user)]):
    ui.label("欢迎来到管理员用户界面!")
    ui.button("返回主菜单", on_click=lambda: ui.open("/login"))


def renews():
    while True:
        new_late = find_newest_file()
        picture.set_source('http://192.168.147.107:9500/usedfor-s-three-test/' + str(new_late))
        time.sleep(3)
        print("update")


###########################################


# from niceguiToolkit.layout import inject_layout_tool
try:
    loaded_arr2 = np.load('arr.npy')
except Exception as e:
    print(e)
    arr_set = np.random.randint(20, 21, size=(31, 33, 6))
    np.save('arr.npy', arr_set)

# 创建一个函数用于映射温度到颜色


# print(loaded_arr)
temperature_colors = [
    "#053061",  # 极低温
    "#0B4083",
    "#1555A5",
    "#1F6BC7",
    "#297FE9",
    "#3288BD",
    "#3991C3",
    "#439AC9",
    "#4DA3CF",
    "#57ACD5",
    "#77B7D7",  # 较低温
    "#97C2D9",
    "#B7CDDC",
    "#D7D8DE",
    "#F7E3E0",  # 温和
    "#F3C2C9",
    "#EF9FB2",
    "#EB7C9B",
    "#E75984",
    "#E3366D",  # 较高温
    "#DF1356",
    "#D90040",
    "#C10038",
    "#A90030",
    "#910022"  # 极高温
]

# inject_layout_tool()
# 多线程指令↓
socket_style = None
line_name = [" 环境温度 ", " 大气压强 ", " 环境湿度 ", " 仪表电流 ", " 光照强度 ",
             " 仪表功率 ", " 芯片温度 ", " 热敏电阻 ", " 芯片电压 ", " 海拔高度 ",
             " 电池电量 ", " 输出通道 ", ]
receive_01 = False
receive_02 = False
receive_03 = False
ping_result = -1
latest_logs = []
latest_logs_2 = []
latest_logs_3 = []

data_panel_1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
data_panel_2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
data_panel_3 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

data_panel_1_1 = []
data_panel_2_1 = []
data_panel_3_1 = []

turnual = 0
bucket_size_show = ui.label("null")
bucket_name_show = ui.label("null")
panel_read = ui.label("null")
thread_number = ui.label("null")
listen_update = ui.label("null")
label_state = ui.label("null")
data_read_1 = ui.label("null")

camera_read = ui.label('null')

scene = ui.scene()
moved_01 = scene.box()
method_select = rxui.select({1: 'PID', 2: '线性', 3: 'DPC'})
mult_1 = rxui.switch()

conf_check3 = ui.checkbox()
conf_check3_2 = ui.checkbox()
conf_check3_3 = ui.checkbox()

header = ui.header()

conf_check2 = ui.checkbox()
conf_check2_2 = ui.checkbox()
conf_check2_3 = ui.checkbox()

logs_1 = ui.log()
logs_2 = ui.log()
logs_3 = ui.log()

k_th01 = 0
m_th01 = 0
click_1_1 = False
next_x_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
next_x_values_2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
next_x_values_3 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


@ui.refreshable
def panel_alarm(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def model_report_show(content):
    ui.markdown(content)


@ui.refreshable
def model_report_show_p(content):
    ui.markdown(content)


###########################
# 1
@ui.refreshable
def panel_1_temp(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_1_wet_1(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_1_pres(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_1_output(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_1_power(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_1_battery(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_1_panel_A(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_1_light(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_1_temp_core(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_1_core_voltage(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_1_chip_temp(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_1_high(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_ID_1(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


###########################
# 2
@ui.refreshable
def panel_2_temp(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_2_wet_2(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_2_pres(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_2_output(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_2_power(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_2_battery(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_2_panel_A(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_2_light(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_2_temp_core(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_2_core_voltage(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_2_chip_temp(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_2_high(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_ID_2(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


###########################
# 3
@ui.refreshable
def panel_3_temp(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_3_wet_3(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_3_pres(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_3_output(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_3_power(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_3_battery(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_3_panel_A(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_3_light(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_3_temp_core(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_3_core_voltage(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_3_chip_temp(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_3_high(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def panel_id_3(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


###########################

@ui.refreshable
def runtime(content):
    ui.label(content).style("align-self:flex-start;font-size:0.8rem")


@ui.refreshable
def connect_second(content):
    ui.label(content)


@ui.refreshable
def step_simu(content):
    ui.label(content)


# # 历史数据图表
k = 12  # 假设有3个通道
m = 10  # 每条曲线的最大点数

fig = go.Figure()
fig.add_trace(go.Scatter(x=[], y=[], visible=False))
for i in range(k):
    name = line_name[i] if i < len(line_name) else f"通道 {i + 1}"
    fig.add_trace(go.Scatter(x=[], y=[], visible=False, name=name))
plot = ui.plotly(fig)
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
conf_check1 = ui.checkbox()

fig_2 = go.Figure()
fig_2.add_trace(go.Scatter(x=[], y=[], visible=False))
for i in range(k):
    name_2 = line_name[i] if i < len(line_name) else f"通道 {i + 1}"
    fig_2.add_trace(go.Scatter(x=[], y=[], visible=False, name=name_2))
plot_2 = ui.plotly(fig_2)
fig_2.update_layout(margin=dict(l=0, r=0, t=0, b=0))
conf_check1_2 = ui.checkbox()

fig_3 = go.Figure()
fig_3.add_trace(go.Scatter(x=[], y=[], visible=False))
for i in range(k):
    name_3 = line_name[i] if i < len(line_name) else f"通道 {i + 1}"
    fig_3.add_trace(go.Scatter(x=[], y=[], visible=False, name=name_3))
plot_3 = ui.plotly(fig_3)
fig_3.update_layout(margin=dict(l=0, r=0, t=0, b=0))
conf_check1_3 = ui.checkbox()

x = None
y = None


# #更新minio的文件大小
def read_bucket_size_f():  # 更新minio的文件大小
    while True:
        try:
            bucket_size, bucket_name = read_bucket_size()
            if bucket_size is not None:
                bucket_size_show.set_text(f"存储桶已使用： {bucket_size} ")  # 这里放指令
                bucket_name_show.set_text(f"存储桶名：{bucket_name}")
        except Exception as e:
            log.error(f"读取存储发生错误: {e}")
        time.sleep(5)  # 更新频率，这里设置为每3秒更新一次


# #更新仪表的参数
def panel_read_f():  # 更新仪表的参数
    global receive_01, data_panel_1, battery1, battery2, battery3
    ID_read = 0
    ID_read_2 = 0
    ID_read_3 = 0
    # 插入字符串到内容中  manager.insert_string("Hello, ")

    # 打印内容  manager.print_content()

    # 获取插入次数  manager.get_insert_count()

    # 清空内容  manager.clear_content()
    # 得到最后一次警报内容  manager.get_last_insert()
    while True:
        global data_panel_1, data_panel_2, data_panel_3
        print("更新仪表")
        data_panel_1, data_panel_2, data_panel_3 = get_latest_data('TILGF87080', 'TILGF37102', 'TILGF41238')
        print("更新完毕")
        if data_panel_1 is not None:
            log.info(f"{ID_read}<{data_panel_1[0]}")
            if ID_read < data_panel_1[0]:
                receive_01 = True
                ID_read = data_panel_1[0]
            panel_read.set_text(f"仪表数据正常 ")  # 这里放指令
            panel_1_temp.refresh(f'{data_panel_1[1]:.2f}°C')
            panel_1_wet_1.refresh(f'{data_panel_1[2]} %')
            panel_1_pres.refresh(f'{data_panel_1[3]:.2f}mPa')
            panel_1_power.refresh(f'{data_panel_1[4]} W')
            panel_1_panel_A.refresh(f"{data_panel_1[11]}mA")
            panel_1_light.refresh(f'{data_panel_1[12]:.1f} Lux')
            panel_1_temp_core.refresh(f'{data_panel_1[14]}°C')
            panel_1_core_voltage.refresh(f'{data_panel_1[13]} V')
            panel_1_chip_temp.refresh(f'{data_panel_1[18]}°C')
            panel_1_high.refresh(f'{data_panel_1[15]}m')
            panel_ID_1.refresh(f"{data_panel_1[16]}")
            battery1 = (3.7 / float(data_panel_1[13])) * 100
            panel_1_battery.refresh(f"{battery1:.2f}")
            data_read_1.set_text("数据库可访问")

            if data_panel_1[1] >= StrDef.Panel1_alarm_1_h.value:
                log.warning(
                    f"高温警报：实际温度：{data_panel_1[1]},"
                    f"温度上限：{StrDef.Panel1_alarm_1_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1高温警报：实际温度：{data_panel_1[1]},"
                    f"温度上限：{StrDef.Panel1_alarm_1_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_1[1] <= StrDef.Panel1_alarm_1_l.value:
                log.warning(
                    f"低温警报：实际温度：{data_panel_1[1]},"
                    f"温度下限：{StrDef.Panel1_alarm_1_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1低温警报：实际温度：{data_panel_1[1]},"
                    f"温度下限：{StrDef.Panel1_alarm_1_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_1[2] >= StrDef.Panel1_alarm_2_h.value:
                log.warning(
                    f"高湿度警报：实际湿度：{data_panel_1[2]},"
                    f"湿度上限：{StrDef.Panel1_alarm_2_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1高湿度警报：实际温度：{data_panel_1[2]},"
                    f"湿度上限：{StrDef.Panel1_alarm_2_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_1[2] <= StrDef.Panel1_alarm_2_l.value:
                log.warning(
                    f"低湿度警报：实际湿度：{data_panel_1[1]},"
                    f"湿度下限：{StrDef.Panel1_alarm_2_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1低湿度警报：实际湿度：{data_panel_1[2]},"
                    f"湿度下限：{StrDef.Panel1_alarm_2_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_1[3] >= StrDef.Panel1_alarm_3_h.value:
                log.warning(
                    f"高压警报：实际压力：{data_panel_1[3]},"
                    f"压力上限：{StrDef.Panel1_alarm_3_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1高压警报：实际压力：{data_panel_1[3]},"
                    f"压力上限：{StrDef.Panel1_alarm_3_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_1[3] <= StrDef.Panel1_alarm_3_l.value:
                log.warning(
                    f"低压警报：实际压力：{data_panel_1[3]},"
                    f"压力下限：{StrDef.Panel1_alarm_3_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1低压警报：实际压力：{data_panel_1[3]},"
                    f"压力下限：{StrDef.Panel1_alarm_3_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_1[4] >= StrDef.Panel1_alarm_4_h.value:
                log.warning(
                    f"高电流警报：实际电流：{data_panel_1[4]},"
                    f"电流上限：{StrDef.Panel1_alarm_4_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1高电流警报：实际电流：{data_panel_1[4]},"
                    f"电流上限：{StrDef.Panel1_alarm_4_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_1[4] <= StrDef.Panel1_alarm_4_l.value:
                log.warning(
                    f"低电流警报：实际电流：{data_panel_1[4]},"
                    f"电流下限：{StrDef.Panel1_alarm_4_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1低电流警报：实际电流：{data_panel_1[4]},"
                    f"电流下限：{StrDef.Panel1_alarm_4_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_1[12] >= StrDef.Panel1_alarm_5_h.value:
                log.warning(
                    f"高光度警报：实际光强：{data_panel_1[12]},"
                    f"光强上限：{StrDef.Panel1_alarm_5_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1高光度警报：实际光强：{data_panel_1[12]},"
                    f"光强上限：{StrDef.Panel1_alarm_5_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_1[12] <= StrDef.Panel1_alarm_5_l.value:
                log.warning(
                    f"低光度警报：实际光强：{data_panel_1[12]},"
                    f"光强下限：{StrDef.Panel1_alarm_5_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1低光度警报：实际光强：{data_panel_1[12]},"
                    f"光强下限：{StrDef.Panel1_alarm_5_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_1[11] >= StrDef.Panel1_alarm_6_h.value:
                log.warning(
                    f"高功率警报：实际功率：{data_panel_1[11]},"
                    f"功率上限：{StrDef.Panel1_alarm_6_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1高功率警报：实际功率：{data_panel_1[11]},"
                    f"功率上限：{StrDef.Panel1_alarm_6_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_1[11] <= StrDef.Panel1_alarm_6_l.value:
                log.warning(
                    f"低功率警报：实际功率：{data_panel_1[11]},"
                    f"功率下限：{StrDef.Panel1_alarm_6_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1低功率警报：实际功率：{data_panel_1[11]},功率下限："
                    f"{StrDef.Panel1_alarm_6_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_1[14] >= StrDef.Panel1_alarm_7_h.value:
                log.warning(
                    f"芯片过热警报：实际温度：{data_panel_1[14]},"
                    f"温度上限：{StrDef.Panel1_alarm_7_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1芯片过热警报：实际温度：{data_panel_1[14]},"
                    f"温度上限：{StrDef.Panel1_alarm_7_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_1[14] <= StrDef.Panel1_alarm_7_l.value:
                log.warning(
                    f"芯片过冷警报：实际温度：{data_panel_1[14]},"
                    f"温度下限：{StrDef.Panel1_alarm_7_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1芯片过冷警报：实际温度：{data_panel_1[14]},"
                    f"温度下限：{StrDef.Panel1_alarm_7_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_1[18] >= StrDef.Panel1_alarm_8_h.value:
                log.warning(
                    f"热敏电阻高温警报：实际温度：{data_panel_1[18]},"
                    f"温度上限：{StrDef.Panel1_alarm_8_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1热敏电阻高温警报：实际温度：{data_panel_1[18]},"
                    f"温度上限：{StrDef.Panel1_alarm_8_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_1[18] <= StrDef.Panel1_alarm_8_l.value:
                log.warning(
                    f"热敏电阻低温警报：实际温度：{data_panel_1[18]},"
                    f"温度下限：{StrDef.Panel1_alarm_8_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1热敏电阻低温警报：实际温度：{data_panel_1[18]},"
                    f"温度下限：{StrDef.Panel1_alarm_8_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_1[13] >= StrDef.Panel1_alarm_9_h.value:
                log.warning(
                    f"仪表高电压警报：实际电压：{data_panel_1[13]},"
                    f"电压上限：{StrDef.Panel1_alarm_9_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1仪表高电压警报：实际电压：{data_panel_1[13]},"
                    f"电压上限：{StrDef.Panel1_alarm_9_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_1[13] <= StrDef.Panel1_alarm_9_l.value:
                log.warning(
                    f"仪表低电压警报：实际电压：{data_panel_1[13]},"
                    f"电压下限：{StrDef.Panel1_alarm_9_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1仪表低电压警报：实际电压：{data_panel_1[13]},"
                    f"电压下限：{StrDef.Panel1_alarm_9_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_1[15] >= StrDef.Panel1_alarm_10_h.value:
                log.warning(
                    f"高海拔警报：实际海拔：{data_panel_1[15]},"
                    f"海拔上限：{StrDef.Panel1_alarm_10_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1高海拔警报：实际海拔：{data_panel_1[15]},"
                    f"海拔上限：{StrDef.Panel1_alarm_10_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_1[15] <= StrDef.Panel1_alarm_10_l.value:
                log.warning(
                    f"低海拔警报：实际海拔：{data_panel_1[15]},"
                    f"海拔下限：{StrDef.Panel1_alarm_10_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1低海拔警报：实际海拔：{data_panel_1[15]},"
                    f"海拔下限：{StrDef.Panel1_alarm_10_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if battery1 >= StrDef.Panel1_alarm_11_h.value:
                log.warning(
                    f"电池过充警报：实际电量：{battery1:.2f},"
                    f"电量上限：{StrDef.Panel1_alarm_11_h.value:.2f},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1电池过充警报：实际电量：{battery1:.2f},"
                    f"电量上限：{StrDef.Panel1_alarm_11_h.value:.2f},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif battery1 <= StrDef.Panel1_alarm_11_l.value:
                log.warning(
                    f"低电量警报：实际电量：{battery1:.2f},"
                    f"电量下限：{StrDef.Panel1_alarm_11_l.value:.2f},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表1低电量警报：实际电量：{battery1:.2f},"
                    f"电量下限：{StrDef.Panel1_alarm_11_l.value:.2f},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            # else:
            # panel_alarm.refresh("无警报")
            # if data_panel_1[12] >= StrDef.Panel1_alarm_12_h.value:
            #    log.warning(f"通道上限警报：实际数值：{data_panel_1[12]},数值上限：{StrDef.Panel1_alarm_12_h.value},时间：{datetime.datetime.now()}")
            #    manager.insert_string(f"通道上限警报：实际数值：{data_panel_1[12]},数值上限：{StrDef.Panel1_alarm_12_h.value},时间：{datetime.datetime.now()}")
            #    panel_alarm.refresh(manager.get_last_insert())
            # elif data_panel_1[12] <= StrDef.Panel1_alarm_12_l.value:
            #    log.warning(f"通道下限警报：实际数值：{data_panel_1[12]},数值下限：{StrDef.Panel1_alarm_12_l.value},时间：{datetime.datetime.now()}")
            #    manager.insert_string(f"通道下限警报：实际数值：{data_panel_1[12]},数值下限：{StrDef.Panel1_alarm_12_l.value},时间：{datetime.datetime.now()}")
            #    panel_alarm.refresh(manager.get_last_insert())
        else:
            panel_read.set_text(f"读取数据失败 ")
        if data_panel_2 is not None:
            log.info(f"{ID_read_2}<{data_panel_2[0]}")
            if ID_read_2 < data_panel_2[0]:
                receive_01 = True
                ID_read_2 = data_panel_2[0]
            panel_read.set_text(f"仪表数据正常 ")  # 这里放指令
            panel_2_temp.refresh(f'{data_panel_2[1]:.2f}°C')
            panel_2_wet_2.refresh(f'{data_panel_2[2]} %')
            panel_2_pres.refresh(f'{data_panel_2[3]:.2f}mPa')
            panel_2_power.refresh(f'{data_panel_2[4]} W')
            panel_2_panel_A.refresh(f"{data_panel_2[11]}mA")
            panel_2_light.refresh(f'{data_panel_2[12]:.1f} Lux')
            panel_2_temp_core.refresh(f'{data_panel_2[14]}°C')
            panel_2_core_voltage.refresh(f'{data_panel_2[13]} V')
            panel_2_chip_temp.refresh(f'{data_panel_2[18]}°C')
            panel_2_high.refresh(f'{data_panel_2[15]}m')
            panel_ID_2.refresh(f"{data_panel_2[16]}")
            battery2 = 3.7 / float(data_panel_2[13]) * 100
            panel_2_battery.refresh(f"{battery2:.2f}")
            data_read_1.set_text("数据库可访问")

            if data_panel_2[1] >= StrDef.Panel2_alarm_1_h.value:
                log.warning(
                    f"高温警报：实际温度：{data_panel_2[1]},"
                    f"温度上限：{StrDef.Panel2_alarm_1_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2高温警报：实际温度：{data_panel_2[1]},"
                    f"温度上限：{StrDef.Panel2_alarm_1_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_2[1] <= StrDef.Panel2_alarm_1_l.value:
                log.warning(
                    f"低温警报：实际温度：{data_panel_2[1]},"
                    f"温度下限：{StrDef.Panel2_alarm_1_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2低温警报：实际温度：{data_panel_2[1]},"
                    f"温度下限：{StrDef.Panel2_alarm_1_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_2[2] >= StrDef.Panel2_alarm_2_h.value:
                log.warning(
                    f"高湿度警报：实际湿度：{data_panel_2[2]},"
                    f"湿度上限：{StrDef.Panel2_alarm_2_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2高湿度警报：实际温度：{data_panel_2[2]},"
                    f"湿度上限：{StrDef.Panel2_alarm_2_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_2[2] <= StrDef.Panel2_alarm_2_l.value:
                log.warning(
                    f"低湿度警报：实际湿度：{data_panel_2[1]},湿度下限：{StrDef.Panel2_alarm_2_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2低湿度警报：实际湿度：{data_panel_2[2]},"
                    f"湿度下限：{StrDef.Panel2_alarm_2_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_2[3] >= StrDef.Panel2_alarm_3_h.value:
                log.warning(
                    f"高压警报：实际压力：{data_panel_2[3]},"
                    f"压力上限：{StrDef.Panel2_alarm_3_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2高压警报：实际压力：{data_panel_2[3]},"
                    f"压力上限：{StrDef.Panel2_alarm_3_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_2[3] <= StrDef.Panel2_alarm_3_l.value:
                log.warning(
                    f"低压警报：实际压力：{data_panel_2[3]},"
                    f"压力下限：{StrDef.Panel2_alarm_3_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2低压警报：实际压力：{data_panel_2[3]},"
                    f"压力下限：{StrDef.Panel2_alarm_3_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_2[4] >= StrDef.Panel2_alarm_4_h.value:
                log.warning(
                    f"高电流警报：实际电流：{data_panel_2[4]},"
                    f"电流上限：{StrDef.Panel2_alarm_4_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2高电流警报：实际电流：{data_panel_2[4]},"
                    f"电流上限：{StrDef.Panel2_alarm_4_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_2[4] <= StrDef.Panel2_alarm_4_l.value:
                log.warning(
                    f"低电流警报：实际电流：{data_panel_2[4]},"
                    f"电流下限：{StrDef.Panel2_alarm_4_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2低电流警报：实际电流：{data_panel_2[4]},"
                    f"电流下限：{StrDef.Panel2_alarm_4_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_2[12] >= StrDef.Panel2_alarm_5_h.value:
                log.warning(
                    f"高光度警报：实际光强：{data_panel_2[12]},"
                    f"光强上限：{StrDef.Panel2_alarm_5_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2高光度警报：实际光强：{data_panel_2[12]},"
                    f"光强上限：{StrDef.Panel2_alarm_5_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_2[12] <= StrDef.Panel2_alarm_5_l.value:
                log.warning(
                    f"低光度警报：实际光强：{data_panel_2[12]},"
                    f"光强下限：{StrDef.Panel2_alarm_5_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2低光度警报：实际光强：{data_panel_2[12]},"
                    f"光强下限：{StrDef.Panel2_alarm_5_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_2[11] >= StrDef.Panel2_alarm_6_h.value:
                log.warning(
                    f"高功率警报：实际功率：{data_panel_2[11]},"
                    f"功率上限：{StrDef.Panel2_alarm_6_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2高功率警报：实际功率：{data_panel_2[11]},"
                    f"功率上限：{StrDef.Panel2_alarm_6_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_2[11] <= StrDef.Panel2_alarm_6_l.value:
                log.warning(
                    f"低功率警报：实际功率：{data_panel_2[11]},"
                    f"功率下限：{StrDef.Panel2_alarm_6_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2低功率警报：实际功率：{data_panel_2[11]},"
                    f"功率下限：{StrDef.Panel2_alarm_6_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_2[14] >= StrDef.Panel2_alarm_7_h.value:
                log.warning(
                    f"芯片过热警报：实际温度：{data_panel_2[14]},"
                    f"温度上限：{StrDef.Panel2_alarm_7_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2芯片过热警报：实际温度：{data_panel_2[14]},"
                    f"温度上限：{StrDef.Panel2_alarm_7_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_2[14] <= StrDef.Panel2_alarm_7_l.value:
                log.warning(
                    f"芯片过冷警报：实际温度：{data_panel_2[14]},"
                    f"温度下限：{StrDef.Panel2_alarm_7_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2芯片过冷警报：实际温度：{data_panel_2[14]},"
                    f"温度下限：{StrDef.Panel2_alarm_7_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_2[18] >= StrDef.Panel2_alarm_8_h.value:
                log.warning(
                    f"热敏电阻高温警报：实际温度：{data_panel_2[18]},"
                    f"温度上限：{StrDef.Panel2_alarm_8_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2热敏电阻高温警报：实际温度：{data_panel_2[18]},"
                    f"温度上限：{StrDef.Panel2_alarm_8_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_2[18] <= StrDef.Panel2_alarm_8_l.value:
                log.warning(
                    f"热敏电阻低温警报：实际温度：{data_panel_2[18]},"
                    f"温度下限：{StrDef.Panel2_alarm_8_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2热敏电阻低温警报：实际温度：{data_panel_2[18]},"
                    f"温度下限：{StrDef.Panel2_alarm_8_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_2[13] >= StrDef.Panel2_alarm_9_h.value:
                log.warning(
                    f"仪表高电压警报：实际电压：{data_panel_2[13]},"
                    f"电压上限：{StrDef.Panel2_alarm_9_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2仪表高电压警报：实际电压：{data_panel_2[13]},"
                    f"电压上限：{StrDef.Panel2_alarm_9_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_2[13] <= StrDef.Panel2_alarm_9_l.value:
                log.warning(
                    f"仪表低电压警报：实际电压：{data_panel_2[13]},"
                    f"电压下限：{StrDef.Panel2_alarm_9_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2仪表低电压警报：实际电压：{data_panel_2[13]},"
                    f"电压下限：{StrDef.Panel2_alarm_9_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_2[15] >= StrDef.Panel2_alarm_10_h.value:
                log.warning(
                    f"高海拔警报：实际海拔：{data_panel_2[15]},"
                    f"海拔上限：{StrDef.Panel2_alarm_10_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2高海拔警报：实际海拔：{data_panel_2[15]},"
                    f"海拔上限：{StrDef.Panel2_alarm_10_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_2[15] <= StrDef.Panel2_alarm_10_l.value:
                log.warning(
                    f"低海拔警报：实际海拔：{data_panel_2[15]},"
                    f"海拔下限：{StrDef.Panel2_alarm_10_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2低海拔警报：实际海拔：{data_panel_2[15]},"
                    f"海拔下限：{StrDef.Panel2_alarm_10_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if battery2 >= StrDef.Panel2_alarm_11_h.value:
                log.warning(
                    f"电池过充警报：实际电量：{battery2:.2f},"
                    f"电量上限：{StrDef.Panel2_alarm_11_h.value:.2f},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2电池过充警报：实际电量：{battery2:.2f},"
                    f"电量上限：{StrDef.Panel2_alarm_11_h.value:.2f},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif battery2 <= StrDef.Panel2_alarm_11_l.value:
                log.warning(
                    f"低电量警报：实际电量：{battery2:.2f},"
                    f"电量下限：{StrDef.Panel2_alarm_11_l.value:.2f},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表2低电量警报：实际电量：{battery2:.2f},"
                    f"电量下限：{StrDef.Panel2_alarm_11_l.value:.2f},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            # else:
            # panel_alarm.refresh("无警报")
            # if data_panel_1[12] >= StrDef.Panel1_alarm_12_h.value:
            #    log.warning(f"通道上限警报：实际数值：{data_panel_1[12]},数值上限：{StrDef.Panel1_alarm_12_h.value},时间：{datetime.datetime.now()}")
            #    manager.insert_string(f"通道上限警报：实际数值：{data_panel_1[12]},数值上限：{StrDef.Panel1_alarm_12_h.value},时间：{datetime.datetime.now()}")
            #    panel_alarm.refresh(manager.get_last_insert())
            # elif data_panel_1[12] <= StrDef.Panel1_alarm_12_l.value:
            #    log.warning(f"通道下限警报：实际数值：{data_panel_1[12]},数值下限：{StrDef.Panel1_alarm_12_l.value},时间：{datetime.datetime.now()}")
            #    manager.insert_string(f"通道下限警报：实际数值：{data_panel_1[12]},数值下限：{StrDef.Panel1_alarm_12_l.value},时间：{datetime.datetime.now()}")
            #    panel_alarm.refresh(manager.get_last_insert())
        else:
            panel_read.set_text(f"读取数据失败 ")
        if data_panel_3 is not None:
            log.info(f"{ID_read_3}<{data_panel_3[0]}")
            if ID_read_3 < data_panel_3[0]:
                receive_01 = True
                ID_read_3 = data_panel_3[0]
            panel_read.set_text(f"仪表数据正常 ")  # 这里放指令
            panel_3_temp.refresh(f'{data_panel_3[1]:.2f}°C')
            panel_3_wet_3.refresh(f'{data_panel_3[2]} %')
            panel_3_pres.refresh(f'{data_panel_3[3]:.2f}mPa')
            panel_3_power.refresh(f'{data_panel_3[4]} W')
            panel_3_panel_A.refresh(f"{data_panel_3[11]}mA")
            panel_3_light.refresh(f'{data_panel_3[12]:.1f} Lux')
            panel_3_temp_core.refresh(f'{data_panel_3[14]}°C')
            panel_3_core_voltage.refresh(f'{data_panel_3[13]} V')
            panel_3_chip_temp.refresh(f'{data_panel_3[18]}°C')
            panel_3_high.refresh(f'{data_panel_3[15]}m')
            panel_id_3.refresh(f"{data_panel_3[16]}")
            battery3 = 3.7 / float(data_panel_3[13]) * 100
            panel_3_battery.refresh(f"{battery3:.2f}")
            data_read_1.set_text("数据库可访问")

            if data_panel_3[1] >= StrDef.Panel3_alarm_1_h.value:
                log.warning(
                    f"高温警报：实际温度：{data_panel_3[1]},温度上限：{StrDef.Panel3_alarm_1_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3高温警报：实际温度：{data_panel_3[1]},温度上限：{StrDef.Panel3_alarm_1_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_3[1] <= StrDef.Panel3_alarm_1_l.value:
                log.warning(
                    f"低温警报：实际温度：{data_panel_3[1]},温度下限：{StrDef.Panel3_alarm_1_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3低温警报：实际温度：{data_panel_3[1]},温度下限：{StrDef.Panel3_alarm_1_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_3[2] >= StrDef.Panel3_alarm_2_h.value:
                log.warning(
                    f"高湿度警报：实际湿度：{data_panel_3[2]},湿度上限：{StrDef.Panel3_alarm_2_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3高湿度警报：实际温度：{data_panel_3[2]},湿度上限：{StrDef.Panel3_alarm_2_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_3[2] <= StrDef.Panel3_alarm_2_l.value:
                log.warning(
                    f"低湿度警报：实际湿度：{data_panel_3[1]},湿度下限：{StrDef.Panel3_alarm_2_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3低湿度警报：实际湿度：{data_panel_3[2]},湿度下限：{StrDef.Panel3_alarm_2_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_3[3] >= StrDef.Panel3_alarm_3_h.value:
                log.warning(
                    f"高压警报：实际压力：{data_panel_3[3]},压力上限：{StrDef.Panel3_alarm_3_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3高压警报：实际压力：{data_panel_3[3]},压力上限：{StrDef.Panel3_alarm_3_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_3[3] <= StrDef.Panel3_alarm_3_l.value:
                log.warning(
                    f"低压警报：实际压力：{data_panel_3[3]},压力下限：{StrDef.Panel3_alarm_3_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3低压警报：实际压力：{data_panel_3[3]},压力下限：{StrDef.Panel3_alarm_3_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_3[4] >= StrDef.Panel3_alarm_4_h.value:
                log.warning(
                    f"高电流警报：实际电流：{data_panel_3[4]},电流上限：{StrDef.Panel3_alarm_4_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3高电流警报：实际电流：{data_panel_3[4]},电流上限：{StrDef.Panel3_alarm_4_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_3[4] <= StrDef.Panel3_alarm_4_l.value:
                log.warning(
                    f"低电流警报：实际电流：{data_panel_3[4]},电流下限：{StrDef.Panel3_alarm_4_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3低电流警报：实际电流：{data_panel_3[4]},电流下限：{StrDef.Panel3_alarm_4_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_3[12] >= StrDef.Panel3_alarm_5_h.value:
                log.warning(
                    f"高光度警报：实际光强：{data_panel_3[12]},光强上限：{StrDef.Panel3_alarm_5_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3高光度警报：实际光强：{data_panel_3[12]},光强上限：{StrDef.Panel3_alarm_5_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_3[12] <= StrDef.Panel3_alarm_5_l.value:
                log.warning(
                    f"低光度警报：实际光强：{data_panel_3[12]},光强下限：{StrDef.Panel3_alarm_5_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3低光度警报：实际光强：{data_panel_3[12]},光强下限：{StrDef.Panel3_alarm_5_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_3[11] >= StrDef.Panel3_alarm_6_h.value:
                log.warning(
                    f"高功率警报：实际功率：{data_panel_3[11]},功率上限：{StrDef.Panel3_alarm_6_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3高功率警报：实际功率：{data_panel_3[11]},功率上限：{StrDef.Panel3_alarm_6_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_3[11] <= StrDef.Panel3_alarm_6_l.value:
                log.warning(
                    f"低功率警报：实际功率：{data_panel_3[11]},功率下限：{StrDef.Panel3_alarm_6_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3低功率警报：实际功率：{data_panel_3[11]},功率下限：{StrDef.Panel3_alarm_6_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_3[14] >= StrDef.Panel3_alarm_7_h.value:
                log.warning(
                    f"芯片过热警报：实际温度：{data_panel_3[14]},温度上限：{StrDef.Panel3_alarm_7_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3芯片过热警报：实际温度：{data_panel_3[14]},温度上限：{StrDef.Panel3_alarm_7_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_3[14] <= StrDef.Panel3_alarm_7_l.value:
                log.warning(
                    f"芯片过冷警报：实际温度：{data_panel_3[14]},温度下限：{StrDef.Panel3_alarm_7_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3芯片过冷警报：实际温度：{data_panel_3[14]},温度下限：{StrDef.Panel3_alarm_7_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_3[18] >= StrDef.Panel3_alarm_8_h.value:
                log.warning(
                    f"热敏电阻高温警报：实际温度：{data_panel_3[18]},温度上限：{StrDef.Panel3_alarm_8_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3热敏电阻高温警报：实际温度：{data_panel_3[18]},温度上限：{StrDef.Panel3_alarm_8_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_3[18] <= StrDef.Panel3_alarm_8_l.value:
                log.warning(
                    f"热敏电阻低温警报：实际温度：{data_panel_3[18]},温度下限：{StrDef.Panel3_alarm_8_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3热敏电阻低温警报：实际温度：{data_panel_3[18]},温度下限：{StrDef.Panel3_alarm_8_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_3[13] >= StrDef.Panel3_alarm_9_h.value:
                log.warning(
                    f"仪表高电压警报：实际电压：{data_panel_3[13]},电压上限：{StrDef.Panel3_alarm_9_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3仪表高电压警报：实际电压：{data_panel_3[13]},电压上限：{StrDef.Panel3_alarm_9_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_3[13] <= StrDef.Panel3_alarm_9_l.value:
                log.warning(
                    f"仪表低电压警报：实际电压：{data_panel_3[13]},电压下限：{StrDef.Panel3_alarm_9_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3仪表低电压警报：实际电压：{data_panel_3[13]},电压下限：{StrDef.Panel3_alarm_9_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if data_panel_3[15] >= StrDef.Panel3_alarm_10_h.value:
                log.warning(
                    f"高海拔警报：实际海拔：{data_panel_3[15]},海拔上限：{StrDef.Panel3_alarm_10_h.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3高海拔警报：实际海拔：{data_panel_3[15]},海拔上限：{StrDef.Panel3_alarm_10_h.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif data_panel_3[15] <= StrDef.Panel3_alarm_10_l.value:
                log.warning(
                    f"低海拔警报：实际海拔：{data_panel_3[15]},海拔下限：{StrDef.Panel3_alarm_10_l.value},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3低海拔警报：实际海拔：{data_panel_3[15]},海拔下限：{StrDef.Panel3_alarm_10_l.value},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())

            if battery3 >= StrDef.Panel3_alarm_11_h.value:
                log.warning(
                    f"电池过充警报：实际电量：{battery3:.2f},电量上限：{StrDef.Panel3_alarm_11_h.value:.2f},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3电池过充警报：实际电量：{battery3:.2f},电量上限：{StrDef.Panel3_alarm_11_h.value:.2f},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            elif battery3 <= StrDef.Panel3_alarm_11_l.value:
                log.warning(
                    f"低电量警报：实际电量：{battery3:.2f},电量下限：{StrDef.Panel3_alarm_11_l.value:.2f},时间：{datetime.datetime.now()}")
                manager.insert_string(
                    f"仪表3低电量警报：实际电量：{battery3:.2f},电量下限：{StrDef.Panel3_alarm_11_l.value:.2f},时间：{datetime.datetime.now()}")
                panel_alarm.refresh(manager.get_last_insert())
            # else:
            # panel_alarm.refresh("无警报")
            # if data_panel_1[12] >= StrDef.Panel1_alarm_12_h.value:
            #    log.warning(f"通道上限警报：实际数值：{data_panel_1[12]},数值上限：{StrDef.Panel1_alarm_12_h.value},时间：{datetime.datetime.now()}")
            #    manager.insert_string(f"通道上限警报：实际数值：{data_panel_1[12]},数值上限：{StrDef.Panel1_alarm_12_h.value},时间：{datetime.datetime.now()}")
            #    panel_alarm.refresh(manager.get_last_insert())
            # elif data_panel_1[12] <= StrDef.Panel1_alarm_12_l.value:
            #    log.warning(f"通道下限警报：实际数值：{data_panel_1[12]},数值下限：{StrDef.Panel1_alarm_12_l.value},时间：{datetime.datetime.now()}")
            #    manager.insert_string(f"通道下限警报：实际数值：{data_panel_1[12]},数值下限：{StrDef.Panel1_alarm_12_l.value},时间：{datetime.datetime.now()}")
            #    panel_alarm.refresh(manager.get_last_insert())
        else:
            panel_read.set_text(f"读取数据失败 ")
        log.info(manager.get_insert_count())
        if manager.get_insert_count() >= 10:
            subject = '[来自智能检测终端V1.1]'
            manager.print_content()
            body = '警报，检测到部分通道数据异常，内容如下：\n' + str(manager.print_content()) + "\n如果不是重要警报，请忽视"
            manager.clear_content()
            threading.Thread(target=send_email, args=(subject, body, '2980168906@qq.com')).start()

        time.sleep(15)  # 更新频率，这里设置为每15秒更新一次
        # log.info(f"当前活跃线程数: {threading.active_count()}")
        # 打印内容  manager.print_content()

        # 获取插入次数  manager.get_insert_count()


# #线程检测
def thread_number_read():  # 线程检测
    while True:
        thread_number_now = threading.active_count()
        time.sleep(0.5)
        thread_number_later = threading.active_count()
        time.sleep(0.5)
        if thread_number_later != thread_number_now:
            log.info(f"当前活跃线程数: {threading.active_count()}")
        thread_number.set_text(f"当前活跃线程数: {threading.active_count()}")
        # 获取当前脚本的进程ID
        pid = os.getpid()
        # 通过进程ID获取进程对象
        process = psutil.Process(pid)
        # 使用进程对象获取内存信息
        memory_info = process.memory_info()

        # 打印内存使用信息
        log.info(f"物理内存: {memory_info.rss / 1024 ** 2:.2f} MB 虚拟内存: {memory_info.vms / 1024 ** 2:.2f} MB")


# #仪表监听程序
def listen_update_f():
    global socket_style
    while True:
        time.sleep(10)
        log.info(f'监听服务已启动')
        try:
            socket_style = True
            socket_listen()
        except Exception as e:
            socket_style = False
            log.error(f"监听服务发生错误: {e}")
            log.warning(f'监听服务终止，将重新启动')
            listen_update.set_text(f'监听服务将重新启动')


# #系统时钟
def system_clock():
    global receive_01
    record_second = 0
    day = 0
    hour = 0
    minute = 0
    sec = 0
    while True:
        try:
            time.sleep(0.5)
            record_second += 1
            if record_second <= 60:
                connect_second.refresh(f'{record_second}s 前')
            elif record_second > 60:

                record_se = record_second % 60
                record_minute = int((record_second - record_se) / 60)
                connect_second.refresh(f'{record_minute}min{record_se}s 前')
            if 20 >= record_second >= 0:
                label_state.set_text("正常")
            elif 60 >= record_second >= 20:
                label_state.set_text("信号不佳")
            elif 120 >= record_second >= 60:
                label_state.set_text("仪表超时")
            elif record_second >= 120:
                label_state.set_text("仪表断开")
            sec += 1
            if sec >= 60:
                sec = 0
                minute += 1
            if minute >= 60:
                minute = 0
                hour += 1
            if hour >= 24:
                day += 1
                hour = 0
            runtime.refresh(f" {day}天 {hour} 小时 {minute} 分钟 {sec} 秒")
            time.sleep(0.5)
            if receive_01:
                receive_01 = False
                record_second = 0
            # 仪表日志更新
        except Exception as e:
            log.error(f"系统时钟错误！{e}")


def get_ping_result():
    global ping_result
    server_test1 = Var.ping_server
    ping_result = ping(server_test1)


def update_log_panel():
    global latest_logs
    latest_logs = fetch_latest_logs(100, logs_123="logs_1")
    logs_1.clear()
    for i_282 in range(1, 100):
        logs_1.push(latest_logs[100 - i_282])
        time.sleep(0.2)


def update_log_panel_2():
    global latest_logs_2
    latest_logs_2 = fetch_latest_logs(100, logs_123="logs_2")
    logs_2.clear()
    for i_282 in range(1, 100):
        logs_2.push(latest_logs_2[100 - i_282])
        time.sleep(0.2)


def update_log_panel_3():
    global latest_logs_3
    latest_logs_3 = fetch_latest_logs(100, logs_123="logs_3")
    logs_3.clear()
    for i_282 in range(1, 100):
        logs_3.push(latest_logs_3[100 - i_282])
        time.sleep(0.2)


def panel_log_update():
    try:
        while True:
            try:
                if StrDef.log_print_state.value:
                    log.info("开始更新日志")
                    latest_logs_get = fetch_latest_logs(100, logs_123="logs_1")
                    for i_123 in range(1, 16):
                        for j in range(1, 6):
                            logs_1.push(latest_logs_get[(16 - i_123) * (6 - j)])
                            time.sleep(0.1)
                        time.sleep(2)
                    log.info("日志更新完毕")
                time.sleep(3)
            except Exception as e:
                log.error(f"处理日志时发生错误: {e}")
    except Exception as e:
        log.critical(f"日志更新模块崩溃:{e}")


def panel_log_update_2():
    try:
        while True:
            try:
                if StrDef.log_print_state_2.value:
                    log.info("开始更新日志")
                    latest_logs_get = fetch_latest_logs(100, logs_123="logs_2")
                    for i_123 in range(1, 16):
                        for j in range(1, 6):
                            logs_2.push(latest_logs_get[(16 - i_123) * (6 - j)])
                            time.sleep(0.1)
                        time.sleep(2)
                    log.info("日志更新完毕")
                time.sleep(3)
            except Exception as e:
                log.error(f"处理日志时发生错误: {e}")
    except Exception as e:
        log.critical(f"日志更新模块崩溃:{e}")


def panel_log_update_3():
    try:
        while True:
            try:
                if StrDef.log_print_state_3.value:
                    log.info("开始更新日志")
                    latest_logs_get = fetch_latest_logs(100, logs_123="logs_3")
                    for i_123 in range(1, 16):
                        for j in range(1, 6):
                            logs_3.push(latest_logs_get[(16 - i_123) * (6 - j)])
                            time.sleep(0.1)
                        time.sleep(2)
                    log.info("日志更新完毕")
                time.sleep(3)
            except Exception as e:
                log.error(f"处理日志时发生错误: {e}")
    except Exception as e:
        log.critical(f"日志更新模块崩溃:{e}")


def panel_data_update():
    global data_panel_1_1, data_panel_1
    while True:
        if StrDef.number_update_state.value:
            if data_panel_1 != data_panel_1_1:
                log.info("开始更新数据")
                add_point()
                log.info("数据更新完毕")
            data_panel_1_1 = data_panel_1
        time.sleep(1)


def panel_data_update_2():
    global data_panel_2_1, data_panel_2
    while True:
        if StrDef.number_update_state_2.value:
            if data_panel_2 != data_panel_2_1:
                log.info("开始更新数据")
                add_point_2()
                log.info("数据更新完毕")
            data_panel_2_1 = data_panel_2
        time.sleep(1)


def panel_data_update_3():
    global data_panel_3_1, data_panel_3
    while True:
        if StrDef.number_update_state_3.value:
            if data_panel_3 != data_panel_3_1:
                log.info("开始更新数据")
                add_point_3()
                log.info("数据更新完毕")
            data_panel_3_1 = data_panel_3
        time.sleep(1)


# # 更新仪表参数


def update_func():
    # PID启用 线性启动  报警启动  滤波启动   限幅限速        中位值            平均值
    (PID_f, LIN_f, alarm_f, log_state, filter_A,
     filter_middle, filter_average, H, battery_save, J) = (StrDef.panel1_1_visibility.value,
                                                           StrDef.panel1_2_visibility.value,
                                                           StrDef.alarm_state.value,
                                                           StrDef.log_state.value,
                                                           StrDef.filter_state_f.value,
                                                           StrDef.filter_state_v.value,
                                                           StrDef.filter_state_m.value,
                                                           False,
                                                           StrDef.battery_low_state.value,
                                                           False)

    # Pack the boolean values into a single integer
    S = (int(PID_f) << 9 | int(LIN_f) << 8 | int(alarm_f) << 7 | int(log_state) << 6 | int(filter_A) << 5 |
         int(filter_middle) << 4 | int(filter_average) << 3 | int(battery_save) << 2 | int(battery_save) << 1 | int(J))

    # PID_f, LIN_f, alarm_f, filter_f, filter_A, filter_middle, filter_average, H, battery_save, J
    update_data(StrDef.Panel1_P.value, StrDef.Panel1_I.value, StrDef.Panel1_D.value,
                S, StrDef.Panel1_k.value, StrDef.Panel1_b.value, "TILGF87080")
    StrDef.rewrite_notify = True


def update_func_2():
    # PID启用 线性启动  报警启动  滤波启动   限幅限速        中位值            平均值
    (PID_f, LIN_f, alarm_f, log_state, filter_A,
     filter_middle, filter_average, H, battery_save, J) = (StrDef.panel2_1_visibility.value,
                                                           StrDef.panel2_2_visibility.value,
                                                           StrDef.alarm_state_2.value,
                                                           StrDef.log_state_2.value,
                                                           StrDef.filter_state_f_2.value,
                                                           StrDef.filter_state_v_2.value,
                                                           StrDef.filter_state_m_2.value,
                                                           False,
                                                           StrDef.battery_low_state_2.value,
                                                           False)

    # Pack the boolean values into a single integer
    S = (int(PID_f) << 9 | int(LIN_f) << 8 | int(alarm_f) << 7 | int(log_state) << 6 | int(filter_A) << 5 |
         int(filter_middle) << 4 | int(filter_average) << 3 | int(battery_save) << 2 | int(battery_save) << 1 | int(J))

    # PID_f, LIN_f, alarm_f, filter_f, filter_A, filter_middle, filter_average, H, battery_save, J
    update_data(StrDef.Panel2_P.value, StrDef.Panel2_I.value, StrDef.Panel2_D.value,
                S, StrDef.Panel2_k.value, StrDef.Panel2_b.value, "TILGF37102")
    StrDef.rewrite_notify_2 = True


def update_func_3():
    # PID启用 线性启动  报警启动  滤波启动   限幅限速        中位值            平均值
    (PID_f, LIN_f, alarm_f, log_state, filter_A,
     filter_middle, filter_average, H, battery_save, J) = (StrDef.panel3_1_visibility.value,
                                                           StrDef.panel3_2_visibility.value,
                                                           StrDef.alarm_state_3.value,
                                                           StrDef.log_state_3.value,
                                                           StrDef.filter_state_f_3.value,
                                                           StrDef.filter_state_v_3.value,
                                                           StrDef.filter_state_m_3.value,
                                                           False,
                                                           StrDef.battery_low_state_3.value,
                                                           False)

    # Pack the boolean values into a single integer
    S = (int(PID_f) << 9 | int(LIN_f) << 8 | int(alarm_f) << 7 | int(log_state) << 6 | int(filter_A) << 5 |
         int(filter_middle) << 4 | int(filter_average) << 3 | int(battery_save) << 2 | int(battery_save) << 1 | int(
                J))

    # PID_f, LIN_f, alarm_f, filter_f, filter_A, filter_middle, filter_average, H, battery_save, J
    update_data(StrDef.Panel3_P.value, StrDef.Panel3_I.value, StrDef.Panel3_D.value,
                S, StrDef.Panel3_k.value, StrDef.Panel3_b.value, "TILGF41238")
    StrDef.rewrite_notify_3 = True


def camera():
    # while True:
    time.sleep(3)
    log.info("摄像头启动")
    try:
        camera_read.set_text("摄像头正常")
        print("")
        read_camera_and_upload()
    except Exception as e:
        camera_read.set_text("摄像头异常")
        log.error(f"摄像头异常：{e}")


def data_read_f():
    global socket_style
    while True:
        try:
            time.sleep(4)
            if socket_style:
                listen_update.set_text(f'监听服务已启动')
            else:
                listen_update.set_text(f'监听服务终止')
        except Exception as e:
            log.error(f"仪表读取模块错误：{e}")


# 3d动画的位置检测
def removables():
    while True:
        time.sleep(0.1)
        global click_1_1
        if click_1_1:
            global m_th01
            moved_01.move(x=0)  # 归零
            for i_kua in range(0, 100):
                inc_12 = 0.01 * i_kua
                time.sleep(0.01)
                moved_01.move(x=inc_12)
            moved_01.move(x=0)  # 归零
            click_1_1 = False

    # 历史数据图表函数：


def add_point():
    global data_panel_1, k, fig, m
    for i_1 in range(k):

        x_data = list(fig.data[i_1].x)
        y_data = list(fig.data[i_1].y)
        if next_x_values is not None:
            if data_panel_1 is not None:
                try:
                    new_x = next_x_values[i_1]
                    if i_1 == 0:
                        new_y = data_panel_1[1]  # 环境温度
                    elif i_1 == 1:
                        new_y = (data_panel_1[3] - 90) * 10  # 大气压强
                    elif i_1 == 2:
                        new_y = (data_panel_1[2] - 40) * 2  # 环境湿度
                    elif i_1 == 3:
                        new_y = data_panel_1[11]  # 仪表电流
                    elif i_1 == 4:
                        new_y = data_panel_1[12] / 2000  # 光照强度
                    elif i_1 == 5:
                        new_y = (data_panel_1[4] * 10) - 10  # 仪表功率
                    elif i_1 == 6:
                        new_y = data_panel_1[14]  # 芯片温度
                    elif i_1 == 7:
                        new_y = data_panel_1[18]  # 热敏电阻
                    elif i_1 == 8:
                        new_y = data_panel_1[13]  # 芯片电压
                    elif i_1 == 9:
                        new_y = -data_panel_1[15]  # 海拔高度
                    elif i_1 == 10:
                        new_y = 100.7 - 80  # 电池电量
                    else:
                        new_y = random()  # 输出通道
                    next_x_values[i_1] += 1

                    x_data.append(new_x)
                    y_data.append(new_y)

                    if len(x_data) > m:
                        x_data.pop(0)
                        y_data.pop(0)

                    fig.data[i_1].x = x_data
                    fig.data[i_1].y = y_data
                except Exception as e:
                    if str(e) == "list index out of range":
                        log.warning("图表1未找到数据")
                    else:
                        log.error(e)

    # 更新坐标轴范围
    all_x_data = [float(x_dab1) for trace in fig.data for x_dab1 in trace.x]  # 转换为 float
    all_y_data = [float(y_dab1) for trace in fig.data for y_dab1 in trace.y]  # 转换为 float

    if all_x_data and all_y_data:
        fig.update_layout(
            xaxis=dict(range=[min(all_x_data), max(all_x_data)]),
            yaxis=dict(range=[min(all_y_data) - 0.1, max(all_y_data) + 0.1])
        )

    else:
        pass
    plot.update()


def add_point_2():
    global data_panel_2, k, fig_2, m
    for i_1 in range(k):

        x_data = list(fig_2.data[i_1].x)
        y_data = list(fig_2.data[i_1].y)
        if next_x_values_2 is not None:
            if data_panel_2 is not None:
                try:
                    new_x = next_x_values_2[i_1]
                    if i_1 == 0:
                        new_y = data_panel_2[1]  # 环境温度
                    elif i_1 == 1:
                        new_y = (data_panel_2[3] - 90) * 10  # 大气压强
                    elif i_1 == 2:
                        new_y = (data_panel_2[2] - 40) * 2  # 环境湿度
                    elif i_1 == 3:
                        new_y = data_panel_2[11]  # 仪表电流
                    elif i_1 == 4:
                        new_y = data_panel_2[12] / 2000  # 光照强度
                    elif i_1 == 5:
                        new_y = (data_panel_2[4] * 10) - 10  # 仪表功率
                    elif i_1 == 6:
                        new_y = data_panel_2[14]  # 芯片温度
                    elif i_1 == 7:
                        new_y = data_panel_2[18]  # 热敏电阻
                    elif i_1 == 8:
                        new_y = data_panel_2[13]  # 芯片电压
                    elif i_1 == 9:
                        new_y = -data_panel_2[15]  # 海拔高度
                    elif i_1 == 10:
                        new_y = 100.7 - 80  # 电池电量
                    else:
                        new_y = random()  # 输出通道
                    next_x_values_2[i_1] += 1

                    x_data.append(new_x)
                    y_data.append(new_y)

                    if len(x_data) > m:
                        x_data.pop(0)
                        y_data.pop(0)

                    fig_2.data[i_1].x = x_data
                    fig_2.data[i_1].y = y_data
                except Exception as e:
                    if str(e) == "list index out of range":
                        log.warning("仪表2未找到数据")
                    else:
                        log.error(e)

    # 更新坐标轴范围
    all_x_data = [float(x_dab1) for trace in fig_2.data for x_dab1 in trace.x]  # 转换为 float
    all_y_data = [float(y_dab1) for trace in fig_2.data for y_dab1 in trace.y]  # 转换为 float

    if all_x_data and all_y_data:
        fig_2.update_layout(
            xaxis=dict(range=[min(all_x_data), max(all_x_data)]),
            yaxis=dict(range=[min(all_y_data) - 0.1, max(all_y_data) + 0.1])
        )

    else:
        pass
    plot_2.update()


def add_point_3():
    global data_panel_3, k, fig_3, m
    for i_1 in range(k):

        x_data = list(fig_3.data[i_1].x)
        y_data = list(fig_3.data[i_1].y)
        if next_x_values_3 is not None:
            if data_panel_3 is not None:
                try:
                    new_x = next_x_values_3[i_1]
                    if i_1 == 0:
                        new_y = data_panel_3[1]  # 环境温度
                    elif i_1 == 1:
                        new_y = (data_panel_3[3] - 90) * 10  # 大气压强
                    elif i_1 == 2:
                        new_y = (data_panel_3[2] - 40) * 2  # 环境湿度
                    elif i_1 == 3:
                        new_y = data_panel_3[11]  # 仪表电流
                    elif i_1 == 4:
                        new_y = data_panel_3[12] / 2000  # 光照强度
                    elif i_1 == 5:
                        new_y = (data_panel_3[4] * 10) - 10  # 仪表功率
                    elif i_1 == 6:
                        new_y = data_panel_3[14]  # 芯片温度
                    elif i_1 == 7:
                        new_y = data_panel_3[18]  # 热敏电阻
                    elif i_1 == 8:
                        new_y = data_panel_3[13]  # 芯片电压
                    elif i_1 == 9:
                        new_y = -data_panel_3[15]  # 海拔高度
                    elif i_1 == 10:
                        new_y = 100.7 - 80  # 电池电量
                    else:
                        new_y = random()  # 输出通道
                    next_x_values_3[i_1] += 1

                    x_data.append(new_x)
                    y_data.append(new_y)

                    if len(x_data) > m:
                        x_data.pop(0)
                        y_data.pop(0)

                    fig_3.data[i_1].x = x_data
                    fig_3.data[i_1].y = y_data
                except Exception as e_103:
                    # print(str(e))
                    if str(e_103) == "list index out of range":
                        log.warning("图表3未找到数据")
                    else:
                        log.error(e_103)
    # 更新坐标轴范围
    all_x_data = [float(x_dab1) for trace in fig_3.data for x_dab1 in trace.x]  # 转换为 float
    all_y_data = [float(y_dab1) for trace in fig_3.data for y_dab1 in trace.y]  # 转换为 float

    if all_x_data and all_y_data:
        fig_3.update_layout(
            xaxis=dict(range=[min(all_x_data), max(all_x_data)]),
            yaxis=dict(range=[min(all_y_data) - 0.1, max(all_y_data) + 0.1])
        )

    else:
        pass
    plot_3.update()


# 为每个通道生成一个复选框
def toggle_trace(i_2: int):
    global fig

    def toggle(event) -> None:
        trace: BaseTraceType = fig.data[i_2]
        trace.visible = event.value  # type: ignore
        plot.update()

    return toggle


def toggle_trace_2(i_2: int):
    global fig_2

    def toggle(event) -> None:
        trace: BaseTraceType = fig_2.data[i_2]
        trace.visible = event.value  # type: ignore
        plot_2.update()

    return toggle


def toggle_trace_3(i_2: int):
    global fig_3

    def toggle(event) -> None:
        trace: BaseTraceType = fig_3.data[i_2]
        trace.visible = event.value  # type: ignore
        plot_3.update()

    return toggle


@ui.page('/')
def main_board_0():
    ui.open('/login')


@ui.page('/welcome')
def home():
    ui.label('欢迎来到环境监控系统管理面板欢迎界面！')
    ui.button("点击访问主页", on_click=lambda: redirect())
    ui.label('您将在5秒后被重定向到管理面板')

    def redirect():
        print('跳转中')
        ui.open("/control/board")

    print('定时器设置为5秒')
    ui.timer(5, redirect, once=True)


###
@ui.page("/error")
async def user_portal():
    """Accessible to all authenticated users"""
    ui.label("错误，您没有权限访问此网页")
    ui.button("返回主菜单", on_click=lambda: ui.open("/login"))


###
# 创建初始 UI↓


@ui.page('/control/board')
def user_portal_2():
    if StrDef.level_1 >= 1:
        global bucket_size_show, bucket_name_show, panel_read, picture
        global thread_number, listen_update, label_state, data_read_1, moved_01
        global logs_1, logs_2, logs_3, k_th01, m_th01, click_1_1, plot, plot_2, plot_3, next_x_values, \
            next_x_values_2, next_x_values_3, fig, fig_2, fig_3, k, x, y, method_select, m, conf_check1
        global header, conf_check2, conf_check2_2, conf_check2_3, conf_check3, conf_check3_2, conf_check3_3, \
            mult_1, name, name_2, name_3, scene, conf_check1_2, conf_check1_3, camera_read

        async def update_func_thread():
            log.warning(f"执行更新！参数为：{StrDef.Panel1_P.value}")
            dialog2.close()
            ui.notify(f'将进行参数更新', close_button=True, type='warning')
            await run.io_bound(update_func)
            ui.notify(f'更改成功！', type='positive')

        async def update_func_thread_2():
            log.warning(f"执行更新！参数为：{StrDef.Panel2_P.value}")
            dialog2.close()
            ui.notify(f'将进行参数更新', close_button=True, type='warning')
            await run.io_bound(update_func_2)
            ui.notify(f'更改成功！', type='positive')

        async def update_func_thread_3():
            log.warning(f"执行更新！参数为：{StrDef.Panel3_P.value}")
            dialog2.close()
            ui.notify(f'将进行参数更新', close_button=True, type='warning')
            await run.io_bound(update_func_3)
            ui.notify(f'更改成功！', type='positive')

        # # ping函数
        async def ping_test():
            log.info(f'正在ping')
            global ping_result
            ui.notify(f'正在测试', close_button=True)
            await run.io_bound(get_ping_result)
            log.info(f'延迟：{ping_result}')
            panel1_ping.set_text(f"{ping_result}")
            panel2_ping.set_text(f"{ping_result}")
            panel3_ping.set_text(f"{ping_result}")
            ui.notify(f'测试完成！延迟为{ping_result}', close_button=True, type='positive')

        async def get_log_update():
            log.info("开始更新日志")
            ui.notify("开始更新日志", type="warning")
            await run.io_bound(update_log_panel)
            global latest_logs

            log.info("日志更新完毕")
            ui.notify("日志更新完毕", type="positive")

        async def get_log_update_2():
            log.info("开始更新日志")
            ui.notify("开始更新日志", type="warning")
            await run.io_bound(update_log_panel_2)
            global latest_logs_2

            log.info("日志更新完毕")
            ui.notify("日志更新完毕", type="positive")

        async def get_log_update_3():
            log.info("开始更新日志")
            ui.notify("开始更新日志", type="warning")
            await run.io_bound(update_log_panel_3)
            global latest_logs_3

            log.info("日志更新完毕")
            ui.notify("日志更新完毕", type="positive")

        with ui.dialog() as dialog1, ui.card():
            ui.label('不知道从哪里出现的小猫，它炸毛了，你应该？')
            with ui.row():
                with ui.button('踢一脚', on_click=dialog1.close):
                    ui.tooltip('这可能不是个好选择').classes('bg-red')

                ui.button('悄悄离开~', on_click=dialog1.close)
        with ui.dialog() as notice, ui.card():
            website_prompt = """
            **作者的话：**
            欢迎来到我的云端仪表检测面板示例网站。本站点提供了一套用于实时监控和管理仪表数据的功能，目前已实现的功能包括：
        
            1. **仪表日志图表**：查看仪表数据的历史记录和趋势，支持多种图表展示。
            2. **数据读取**：实时从仪表中读取数据，确保您能够即时获取最新信息。
            3. **状态检测**：监测仪表的当前状态，包括但不限于开/关状态、性能指标等。
            4. **数据库存储**：所有仪表数据都会被安全地存储在云端数据库中，便于历史数据的查询和分析。
            5. **仪表状态存储**：除了数据本身，仪表的状态信息也会被记录，以便于状态的追踪和回溯。
            6. **仪表控制参数更改**：通过网站界面，您可以远程调整仪表的控制参数，实现灵活的远程管理。
        
            我正致力于扩展更多功能，未来计划实现的功能包括：
        
            - **基于深度学习的特定物体识别**：利用最新的AI技术，识别并分析仪表图像中的特定对象。
            - **基于文档信息的报警控制**：通过分析相关文档和信息，智能生成报警控制策略。
            - **基于数据库数据的建模和分析**：对存储的大量数据进行深入分析，提取有价值的信息，支持决策制定。
            - **更多控制算法和检测算法**：利用更多研究出的新控制算法、检测算法来进行运行实验。
            - **对控制流程和算法的一些解释**：说明书。
        
            技术支持：(登录界面)http://hzhcontrols.com/new-1581867.html
            """

            # 将提示翻译成英文
            website_prompt_english = """
                **A Message from the Author:**
                Welcome to my Cloud-based Instrumentation Dashboard Example Website. This site offers a set of \
                features for real-time monitoring and management of instrument data. Currently implemented features \
                include:
                1. **Instrument Log Charts**: View historical records and trends of instrument \
                data with support for various chart displays.
                2. **Data Reading**: Real-time data reading from instruments, \
                ensuring you have immediate access to the latest information.
                3. **Status Detection**: Monitor the current status of instruments, \
                including but not limited to on/off status, performance metrics, etc.
                4. **Database Storage**: All instrument data are securely stored in the \
                cloud database, facilitating the query and analysis of historical data.
                5. **Instrument Status Storage**: In addition to the data itself, the status \
                information of the instruments is also recorded for tracking and retrospective purposes.
                6. **Instrument Control Parameter Changes**: Through the website interface, \
                you can remotely adjust the control parameters of the instruments for flexible remote management.
        
                I am committed to expanding more features, with future planned functionalities including:
        
                - **Specific Object Recognition Based on Deep Learning**: Utilizing the latest \
                AI technology to identify and analyze specific objects in instrument images.
                - **Alarm Control Based on Document Information**: Intelligently generate \
                alarm control strategies by analyzing related documents and information.
                - **Modeling and Analysis Based on Database Data**: Perform in-depth analysis \
                on the stored vast amount of data to extract valuable information to support decision-making.
                - **More Control and Detection Algorithms**: Utilize newly developed control and \
                detection algorithms for experimental operations.
                login menu：http://hzhcontrols.com/new-1581867.html
            """
            ui.markdown(website_prompt)
            ui.markdown(website_prompt_english)
            with ui.row():
                ui.button('确认', on_click=notice.close)
        with ui.dialog() as dialog2, ui.card():
            ui.label('请不要乱动别人设定好的参数哦！')
            with ui.row():
                with ui.button('收到', on_click=dialog2.close):
                    ui.tooltip('收到+1').classes('bg-green')

                ui.button('明白~', on_click=dialog2.close)
                ui.button('确认更改^o^', on_click=update_func_thread)
        with ui.header().classes(replace='row items-center') as header:
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
            ui.markdown('           <font size="5">**环境监控系统管理面板（更新中）**</font>')
            ui.button(on_click=dialog1.open, icon='pets').props('flat color=white')
            ui.markdown('           <font size="5">  | </font>')
            ui.button("访问须知", on_click=notice.open, icon='help').props('flat color=white')
            ui.markdown('           <font size="5">  | </font>')
            with ui.button(icon='email').props('flat color=white'):
                ui.tooltip('暂未实装').classes('bg-green')
            ui.markdown('           <font size="5">  | </font>')
            with ui.button(icon='star').props('flat color=white'):
                ui.tooltip('暂未实装').classes('bg-green')
        with ui.left_drawer(value=False).style("").classes('bg-blue-100').classes('width:50%"') as left_drawer:
            ui.tooltip('这里还什么都没有').classes('bg-green')
            left_drawer.ignores_events_when_hidden = False
            ui.label('侧边栏')
            with ui.button("访问须知", on_click=notice.open).props('flat color=black'):
                ui.tooltip('了解本网站').classes('bg-green')
            with ui.button("返回登录页面", on_click=lambda: ui.open("/login")).props('flat color=black'):
                ui.tooltip('回到登入界面').classes('bg-green')

            def scroll_to_target_1():
                ui.run_javascript("document.getElementById('panel1_jump').scrollIntoView();")

            with ui.button("仪表1", on_click=scroll_to_target_1).props('flat color=black'):
                ui.tooltip('跳转至仪表1').classes('bg-green')

            def scroll_to_target_2():
                ui.run_javascript("document.getElementById('panel2_jump').scrollIntoView();")

            with ui.button("仪表2", on_click=scroll_to_target_2).props('flat color=black'):
                ui.tooltip('跳转至仪表2').classes('bg-green')

            def scroll_to_target_3():
                ui.run_javascript("document.getElementById('panel3_jump').scrollIntoView();")

            with ui.button("仪表3", on_click=scroll_to_target_3).props('flat color=black'):
                ui.tooltip('跳转至仪表3').classes('bg-green')

            def scroll_to_target_4():
                ui.run_javascript("document.getElementById('panel4_jump').scrollIntoView();")

            with ui.button("上下限报警", on_click=scroll_to_target_4).props('flat color=black'):
                ui.tooltip('跳转至上下限报警').classes('bg-green')

            def scroll_to_target_5():
                ui.run_javascript("document.getElementById('panel5_jump').scrollIntoView();")

            with ui.button("模型分析", on_click=scroll_to_target_5).props('flat color=black'):
                ui.tooltip('跳转至模型分析').classes('bg-green')

            def scroll_to_target_6():
                ui.run_javascript("document.getElementById('panel6_jump').scrollIntoView();")

            with ui.button("摄像头(视觉传感器)", on_click=scroll_to_target_6).props('flat color=black'):
                ui.tooltip('跳转至摄像头').classes('bg-green')

            def scroll_to_target_7():
                ui.run_javascript("document.getElementById('panel7_jump').scrollIntoView();")

            with ui.button("关于（页尾）", on_click=scroll_to_target_7).props('flat color=black'):
                ui.tooltip('跳转至页面尾').classes('bg-green')

        with ui.row():
            with ui.element('div').classes('p-2 bg-pink-100'):
                bucket_name_show = ui.tooltip('正在读取存储桶名称...').classes('bg-purple')
                bucket_size_show = ui.label('正在读取数据：')

            with ui.element('div').classes('p-2 bg-pink-100'):
                ui.tooltip('这里显示后台正在运行的活跃线程数量').classes('bg-purple')
                thread_number = ui.label('正在读取数据：')
            with ui.element('div').classes('p-2 bg-pink-100'):
                ui.tooltip('这里显示监听服务状态').classes('bg-purple')
                listen_update = ui.label('正在读取状态：')
            with ui.element('div').classes('p-2 bg-blue-100'):
                ui.tooltip('这里显示仪表状态').classes('bg-purple')
                panel_read = ui.label('正在读取仪表数据：')
            with ui.element('div').classes('p-2 bg-blue-100'):
                ui.tooltip('这里显示数据库状态').classes('bg-purple')
                data_read_1 = ui.label('正在读取数据库状态')
            with ui.element('div').classes('p-2 bg-blue-100'):
                ui.tooltip('这里显示摄像头状态').classes('bg-purple')
                camera_read = ui.label('正在读取摄像头状态')
        ui.separator()
        with ui.row():
            # 表1
            with ui.card().style('width: 650px; height: 980px;'):
                with ui.grid(columns=2):
                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.row().style("flex-direction:column"):
                            with ui.row().style("font-size:1.4rem;gap:0rem"):
                                with ui.element('div').classes('p-2 bg-pink-50'):
                                    with ui.row():
                                        ui.label(" ")
                                        ui.html('<div id="panel1_jump">仪表1</div>')
                            with ui.element('div').classes('p-2 bg-pink-50'):
                                with ui.row().style("flex-direction:row;gap:1.1rem"):
                                    ui.label("状态： ")
                                    label_state = ui.label("正常")
                                with ui.row().style("flex-direction:row;gap:1.1rem"):
                                    ui.label("仪表编号：")
                                    panel_ID_1("E172")
                                with ui.row():
                                    ui.label("上次通讯：")
                                    connect_second("?s 前")
                                with ui.row():
                                    ui.label(" 监测通道数：")
                                    ui.label("12")
                                with ui.row():
                                    ui.label("控制通道数：")
                                    ui.label("1")
                                with ui.row():
                                    ui.label("延迟")
                                    panel1_ping = ui.label("46 ms").style("align-self:flex-start")
                                    ui.button(text="连接测试", on_click=ping_test).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                            with ui.row().style("align-self:center;gap:3.0rem"):
                                with ui.element('div').style("align-self:center;font-size:0.5rem").classes(
                                        'p-2 bg-pink-50'):
                                    ui.label("_________________")
                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.tabs().style("font-size:1.6rem").classes('w-full') as tabs:
                            one = ui.tab('控制')
                            two = ui.tab('滤波')
                            three = ui.tab('其他')
                        with ui.tab_panels(tabs, value=one).classes('w-full'):
                            with ui.tab_panel(one).style("color:#2e77d1"):
                                with ui.row():
                                    def notify_102():
                                        ui.notify("控制模块设定成功", type='positive')

                                    rxui.switch('控制模块', value=StrDef.control_stat,
                                                on_change=lambda: notify_102).style(
                                        'height: 30px;')

                                with ui.row().bind_visibility_from(StrDef.control_stat, 'value'):
                                    ui.label("控制算法")
                                    with ui.row().style('width: 150px; height: 30px;'):
                                        method_select = rxui.select(
                                            {1: 'PID', 2: '线性', 3: 'DPC'}, value=StrDef.select_value).style(
                                            'min-width: 0;width: 50%;min-height: 0;height: 20%;')
                                        conf_check1 = ui.checkbox().bind_visibility_from(
                                            StrDef.panel1_1_visibility, 'value').style(
                                            'width: 40px; height: 40px;').bind_value_from(StrDef.panel1_1_visibility,
                                                                                          "value")
                                        conf_check2 = ui.checkbox().bind_visibility_from(
                                            StrDef.panel1_2_visibility, 'value').style(
                                            'width: 40px; height: 40px;').bind_value_from(StrDef.panel1_2_visibility,
                                                                                          "value")
                                        conf_check3 = ui.checkbox().bind_visibility_from(
                                            StrDef.panel1_3_visibility, 'value').style(
                                            'width: 40px; height: 40px;').bind_value_from(StrDef.panel1_3_visibility,
                                                                                          "value")
                                    rxui.label(visitable_1)  # 动态调用标志
                                with ui.row().bind_visibility_from(StrDef.control_stat, 'value'):
                                    ui.label("控制参数")
                                    with ui.row().style("flex-direction:column").bind_visibility_from(
                                            StrDef.panel1_1_visibility, 'value').style('width: 150px; height: 50px;'):
                                        with ui.row():
                                            rxui.number(min=0, max=9999, label='P', value=StrDef.Panel1_P,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 25%;')
                                            rxui.number(min=0, max=9999, label='I', value=StrDef.Panel1_I,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 25%;')
                                            rxui.number(min=0, max=9999, label='D', value=StrDef.Panel1_D,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 25%;')
                                    with ui.row().bind_visibility_from(StrDef.panel1_1_visibility, 'value'):
                                        rxui.label(pid_show).style('width: 200px; height: 30px;')

                                    with ui.row().style("flex-direction:column").bind_visibility_from(
                                            StrDef.panel1_2_visibility, 'value'):
                                        with ui.row():
                                            rxui.number(min=0, max=9999, label='增益', value=StrDef.Panel1_k,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 32%;')
                                            rxui.number(min=0, max=9999, label='偏移', value=StrDef.Panel1_b,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 32%;')
                                    with ui.row().bind_visibility_from(StrDef.panel1_2_visibility, 'value'):
                                        rxui.label(kb_show).style('width: 200px; height: 30px;')

                                    with ui.row().style("flex-direction:column").bind_visibility_from(
                                            StrDef.panel1_3_visibility, 'value'):
                                        ui.label('此功能暂未实装')

                        with ui.tab_panels(tabs, value=two).classes('w-full'):
                            with ui.tab_panel(two).style("color:#2e77d1"):
                                def notify_103():
                                    ui.notify("滤波算法设定成功", type='positive')

                                mult_1 = rxui.switch("滤波算法", value=StrDef.filter_state_f,
                                                     on_change=lambda: notify_103).style(
                                    'width: 80px; height: 19px;').style(
                                    "align-self:flex-start;font-size:0.7rem")
                                rxui.checkbox('限幅限速滤波', value=StrDef.filter_state_f).style(
                                    'width: 140px; height: 25px;')
                                rxui.checkbox('中位值滤波', value=StrDef.filter_state_m).style(
                                    'width: 140px; height: 25px;')
                                rxui.checkbox('平均值滤波', value=StrDef.filter_state_v).style(
                                    'width: 140px; height: 25px;')
                        with ui.tab_panels(tabs, value=three).classes('w-full'):
                            with ui.tab_panel(three).style("color:#2e77d1"):
                                rxui.checkbox("省电模式", value=StrDef.battery_low_state,
                                              on_change=lambda: ui.notify("模式设定成功", type='positive'))
                                rxui.checkbox("报警", value=StrDef.alarm_state,
                                              on_change=lambda: ui.notify("报警设定成功", type='positive'))
                                rxui.checkbox("读取日志", value=StrDef.log_state,
                                              on_change=lambda: ui.notify("变更成功", type='positive'))
                        with ui.element():
                            ui.button('应用', on_click=dialog2.open).style(
                                'width: 80px; height: 20px;').style(
                                "align-self:flex-start;font-size:0.7rem")
                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.tabs().style("font-size:1.6rem").classes('w-full') as tabs:
                            one_1 = ui.tab('图表')
                            two_2 = ui.tab('通道')
                        with ui.tab_panels(tabs, value=one_1).classes('w-full'):
                            with ui.tab_panel(one_1).style("color:#2e77d1"):
                                ui.label("历史数据图表(已放大趋势)      ")

                                fig = go.Figure()

                                # 根据 k 值创建轨迹
                                for i_894 in range(k):
                                    name = line_name[i_894] if i_894 < len(line_name) else f"通道 {i_894 + 1}"
                                    fig.add_trace(go.Scatter(x=[], y=[], visible=False, name=name))

                                fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
                                plot = ui.plotly(fig).classes('w-full').style(
                                    ' height: 136px;')
                                # 为每个通道维护一个 x 值
                                next_x_values = [1] * k

                        with ui.tab_panels(tabs, value=two_2).classes('w-full'):
                            with ui.tab_panel(two_2).style("color:#2e77d1"):
                                with ui.row():
                                    for i_894 in range(k):
                                        ui.checkbox(f'{line_name[i_894]}', on_change=toggle_trace(i_894)).style(
                                            "align-self:flex-start;font-size:0.6rem").style(
                                            'width: 60px; height: 20px;')
                                with ui.row():
                                    ui.button('添加测试', on_click=add_point).style(
                                        'width: 80px; height: 19px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                                    rxui.switch("自动更新", value=StrDef.number_update_state).style(
                                        'width: 80px; height: 19px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.row():
                            with ui.row().style("flex-direction:column;width:100%"):
                                ui.label("仪表日志：")
                                with ui.row():
                                    ui.button('清除日志', on_click=lambda: logs_1.clear()).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                                    ui.button('获取日志', on_click=lambda: get_log_update()).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")

                                    def notify_90():
                                        ui.notify("变更成功", type='positive')

                                    rxui.switch("自动更新", on_change=lambda: notify_90,
                                                value=StrDef.log_print_state).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                                logs_1 = ui.log(max_lines=10).style('width: 280px; height: 120px;').style(
                                    "align-self:flex-start;font-size:0.7rem")
                                logs_1.push("这里是日志！")
                            with ui.row():
                                ui.label("已运行 ").style("align-self:flex-start;font-size:0.8rem")
                                runtime(" 1天 02 小时 23 分钟 34 秒")
                ui.separator()
                with ui.element('div').classes('p-2 bg-pink-50'):
                    ui.label("仪表数据：")
                    with ui.grid(columns=3).style("gap:2.7rem").style('width: 602px;height: 250px; '):
                        with ui.row():
                            ui.label(" 环境温度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_temp(" ?°C")

                        with ui.row():
                            ui.label(" 大气压强 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_pres(" ?mPa")

                        with ui.row():
                            ui.label(" 环境湿度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_wet_1(" ?%")

                        with ui.row():
                            ui.label(" 仪表电流 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_panel_A(" ? mA")

                        with ui.row():
                            ui.label(" 光照强度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_light(" ??Lux")

                        with ui.row():
                            ui.label(" 仪表功率 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_power(" ? W")
                        with ui.row():
                            ui.label(" 芯片温度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_chip_temp(" ??°C")

                        with ui.row():
                            ui.label(" 热敏电阻 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_temp_core(" ??°C")

                        with ui.row():
                            ui.label(" 芯片电压 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_core_voltage(" ?? V")
                        with ui.row():
                            ui.label(" 海拔高度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_high(" ? m")

                        with ui.row():
                            ui.label(" 电池电量 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_battery(" 100.7%")

                        with ui.row():
                            ui.label(" 输出通道 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_1_output("^U^")
                ui.separator()

                def test_notice():
                    ui.notify(f"暂未实装")

                with ui.row().style("color:#000000;flex-direction:row"):
                    rxui.checkbox("云端数据分析", value=StrDef.data_calculate_1,
                                  on_change=lambda: ui.notify("变更成功", type='positive'))
                    ui.checkbox("学习历史趋势", on_change=test_notice)
                    ui.checkbox("模型智能预警", on_change=test_notice)

            # 表2
            with ui.card().style('width: 650px; height: 980px;'):
                with ui.grid(columns=2):
                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.row().style("flex-direction:column"):
                            with ui.row().style("font-size:1.4rem;gap:0rem"):
                                with ui.element('div').classes('p-2 bg-pink-50'):
                                    with ui.row():
                                        ui.label(" ")
                                        ui.html('<div id="panel2_jump">仪表2</div>')
                            with ui.element('div').classes('p-2 bg-pink-50'):
                                with ui.row().style("flex-direction:row;gap:1.1rem"):
                                    ui.label("状态： ")
                                    label_state = ui.label("正常")
                                with ui.row().style("flex-direction:row;gap:1.1rem"):
                                    ui.label("仪表编号：")
                                    panel_ID_2("E172")
                                with ui.row():
                                    ui.label("上次通讯：")
                                    connect_second("?s 前")
                                with ui.row():
                                    ui.label(" 监测通道数：")
                                    ui.label("12")
                                with ui.row():
                                    ui.label("控制通道数：")
                                    ui.label("1")
                                with ui.row():
                                    ui.label("延迟")
                                    panel2_ping = ui.label("46 ms").style("align-self:flex-start")
                                    ui.button(text="连接测试", on_click=ping_test).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                            with ui.row().style("align-self:center;gap:3.0rem"):
                                with ui.element('div').style("align-self:center;font-size:0.5rem").classes(
                                        'p-2 bg-pink-50'):
                                    ui.label("_________________")
                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.tabs().style("font-size:1.6rem").classes('w-full') as tabs:
                            one_2 = ui.tab('控制')
                            two_2 = ui.tab('滤波')
                            three_2 = ui.tab('其他')
                        with ui.tab_panels(tabs, value=one_2).classes('w-full'):
                            with ui.tab_panel(one_2).style("color:#2e77d1"):
                                with ui.row():
                                    def notify1_0():
                                        ui.notify("控制模块设定成功", type='positive')

                                    rxui.switch('控制模块', value=StrDef.control_stat_2,
                                                on_change=lambda: notify1_0).style(
                                        'height: 30px;')

                                with ui.row().bind_visibility_from(StrDef.control_stat_2, 'value'):
                                    ui.label("控制算法")
                                    with ui.row().style('width: 150px; height: 30px;'):
                                        method_select = rxui.select(
                                            {1: 'PID', 2: '线性', 3: 'DPC'}, value=StrDef.select_value_2).style(
                                            'min-width: 0;width: 50%;min-height: 0;height: 20%;')
                                        conf_check1_2 = ui.checkbox().bind_visibility_from(
                                            StrDef.panel2_1_visibility, 'value').style(
                                            'width: 40px; height: 40px;').bind_value_from(
                                            StrDef.panel2_1_visibility,
                                            "value")
                                        conf_check2_2 = ui.checkbox().bind_visibility_from(
                                            StrDef.panel2_2_visibility, 'value').style(
                                            'width: 40px; height: 40px;').bind_value_from(
                                            StrDef.panel2_2_visibility,
                                            "value")
                                        conf_check3_2 = ui.checkbox().bind_visibility_from(
                                            StrDef.panel2_3_visibility, 'value').style(
                                            'width: 40px; height: 40px;').bind_value_from(
                                            StrDef.panel2_3_visibility,
                                            "value")

                                    rxui.label(visitable_2)  # 动态调用标志
                                with ui.row().bind_visibility_from(StrDef.control_stat_2, 'value'):
                                    ui.label("控制参数")
                                    with ui.row().style("flex-direction:column").bind_visibility_from(
                                            StrDef.panel2_1_visibility, 'value').style(
                                        'width: 150px; height: 50px;'):
                                        with ui.row():
                                            rxui.number(min=0, max=9999, label='P', value=StrDef.Panel2_P,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 25%;')
                                            rxui.number(min=0, max=9999, label='I', value=StrDef.Panel2_I,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 25%;')
                                            rxui.number(min=0, max=9999, label='D', value=StrDef.Panel2_D,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 25%;')
                                    with ui.row().bind_visibility_from(StrDef.panel2_1_visibility, 'value'):
                                        rxui.label(pid_show_2).style('width: 200px; height: 30px;')

                                    with ui.row().style("flex-direction:column").bind_visibility_from(
                                            StrDef.panel2_2_visibility, 'value'):
                                        with ui.row():
                                            rxui.number(min=0, max=9999, label='增益', value=StrDef.Panel2_k,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 32%;')
                                            rxui.number(min=0, max=9999, label='偏移', value=StrDef.Panel2_b,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 32%;')
                                    with ui.row().bind_visibility_from(StrDef.panel2_2_visibility, 'value'):
                                        rxui.label(kb_show_2).style('width: 200px; height: 30px;')

                                    with ui.row().style("flex-direction:column").bind_visibility_from(
                                            StrDef.panel2_3_visibility, 'value'):
                                        ui.label('此功能暂未实装')

                        with ui.tab_panels(tabs, value=two_2).classes('w-full'):
                            with ui.tab_panel(two_2).style("color:#2e77d1"):
                                def notify2_1():
                                    ui.notify("滤波算法设定成功", type='positive')

                                mult_1 = rxui.switch("滤波算法", value=StrDef.filter_state_f_2,
                                                     on_change=lambda: notify2_1).style(
                                    'width: 80px; height: 19px;').style(
                                    "align-self:flex-start;font-size:0.7rem")
                                rxui.checkbox('限幅限速滤波', value=StrDef.filter_state_f_2).style(
                                    'width: 140px; height: 25px;')
                                rxui.checkbox('中位值滤波', value=StrDef.filter_state_m_2).style(
                                    'width: 140px; height: 25px;')
                                rxui.checkbox('平均值滤波', value=StrDef.filter_state_v_2).style(
                                    'width: 140px; height: 25px;')
                        with ui.tab_panels(tabs, value=three_2).classes('w-full'):
                            with ui.tab_panel(three_2).style("color:#2e77d1"):
                                rxui.checkbox("省电模式", value=StrDef.battery_low_state_2,
                                              on_change=lambda: ui.notify("模式设定成功", type='positive'))
                                rxui.checkbox("报警", value=StrDef.alarm_state_2,
                                              on_change=lambda: ui.notify("报警设定成功", type='positive'))

                                def notify7_02():
                                    ui.notify("变更成功", type='positive')

                                rxui.checkbox("读取日志", value=StrDef.log_state_2,
                                              on_change=lambda: notify7_02)
                        with ui.element():
                            ui.button('应用', on_click=dialog2.open).style(
                                'width: 80px; height: 20px;').style(
                                "align-self:flex-start;font-size:0.7rem")
                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.tabs().style("font-size:1.6rem").classes('w-full') as tabs:
                            one_1_2 = ui.tab('图表')
                            two_2_2 = ui.tab('通道')
                        with ui.tab_panels(tabs, value=one_1_2).classes('w-full'):
                            with ui.tab_panel(one_1_2).style("color:#2e77d1"):
                                ui.label("历史数据图表(已放大趋势)      ")

                                fig_2 = go.Figure()

                                # 根据 k 值创建轨迹
                                for i_894_2 in range(k):
                                    name_2 = line_name[i_894_2] if i_894_2 < len(line_name) else f"通道 {i_894_2 + 1}"
                                    fig_2.add_trace(go.Scatter(x=[], y=[], visible=False, name=name_2))

                                fig_2.update_layout(margin=dict(l=0, r=0, t=0, b=0))
                                plot_2 = ui.plotly(fig_2).classes('w-full').style(
                                    ' height: 136px;')
                                # 为每个通道维护一个 x 值
                                next_x_values_2 = [1] * k

                        with ui.tab_panels(tabs, value=two_2_2).classes('w-full'):
                            with ui.tab_panel(two_2_2).style("color:#2e77d1"):
                                with ui.row():
                                    for i_895 in range(k):
                                        ui.checkbox(f'{line_name[i_895]}', on_change=toggle_trace_2(i_895)).style(
                                            "align-self:flex-start;font-size:0.6rem").style(
                                            'width: 60px; height: 20px;')
                                with ui.row():
                                    ui.button('添加测试', on_click=add_point_2).style(
                                        'width: 80px; height: 19px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                                    rxui.switch("自动更新", value=StrDef.number_update_state_2).style(
                                        'width: 80px; height: 19px;').style(
                                        "align-self:flex-start;font-size:0.7rem")

                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.row():
                            with ui.row().style("flex-direction:column;width:100%"):
                                ui.label("仪表日志：")
                                with ui.row():
                                    ui.button('清除日志', on_click=lambda: logs_2.clear()).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                                    ui.button('获取日志', on_click=lambda: get_log_update_2()).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")

                                    def notify3_09():
                                        ui.notify("变更成功", type='positive')

                                    rxui.switch("自动更新",
                                                on_change=lambda: notify3_09,
                                                value=StrDef.log_print_state_2).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                                logs_2 = ui.log(max_lines=10).style('width: 280px; height: 120px;').style(
                                    "align-self:flex-start;font-size:0.7rem")
                                logs_2.push("这里是日志！")

                            with ui.row():
                                ui.label("已运行 ").style("align-self:flex-start;font-size:0.8rem")
                                runtime(" 1天 02 小时 23 分钟 34 秒")
                ui.separator()
                with ui.element('div').classes('p-2 bg-pink-50'):
                    ui.label("仪表数据：")
                    with ui.grid(columns=3).style("gap:2.7rem").style('width: 602px;height: 250px; '):
                        with ui.row():
                            ui.label(" 环境温度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_temp(" ?°C")

                        with ui.row():
                            ui.label(" 大气压强 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_pres(" ?mPa")

                        with ui.row():
                            ui.label(" 环境湿度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_wet_2(" ?%")

                        with ui.row():
                            ui.label(" 仪表电流 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_panel_A(" ? mA")

                        with ui.row():
                            ui.label(" 光照强度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_light(" ??Lux")

                        with ui.row():
                            ui.label(" 仪表功率 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_power(" ? W")
                        with ui.row():
                            ui.label(" 芯片温度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_chip_temp(" ??°C")

                        with ui.row():
                            ui.label(" 热敏电阻 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_temp_core(" ??°C")

                        with ui.row():
                            ui.label(" 芯片电压 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_core_voltage(" ?? V")
                        with ui.row():
                            ui.label(" 海拔高度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_high(" ? m")

                        with ui.row():
                            ui.label(" 电池电量 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_battery(" 100.7%")

                        with ui.row():
                            ui.label(" 输出通道 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_2_output("^U^")
                ui.separator()

                def test_notice():
                    ui.notify(f"暂未实装")

                with ui.row().style("color:#000000;flex-direction:row"):
                    ui.checkbox("学习历史趋势", on_change=test_notice)
                    ui.checkbox("模型智能预警", on_change=test_notice)

                    def notify7_3():
                        ui.notify("变更成功", type='positive')

                    rxui.checkbox("云端数据分析", value=StrDef.data_calculate_2,
                                  on_change=lambda: notify7_3)

            # 表3
            with ui.card().style('width: 650px; height: 980px;'):
                with ui.grid(columns=2):
                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.row().style("flex-direction:column"):
                            with ui.row().style("font-size:1.4rem;gap:0rem"):
                                with ui.element('div').classes('p-2 bg-pink-50'):
                                    with ui.row():
                                        ui.label(" ")
                                        ui.html('<div id="panel3_jump">仪表3</div>')
                            with ui.element('div').classes('p-2 bg-pink-50'):
                                with ui.row().style("flex-direction:row;gap:1.1rem"):
                                    ui.label("状态： ")
                                    label_state = ui.label("正常")
                                with ui.row().style("flex-direction:row;gap:1.1rem"):
                                    ui.label("仪表编号：")
                                    panel_id_3("E172")
                                with ui.row():
                                    ui.label("上次通讯：")
                                    connect_second("?s 前")
                                with ui.row():
                                    ui.label(" 监测通道数：")
                                    ui.label("12")
                                with ui.row():
                                    ui.label("控制通道数：")
                                    ui.label("1")
                                with ui.row():
                                    ui.label("延迟")
                                    panel3_ping = ui.label("46 ms").style("align-self:flex-start")
                                    ui.button(text="连接测试", on_click=ping_test).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                            with ui.row().style("align-self:center;gap:3.0rem"):
                                with ui.element('div').style("align-self:center;font-size:0.5rem").classes(
                                        'p-2 bg-pink-50'):
                                    ui.label("_________________")
                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.tabs().style("font-size:1.6rem").classes('w-full') as tabs:
                            one_3 = ui.tab('控制')
                            two_3 = ui.tab('滤波')
                            three_3 = ui.tab('其他')
                        with ui.tab_panels(tabs, value=one_3).classes('w-full'):
                            with ui.tab_panel(one_3).style("color:#2e77d1"):
                                with ui.row():
                                    def notify3_0():
                                        ui.notify("控制模块设定成功",
                                                  type='positive')

                                    rxui.switch('控制模块', value=StrDef.control_stat_3,
                                                on_change=lambda: notify3_0).style(
                                        'height: 30px;')

                                with ui.row().bind_visibility_from(StrDef.control_stat_3, 'value'):
                                    ui.label("控制算法")
                                    with ui.row().style('width: 150px; height: 30px;'):
                                        method_select = rxui.select(
                                            {1: 'PID', 2: '线性', 3: 'DPC'}, value=StrDef.select_value_3).style(
                                            'min-width: 0;width: 50%;min-height: 0;height: 20%;')
                                        conf_check1_3 = ui.checkbox().bind_visibility_from(
                                            StrDef.panel3_1_visibility, 'value').style(
                                            'width: 40px; height: 40px;').bind_value_from(
                                            StrDef.panel3_1_visibility,
                                            "value")
                                        conf_check2_3 = ui.checkbox().bind_visibility_from(
                                            StrDef.panel3_2_visibility, 'value').style(
                                            'width: 40px; height: 40px;').bind_value_from(
                                            StrDef.panel3_2_visibility,
                                            "value")
                                        conf_check3_3 = ui.checkbox().bind_visibility_from(
                                            StrDef.panel3_3_visibility, 'value').style(
                                            'width: 40px; height: 40px;').bind_value_from(
                                            StrDef.panel3_3_visibility,
                                            "value")

                                    rxui.label(visitable_3)  # 动态调用标志
                                with ui.row().bind_visibility_from(StrDef.control_stat_3, 'value'):
                                    ui.label("控制参数")
                                    with ui.row().style("flex-direction:column").bind_visibility_from(
                                            StrDef.panel3_1_visibility, 'value').style(
                                        'width: 150px; height: 50px;'):
                                        with ui.row():
                                            rxui.number(min=0, max=9999, label='P', value=StrDef.Panel3_P,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 25%;')
                                            rxui.number(min=0, max=9999, label='I', value=StrDef.Panel3_I,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 25%;')
                                            rxui.number(min=0, max=9999, label='D', value=StrDef.Panel3_D,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 25%;')
                                    with ui.row().bind_visibility_from(StrDef.panel3_1_visibility, 'value'):
                                        rxui.label(pid_show_3).style('width: 200px; height: 30px;')

                                    with ui.row().style("flex-direction:column").bind_visibility_from(
                                            StrDef.panel3_2_visibility, 'value'):
                                        with ui.row():
                                            rxui.number(min=0, max=9999, label='增益', value=StrDef.Panel3_k,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 32%;')
                                            rxui.number(min=0, max=9999, label='偏移', value=StrDef.Panel3_b,
                                                        format='%.3f').style(
                                                'min-width: 0;width: 32%;')
                                    with ui.row().bind_visibility_from(StrDef.panel3_2_visibility, 'value'):
                                        rxui.label(kb_show_3).style('width: 200px; height: 30px;')

                                    with ui.row().style("flex-direction:column").bind_visibility_from(
                                            StrDef.panel3_3_visibility, 'value'):
                                        ui.label('此功能暂未实装')

                        with ui.tab_panels(tabs, value=two_3).classes('w-full'):
                            with ui.tab_panel(two_3).style("color:#2e77d1"):
                                def notify3_1():
                                    ui.notify("滤波算法设定成功",
                                              type='positive')

                                mult_1 = rxui.switch("滤波算法", value=StrDef.filter_state_f_3,
                                                     on_change=lambda: notify3_1).style(
                                    'width: 80px; height: 19px;').style(
                                    "align-self:flex-start;font-size:0.7rem")
                                rxui.checkbox('限幅限速滤波', value=StrDef.filter_state_f_3).style(
                                    'width: 140px; height: 25px;')
                                rxui.checkbox('中位值滤波', value=StrDef.filter_state_m_3).style(
                                    'width: 140px; height: 25px;')
                                rxui.checkbox('平均值滤波', value=StrDef.filter_state_v_3).style(
                                    'width: 140px; height: 25px;')
                        with ui.tab_panels(tabs, value=three_3).classes('w-full'):
                            with ui.tab_panel(three_3).style("color:#2e77d1"):
                                rxui.checkbox("省电模式", value=StrDef.battery_low_state_3,
                                              on_change=lambda: ui.notify("模式设定成功", type='positive'))
                                rxui.checkbox("报警", value=StrDef.alarm_state_3,
                                              on_change=lambda: ui.notify("报警设定成功", type='positive'))

                                rxui.checkbox("读取日志", value=StrDef.log_state_3,
                                              on_change=lambda: ui.notify("变更成功", type='positive'))
                        with ui.element():
                            ui.button('应用', on_click=dialog2.open).style(
                                'width: 80px; height: 20px;').style(
                                "align-self:flex-start;font-size:0.7rem")
                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.tabs().style("font-size:1.6rem").classes('w-full') as tabs:
                            one_1_3 = ui.tab('图表')
                            two_2_3 = ui.tab('通道')
                        with ui.tab_panels(tabs, value=one_1_3).classes('w-full'):
                            with ui.tab_panel(one_1_3).style("color:#2e77d1"):
                                ui.label("历史数据图表(已放大趋势)      ")

                                fig_3 = go.Figure()

                                # 根据 k 值创建轨迹
                                for i_894_3 in range(k):
                                    name_3 = line_name[i_894_3] if i_894_3 < len(
                                        line_name) else f"通道 {i_894_3 + 1}"
                                    fig_3.add_trace(go.Scatter(x=[], y=[], visible=False, name=name_3))

                                fig_3.update_layout(margin=dict(l=0, r=0, t=0, b=0))
                                plot_3 = ui.plotly(fig_3).classes('w-full').style(
                                    ' height: 136px;')
                                # 为每个通道维护一个 x 值
                                next_x_values_3 = [1] * k

                        with ui.tab_panels(tabs, value=two_2_3).classes('w-full'):
                            with ui.tab_panel(two_2_3).style("color:#2e77d1"):
                                with ui.row():
                                    for i_895 in range(k):
                                        ui.checkbox(f'{line_name[i_895]}', on_change=toggle_trace_3(i_895)).style(
                                            "align-self:flex-start;font-size:0.6rem").style(
                                            'width: 60px; height: 20px;')
                                with ui.row():
                                    ui.button('添加测试', on_click=add_point_3).style(
                                        'width: 80px; height: 19px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                                    rxui.switch("自动更新", value=StrDef.number_update_state_3).style(
                                        'width: 80px; height: 19px;').style(
                                        "align-self:flex-start;font-size:0.7rem")

                    with ui.element('div').classes('p-2 bg-pink-50'):
                        with ui.row():
                            with ui.row().style("flex-direction:column;width:100%"):
                                ui.label("仪表日志：")
                                with ui.row():
                                    ui.button('清除日志', on_click=lambda: logs_3.clear()).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                                    ui.button('获取日志', on_click=lambda: get_log_update_3()).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")

                                    def notify_890():
                                        ui.notify("变更成功", type='positive')

                                    rxui.switch("自动更新",
                                                on_change=lambda: notify_890,
                                                value=StrDef.log_print_state_3).style(
                                        'width: 80px; height: 20px;').style(
                                        "align-self:flex-start;font-size:0.7rem")
                                logs_3 = ui.log(max_lines=10).style('width: 280px; height: 120px;').style(
                                    "align-self:flex-start;font-size:0.7rem")
                                logs_3.push("这里是日志！")

                            with ui.row():
                                ui.label("已运行 ").style("align-self:flex-start;font-size:0.8rem")
                                runtime(" 1天 02 小时 23 分钟 34 秒")
                ui.separator()
                with ui.element('div').classes('p-2 bg-pink-50'):
                    ui.label("仪表数据：")
                    with ui.grid(columns=3).style("gap:2.7rem").style('width: 602px;height: 250px; '):
                        with ui.row():
                            ui.label(" 环境温度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_temp(" ?°C")

                        with ui.row():
                            ui.label(" 大气压强 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_pres(" ?mPa")

                        with ui.row():
                            ui.label(" 环境湿度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_wet_3(" ?%")

                        with ui.row():
                            ui.label(" 仪表电流 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_panel_A(" ? mA")

                        with ui.row():
                            ui.label(" 光照强度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_light(" ??Lux")

                        with ui.row():
                            ui.label(" 仪表功率 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_power(" ? W")
                        with ui.row():
                            ui.label(" 芯片温度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_chip_temp(" ??°C")

                        with ui.row():
                            ui.label(" 热敏电阻 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_temp_core(" ??°C")

                        with ui.row():
                            ui.label(" 芯片电压 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_core_voltage(" ?? V")
                        with ui.row():
                            ui.label(" 海拔高度 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_high(" ? m")

                        with ui.row():
                            ui.label(" 电池电量 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_battery(" 100.7%")

                        with ui.row():
                            ui.label(" 输出通道 ").style("align-self:flex-start;font-size:0.8rem")
                            ui.label(":")
                            panel_3_output("^U^")
                ui.separator()

                def test_notice():
                    ui.notify(f"暂未实装")

                with ui.row().style("color:#000000;flex-direction:row"):
                    rxui.checkbox("云端数据分析", value=StrDef.data_calculate_3,
                                  on_change=lambda: ui.notify("变更成功", type='positive'))
                    ui.checkbox("学习历史趋势", on_change=test_notice)
                    ui.checkbox("模型智能预警", on_change=test_notice)

            ##############################################################################################
            # 插入字符串到内容中  manager.insert_string("Hello, ")

            # 打印内容  manager.print_content()

            # 获取插入次数  manager.get_insert_count()

            # 清空内容  manager.clear_content()
            # 得到最后一次警报内容  manager.get_last_insert()
            with ui.card().style('width: 650px; height: 980px;'):
                ui.html('<div id="panel4_jump">这里是警报</div>')
                panel_alarm("没有警报")
                ui.label("仪表1")
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("温度")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel1_alarm_1_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel1_alarm_1_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("压强")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel1_alarm_2_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel1_alarm_2_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("湿度")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel1_alarm_3_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel1_alarm_3_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("电流")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel1_alarm_4_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel1_alarm_4_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("光强")
                        rxui.number(min=-19999, max=19999, label='上限', value=StrDef.Panel1_alarm_5_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-19999, max=19999, label='下限', value=StrDef.Panel1_alarm_5_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("功率")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel1_alarm_6_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel1_alarm_6_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("芯温")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel1_alarm_7_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel1_alarm_7_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("表温")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel1_alarm_8_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel1_alarm_8_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("芯压")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel1_alarm_9_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel1_alarm_9_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("海拔")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel1_alarm_10_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel1_alarm_10_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("电量")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel1_alarm_11_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel1_alarm_11_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("输出")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel1_alarm_12_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel1_alarm_12_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                ui.label("仪表2")
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("温度")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel2_alarm_1_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel2_alarm_1_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("压强")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel2_alarm_2_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel2_alarm_2_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("湿度")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel2_alarm_3_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel2_alarm_3_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("电流")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel2_alarm_4_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel2_alarm_4_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("光强")
                        rxui.number(min=-19999, max=19999, label='上限', value=StrDef.Panel2_alarm_5_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-19999, max=19999, label='下限', value=StrDef.Panel2_alarm_5_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("功率")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel2_alarm_6_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel2_alarm_6_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("芯温")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel2_alarm_7_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel2_alarm_7_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("表温")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel2_alarm_8_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel2_alarm_8_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("芯压")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel2_alarm_9_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel2_alarm_9_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("海拔")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel2_alarm_10_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel2_alarm_10_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("电量")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel2_alarm_11_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel2_alarm_11_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("输出")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel2_alarm_12_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel2_alarm_12_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                ui.label("仪表3")
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("温度")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel3_alarm_1_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel3_alarm_1_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("压强")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel3_alarm_2_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel3_alarm_2_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("湿度")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel3_alarm_3_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel3_alarm_3_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("电流")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel3_alarm_4_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel3_alarm_4_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("光强")
                        rxui.number(min=-19999, max=19999, label='上限', value=StrDef.Panel3_alarm_5_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-19999, max=19999, label='下限', value=StrDef.Panel3_alarm_5_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("功率")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel3_alarm_6_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel3_alarm_6_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("芯温")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel3_alarm_7_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel3_alarm_7_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("表温")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel3_alarm_8_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel3_alarm_8_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("芯压")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel3_alarm_9_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel3_alarm_9_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                with ui.row():
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("海拔")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel3_alarm_10_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel3_alarm_10_l,
                                    format='%.3f').style('width: 50px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("电量")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel3_alarm_11_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel3_alarm_11_l,
                                    format='%.3f').style('width: 60px; height: 18px;')
                    with ui.row():
                        with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                            ui.label("输出")
                        rxui.number(min=-9999, max=9999, label='上限', value=StrDef.Panel3_alarm_12_h,
                                    format='%.3f').style('width: 50px; height: 18px;')
                        rxui.number(min=-9999, max=9999, label='下限', value=StrDef.Panel3_alarm_12_l,
                                    format='%.3f').style('width: 60px; height: 18px;')

        ui.separator()

        ################################################################################################

        with ui.row():
            def report_api():
                basic = "仪表1位于卧室，仪表2位于客厅，仪表3位于厨房"
                panel1_report = f"仪表1数据：温度48°，湿度{str(data_panel_1[2])}气压{str(data_panel_1[3])}仪表电流{str(data_panel_1[4])}亮度{str(data_panel_1[12])}仪表功率{str(data_panel_1[12])}芯片温度{str(data_panel_1[14])}海拔{str(data_panel_1[15])}电池电量{battery1:.2f}"
                panel2_report = f"仪表2数据：温度{str(data_panel_2[1])}湿度{str(data_panel_2[2])}气压{str(data_panel_2[3])}仪表电流{str(data_panel_2[4])}亮度{str(data_panel_2[12])}仪表功率{str(data_panel_2[12])}芯片温度{str(76)}海拔{str(data_panel_2[15])}电池电量{battery2:.2f}"
                panel3_report = f"仪表3数据：温度{str(data_panel_3[1])}湿度{str(data_panel_3[2])}气压{str(data_panel_3[3])}仪表电流{str(data_panel_3[4])}亮度{str(data_panel_3[12])}仪表功率{str(data_panel_3[12])}芯片温度{str(data_panel_3[14])}海拔{str(data_panel_3[15])}电池电量{12}"
                attampt = basic + panel1_report + panel2_report + panel3_report + str("分析此部分数据")
                if StrDef.report_in_change.value:
                    attampt += str(StrDef.report_input.value)
                if StrDef.report_in_advice.value:
                    attampt = attampt + "请在此基础上给出环境建议"
                if StrDef.report_in_alarm.value:
                    attampt = attampt + "请在此基础上生成警报，如果发现了数据异常，在分析尾另起一行加上异常评级，格式为   -风险等级:（修改为异常评级）-   括号内为需要修改内容，无问题则评级为正常"
                model_report, token_cost = get_report(attampt)
                model_report_show.refresh(f"{model_report}  字节消耗：{str(token_cost)}")

            async def generate_report():
                log.info(f'正在生成报告')
                ui.notify(f'正在生成报告', close_button=True)
                log.warning(str(StrDef.report_input.value))
                await run.io_bound(report_api)
                log.info(f'生成成功')
                ui.notify(f'生成成功', close_button=True)

            with ui.card().style('width: 650px; height: 800px;'):
                ui.tooltip("这里可以对数据进行简单分析")
                ui.html('<div id="panel6_jump">数据分析模块</div>')
                ui.label("检测特点：")
                with ui.row():
                    rxui.checkbox("参数异常报警", value=StrDef.report_in_alarm)
                    rxui.checkbox("环境分析建议", value=StrDef.report_in_advice)
                    rxui.checkbox("提示词调整", value=StrDef.report_in_change)
                model_report_show("这里显示分析报告")
                ui.button("生成分析报告", on_click=generate_report)
                rxui.input(label="手动调整", placeholder='输入提示词', value=StrDef.report_input,
                           validation={'提示词过长': lambda value: len(value) < 20})

            def report_p_api():
                basic = "请识别图中的图像并判断是否有以下内容，"
                attampt = basic
                if StrDef.report_p_in_advice.value:
                    attampt += str(StrDef.report_p_input.value)
                if StrDef.report_p_in_change.value:
                    attampt = attampt + "图中是否有生物活动？"
                if StrDef.report_p_in_alarm.value:
                    attampt = attampt + "图中是否有火焰或其他异常？"
                #model_report_p, token_cost_p = picture_api_analy(attampt)
                #model_report_show_p.refresh(f"{model_report_p}  字节消耗：{str(token_cost_p)}")

            async def generate_p_report():
                log.info(f'正在生成报告')
                ui.notify(f'正在生成报告', close_button=True)
                log.warning(str(StrDef.report_input.value))
                await run.io_bound(report_p_api)
                log.info(f'生成成功')
                ui.notify(f'生成成功', close_button=True)

            ##################################################################################################
            with ui.card().style('width: 650px; height: 800px;'):
                ui.html('<div id="panel6_jump">视觉传感器</div>')
                from picture_find import find_newest_file
                picture = ui.image().style(
                    'height: 300px;')
                with ui.row():
                    ui.tooltip("这里显示视觉传感器截图！")
                    rxui.checkbox("火焰/异常检测", value=StrDef.report_p_in_alarm)
                    rxui.checkbox("生物活动检测", value=StrDef.report_p_in_change)
                    rxui.checkbox("提示词检测", value=StrDef.report_p_in_advice)
                rxui.input(label="手动提示", placeholder='输入提示词', value=StrDef.report_p_input,
                           validation={'提示词过长': lambda value: len(value) < 20})
                model_report_show_p("这里显示分析报告")
                ui.button("生成分析报告", on_click=generate_p_report)
                ####################################################################################
                ################################################################################################

            def map_temp_to_color(temp, min_temp_23, temp_range_width__31):
                index = int((temp - min_temp_23) / temp_range_width__31)
                index = max(0, min(index, len(temperature_colors) - 1))  # 确保索引不小于0也不越界
                return temperature_colors[index]

            with ui.element('div').style("align-self:center").classes('p-2 bg-white-50').style(
                    'width: 650px; height: 400px;'):
                ui.html('<div id="panel5_jump">基于数据和已知环境的实时建模分析</div>')
                with ui.scene().classes('width: 650px; height: 400px;') as scene:
                    scene.box().scale(60, 60, 1).move(z=-0.3)
                    house = 'https://storage.picture.aichangeworld.tech/usedfor-s-three-test/scenes/house.STL'
                    scene.stl(house).scale(0.2).rotate(3.14 / 2, 0, 0).move(x=-10, y=15, z=-0.1).material('#DEDEDE')
                    tree = 'https://storage.picture.aichangeworld.tech/usedfor-s-three-test/scenes/tree.stl'
                    scene.stl(tree).scale(0.6).rotate(3.14 / 2, 0, 0).move(x=22).material('#3BD13B')
                    scene.stl(tree).scale(0.6).rotate(3.14 / 2, 0, 0).move(x=22, y=-10).material('#ADFF2F')
                    loaded_arr2_1 = np.load('arr.npy')
                    x = loaded_arr2_1.shape[0]
                    y = loaded_arr2_1.shape[1]
                    z = loaded_arr2_1.shape[2]
                    wall = np.ones_like(loaded_arr2_1)
                    # 放置墙
                    wall[:, 6] = 0
                    wall[9, :6] = 0
                    wall[:6, 16] = 0
                    wall[6, 16:23] = 0
                    wall[:12, 23] = 0
                    wall[12, 21:] = 0
                    wall[12:, 21] = 0
                    wall[27, :] = 0
                    # 放置门
                    wall[:3, 6, 0:4] = 1
                    wall[11:13, 6, 0:4] = 1
                    wall[27, 1:4, 2:5] = 1
                    wall[7:10, 23, 0:4] = 1
                    wall[12, 21:24, 0:4] = 1
                    # 计算最大值和最小值
                    max_temp = 23  # np.max(arr)
                    min_temp = 15
                    # 确定每个温度范围的宽度
                    temp_range_width = (max_temp - min_temp) / 25
                    sphere = [[[0 for _ in range(z)] for _ in range(y)] for _ in range(x)]
                    with scene.group().move(x=-9, y=-18):
                        for i_124 in range(x):
                            for j_1 in range(y):
                                for k_101 in range(z):
                                    if i_124 >= 27 and j_1 <= 21:
                                        break
                                    else:
                                        sphere[i_124][j_1][k_101] = scene.sphere().material('#4488ff').move(x=i_124,
                                                                                                            y=j_1,
                                                                                                            z=k_101).scale(
                                            0.1)
                        for i_124 in range(len(sphere)):  # 对应 arr 的 x 轴
                            for j_3 in range(len(sphere[0])):  # 对应 arr 的 y 轴
                                for k_102 in range(len(sphere[0][0])):
                                    try:
                                        color = map_temp_to_color(loaded_arr2_1[i_124][j_3][k_102], min_temp,
                                                                  temp_range_width)
                                        if not isinstance(sphere[i_124][j_3][k_102], int):
                                            if wall[i_124][j_3][k_102] == 0:
                                                # print(f"x={i}y={j}z={k}")
                                                sphere[i_124][j_3][k_102].material('#ADFF2F')
                                                # print(0)
                                            else:
                                                sphere[i_124][j_3][k_102].material(color)
                                        else:
                                            pass
                                            # print(f"Skipping sphere[{i}][{j}][{k}] because it is not a scene object.")
                                    except Exception as e__29:
                                        print(e__29)
                                        print(i_124, j_3, k_102)
                                    if i_124 >= 27 and j_3 <= 21:
                                        break
                                    else:
                                        pass

                    scene.cylinder(1, 0.5, 2, 20).material('#ff8800', opacity=0.5).move(-2, 1)
                    scene.extrusion([[0, 0], [0, 1], [1, 0.5]], 0.1).material('#ff8888').move(-2, -2)

                    with scene.group().move(z=2):
                        # kua_001 = scene.box().move(x=2)
                        moved_01 = scene.box().move(x=4, y=2).rotate(0.25, 0.5, 0.75)
                        scene.box(wireframe=True).material('#888888').move(x=2, y=2)
                    # scene.line([-4, 0, 0], [-4, 2, 0]).material('#ff0000')
                    # scene.curve([-4, 0, 0], [-4, -1, 0], [-3, -1, 0], [-3, -2, 0]).material('#008800')

                    # logo = 'https://avatars.githubusercontent.com/u/2843826'
                    # scene.texture(logo, [[[0.5, 2, 0], [2.5, 2, 0]],
                    #  [[0.5, 0, 0], [2.5, 0, 0]]]).move(1, -2)

                    # teapot = 'https://upload.wikimedia.org/wikipedia/commons/9/93/Utah_teapot_(solid).stl'
                    # scene.stl(teapot).scale(0.2).move(-3, 4)

                    # scene.text('2D', 'background: rgba(0, 0, 0, 0.2); border-radius: 5px; padding: 5px').move(z=2)
                    scene.text3d('这里还在实验中！',
                                 'background: rgba(0, 0, 0, 0.2); border-radius: 5px; padding: 5px').move(
                        y=4, z=2).scale(.05).rotate(3.14 / 2, 0, 0)

                def step_update():
                    global data_panel_1, data_panel_2, data_panel_3
                    try:
                        loaded_arr = np.load('arr.npy')
                    except Exception as e__30:
                        log.warning(e__30)
                        loaded_arr = np.random.randint(20, 21, size=(24, 24, 6))
                    # 更新一步
                    # 墙和温度场
                    arr = loaded_arr
                    wall_28 = np.ones_like(arr)
                    # 放置墙
                    wall_28[:, 6] = 0
                    wall_28[9, :6] = 0
                    wall_28[:6, 16] = 0
                    wall_28[6, 16:23] = 0
                    wall_28[:12, 23] = 0
                    wall_28[12, 21:] = 0
                    wall_28[12:, 21] = 0
                    wall_28[27, :] = 0
                    # 放置门
                    wall_28[:3, 6, 0:4] = 1
                    wall_28[11:13, 6, 0:4] = 1
                    wall_28[27, 1:4, 2:5] = 1
                    wall_28[7:10, 23, 0:4] = 1
                    wall_28[12, 21:24, 0:4] = 1
                    # 定义取得的数值
                    arr[5:7][7:9][2:4] = data_panel_2[18]
                    arr[18:20][22:24][2:4] = data_panel_1[18]
                    arr[22:24][3:5][3:5] = data_panel_3[18]
                    # 提取不同点
                    arr_diff = extract_different_neighbours(arr)
                    # 更新权重
                    arr_step_1 = calculate_temperature_change(arr, wall_28, arr_diff, time_step=5)
                    print(np.around(arr_step_1, decimals=4))
                    arr = arr + arr_step_1
                    print(np.around(arr, decimals=3))

                    # 计算最大值和最小值
                    max_temp_25 = 23  # np.max(arr)
                    min_temp_26 = 15  # np.min(arr)
                    # 确定每个温度范围的宽度
                    temp_range_width_27 = (max_temp_25 - min_temp_26) / 25

                    for i_123 in range(len(sphere)):  # 对应 arr 的 x 轴
                        for j_123 in range(len(sphere[0])):  # 对应 arr 的 y 轴
                            for k_123 in range(len(sphere[0][0])):
                                try:
                                    color_1 = map_temp_to_color(arr[i_123][j_123][k_123], min_temp_26,
                                                                temp_range_width_27)
                                    if not isinstance(sphere[i_123][j_123][k_123], int):
                                        if wall_28[i_123][j_123][k_123] == 0:
                                            # print(f"x={i}y={j}z={k}")
                                            sphere[i_123][j_123][k_123].material('#ADFF2F')
                                            # print(0)
                                        else:
                                            sphere[i_123][j_123][k_123].material(color_1)
                                    else:
                                        pass
                                        # print(f"Skipping sphere[{i}][{j}][{k}] because it is not a scene object.")
                                except Exception as e__30:
                                    print(e__30)
                                    print(i_123, j_123, k_123)
                                if i_123 >= 27 and j_123 <= 21:
                                    break
                                else:
                                    pass
                    # 将数组保存到文件中
                    np.save('arr.npy', arr)

                def time__sleep():
                    time.sleep(10)

                async def calculate_1_1():
                    log.info(f'正在进行模拟')
                    ui.notify(f'正在进行模拟', close_button=True)
                    await run.io_bound(step_update)
                    log.info(f'模拟完成')
                    ui.notify(f'模拟完成', close_button=True)

                async def calculate_2():
                    log.info(f'正在进行模拟')
                    ui.notify(f'正在进行模拟', close_button=True)
                    for i___3 in range(100):
                        if StrDef.auto_update:
                            await run.io_bound(time__sleep)
                            await run.io_bound(step_update)
                            step_simu.refresh(f"模拟时长：5s 模拟次数 {i___3}次")
                        else:
                            step_simu.refresh(f"模拟时长：5s 模拟次数 {0}次")
                    log.info(f'模拟完成')
                    ui.notify(f'模拟完成', close_button=True)

                with ui.dialog() as define_1, ui.card():
                    ui.label('确认要长时间模拟吗，可能对低配置计算机造成运算负担。。')
                    with ui.row():
                        with ui.button('确认！', on_click=calculate_1_1):
                            ui.tooltip('可以接受').classes('bg-red')

                        ui.button('我再想想', on_click=define_1.close)
                with ui.element('div').style("align-self:center").classes('p-2 bg-white-50'):
                    with ui.row():
                        ui.button(text="模拟一步", on_click=calculate_1_1)
                        with ui.button(text="长时间模拟", on_click=define_1.open):
                            ui.tooltip(
                                '这将使模拟变为周期常态化，模拟结果有±3s的延时，此结果是由采集速度决定的').classes(
                                'bg-red')
                        step_simu(f"模拟时长：5s 模拟次数 ？次")
                        rxui.checkbox("确认模拟", value=StrDef.auto_update,
                                      on_change=lambda: ui.notify("模式设定成功", type='positive'))

                ##################################################################################################
        ############################################################################################33
        ui.separator()
        # 页脚
        with ui.row():
            ui.html('<div id="panel7_jump">此页面由 hunter 设计</div>')
            ui.label("技术支持:")
            ui.html('<a href="https://nicegui.io/" target="_blank">NiceGUI</a>')
            ui.label("ICP备案号：")
            ui.html('<a href="https://beian.miit.gov.cn/" target="_blank">黑ICP备2024016760号-1</a>')
    else:
        ui.open("/error")
        print(StrDef.level_1)


app.on_startup(threading.Thread(target=camera, daemon=True).start)  # 视觉传感器更新
app.on_startup(threading.Thread(target=renews, daemon=True).start)  # 视觉传感器采集图像更新
app.on_startup(threading.Thread(target=read_bucket_size_f, daemon=True).start)  # bucket_size_show的参数更新
app.on_startup(threading.Thread(target=thread_number_read, daemon=True).start)  # 线程检测器
app.on_startup(threading.Thread(target=listen_update_f, daemon=True).start)  # 仪表监听终端
app.on_startup(threading.Thread(target=panel_read_f, daemon=True).start)  # 仪表的参数更新
app.on_startup(threading.Thread(target=data_read_f, daemon=True).start)  # 数据库状态更新
app.on_startup(threading.Thread(target=system_clock, daemon=True).start)  # 线程检测器
app.on_startup(threading.Thread(target=panel_data_update, daemon=True).start)  # 仪表1的图表更新
app.on_startup(threading.Thread(target=panel_data_update_2, daemon=True).start)  # 仪表2的图表更新
app.on_startup(threading.Thread(target=panel_data_update_3, daemon=True).start)  # 仪表3的图表更新
app.on_startup(threading.Thread(target=panel_log_update, daemon=True).start)  # 仪表1的日志更新
app.on_startup(threading.Thread(target=panel_log_update_2, daemon=True).start)  # 仪表2的日志更新
app.on_startup(threading.Thread(target=panel_log_update_3, daemon=True).start)  # 仪表3的日志更新
app.on_startup(threading.Thread(target=removables, daemon=True).start)  # 3d更新

user_number = 0


def user_connect():
    global user_number
    user_number += 1
    log.info(f"用户数：{user_number} 用户连接")


app.on_connect(user_connect)


def user_disconnect():
    global user_number
    user_number -= 1
    log.info(f"用户数：{user_number} 用户断开连接")


app.on_disconnect(user_disconnect)
ui.run(port=8456, favicon="bin/web_icon.png", title="云端分析控制面板（实验）",
       storage_secret="world_never_abandoned_you")
