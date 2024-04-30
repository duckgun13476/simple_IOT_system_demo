import mysql.connector
from dashboard.lib.log_color import log
from dashboard.lib.sugar import timer
import os
from dashboard.variables.variable import Var

SQL_HOST = Var.SQL_HOST
SQL_PORT = Var.SQL_PORT
SQL_USER_NAME = Var.SQL_USER_NAME
SQL_USER_PASSWORD = Var.SQL_USER_PASSWORD
SQL_DATABASE = Var.SQL_DATABASE


@timer
def get_latest_data(id, id2, id3):
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

        # 准备SQL查询语句，获取最大ID的记录
        sql = """
            SELECT * FROM datasavelist
            WHERE name_panel = %s
            ORDER BY id DESC
            LIMIT 1
            """

        # 执行SQL语句，传入参数'TILGF37102'
        cursor.execute(sql, (id,))
        # 获取查询结果
        result1 = cursor.fetchone()
        cursor.execute(sql, (id2,))
        # 获取查询结果
        result2 = cursor.fetchone()
        cursor.execute(sql, (id3,))
        # 获取查询结果
        result3 = cursor.fetchone()
        if result1:
            if result2:
                if result3:
                    return result1, result2, result3
        else:
            log.warning("未找到数据/连接不稳定")

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
    latest_data1, latest_data2, latest_data3 = get_latest_data('TILGF37102', 'TILGF37102', 'TILGF37102')
    if latest_data1:
        if latest_data2:
            if latest_data3:
                log.info(f"最新数据: {latest_data1}{latest_data2}{latest_data3}")
                log.info(f'温度为：{latest_data1[1]}{latest_data1[2]}{latest_data1[3]}')
