import mysql.connector
from dashboard.lib.log_color import log
from dashboard.variables.variable import Var

SQL_HOST = Var.SQL_HOST
SQL_PORT = Var.SQL_PORT
SQL_USER_NAME = Var.SQL_USER_NAME
SQL_USER_PASSWORD = Var.SQL_USER_PASSWORD
SQL_DATABASE = Var.SQL_DATABASE


def insert_data(temperature, wet, power, press, panel_A, light, core_V,
                T_2, high, chip_temp, ID, P_read, I_read, D_read, S_read):
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

        # 准备SQL插入语句
        sql = """
        INSERT INTO datasavelist (temperature, wet, power, press, panel_A, light, core_V, T_2, high, chip_temp, name_panel,P,I,D,S)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # 执行SQL语句
        cursor.execute(sql, (temperature, wet, power, press, panel_A,
                             light, core_V, T_2, high, chip_temp, ID, P_read, I_read, D_read, S_read))

        # 提交到数据库执行
        conn.commit()

        # 插入成功消息
        log.info("数据成功插入!")

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
    insert_data(114.0, 27.5, 65.6,
                2.5, 1, 1, 2, 1, 1,
                1, 1, 1, 1, 1, 1)
