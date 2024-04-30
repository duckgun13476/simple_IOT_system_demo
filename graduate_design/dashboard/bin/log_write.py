import mysql.connector
from dashboard.lib.log_color import log
from dashboard.variables.variable import Var

SQL_HOST = Var.SQL_HOST
SQL_PORT = Var.SQL_PORT
SQL_USER_NAME = Var.SQL_USER_NAME
SQL_USER_PASSWORD = Var.SQL_USER_PASSWORD
SQL_DATABASE = Var.SQL_DATABASE


def insert_logs(logs,list):
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
        log.info("插入日志信息中")

        # 准备SQL插入语句
        insert_query = "INSERT INTO " + list + " (content) VALUES (%s)"

        # 构建包含所有日志信息的列表
        log_values = [(log_entry,) for log_entry in logs]

        # 执行一次性插入
        cursor.executemany(insert_query, log_values)

        # 提交到数据库执行
        conn.commit()

        # 插入成功消息
        log.info("日志信息成功插入!")

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
    log_data = ["数据34", "数据132","数据113", "数据23","数据31", "数据412"]
    insert_logs(log_data,"logs_1")