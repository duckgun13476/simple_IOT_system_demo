import mysql.connector
from dashboard.lib.log_color import log
from dashboard.lib.sugar import timer
from dashboard.variables.variable import Var

SQL_HOST = Var.SQL_HOST
SQL_PORT = Var.SQL_PORT
SQL_USER_NAME = Var.SQL_USER_NAME
SQL_USER_PASSWORD = Var.SQL_USER_PASSWORD
SQL_DATABASE = Var.SQL_DATABASE


@timer
def get_latest_update_data(id_1):
    try:
        # 创建数据库连接
        conn = mysql.connector.connect(
            host=SQL_HOST,
            port=SQL_PORT,
            user=SQL_USER_NAME,
            password=SQL_USER_PASSWORD,
            database=SQL_DATABASE
        )

        # 创建一个cursor对象来执行SQL语句
        cursor = conn.cursor()

        sql = """
                    SELECT * FROM datasavelist
                    WHERE name_panel = %s
                    ORDER BY id DESC
                    LIMIT 1
                    """

        # 执行SQL语句，传入参数'TILGF37102'
        cursor.execute(sql, (id_1,))

        # 获取查询结果
        result = cursor.fetchone()
        if result:
            return result
        else:
            log.error("未找到数据")

    except mysql.connector.Error as err:
        # 返回错误消息
        log.error(f"错误: {err}")

    finally:
        # 关闭cursor和连接
        if conn.is_connected():
            cursor.close()
            conn.close()


# 调用函数示例
if __name__ == '__main__':

    latest_data = get_latest_update_data('TILGF37102')
    if latest_data:
        log.info(f"最新参数: {latest_data}")
        log.info(f'参数为：型号：{latest_data[0]}参数：{latest_data[1]}{latest_data[2]}{latest_data[3]}{latest_data[4]}')
