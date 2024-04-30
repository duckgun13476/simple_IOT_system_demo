import mysql.connector
from dashboard.lib.log_color import log
from dashboard.lib import time_8
from dashboard.variables.variable import Var
SQL_HOST = Var.SQL_HOST
SQL_PORT = Var.SQL_PORT
SQL_USER_NAME = Var.SQL_USER_NAME
SQL_USER_PASSWORD = Var.SQL_USER_PASSWORD
SQL_DATABASE = Var.SQL_DATABASE


def fetch_latest_logs(k, logs_123="logs_1 "):
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
        log.info("读取日志信息中")
        # 准备SQL插入语句
        query = "SELECT content, insert_time FROM " + logs_123 + " ORDER BY insert_time DESC LIMIT %s"
        # 执行SQL语句
        cursor.execute(query, (k,))
        logs = [f"{content} {insert_time}" for content, insert_time in cursor.fetchall()]
        logs = time_8.time_8(logs)
        # 插入成功消息
        log.info("日志信息成功读取!")

    except mysql.connector.Error as err:
        # 返回错误消息
        log.error(f"错误: {err}")

    finally:
        # 关闭cursor和连接
        if conn.is_connected():
            cursor.close()
            conn.close()
    return logs


# 调用函数示例
if __name__ == '__main__':
    latest_logs = fetch_latest_logs(3)
    print(latest_logs)
