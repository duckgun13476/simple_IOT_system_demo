from nicegui import ui, app
from uuid import uuid4


# 定义一个函数来创建用户特定的界面
def create_user_specific_page(user_id):
    @ui.page(f'/{user_id}')
    def user_page():
        ui.label(f'这是用户 {user_id} 的专属页面')

        # 在这里添加更多用户特定的界面元素
        def remove_tab():
            app.routes[:] = [route for route in app.routes if route.path != f'/{user_id}']

        ui.button("删除页面", on_click=lambda: remove_tab())


# 创建一个主页面，为每个访问者生成一个唯一的用户ID和URL
@ui.page('/')
def main_page():
    user_id = str(uuid4())
    ui.label('欢迎来到主页面')
    ui.link('前往你的专属页面', f'/{user_id}')
    create_user_specific_page(user_id)


ui.run(port=8454, title="12")
