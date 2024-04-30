import mysql.connector
from dashboard.lib.log_color import log
from dashboard.variables.variable import Var

SQL_HOST = Var.SQL_HOST
SQL_PORT = Var.SQL_PORT
SQL_USER_NAME = Var.SQL_USER_NAME
SQL_USER_PASSWORD = Var.SQL_USER_PASSWORD
SQL_DATABASE = Var.SQL_DATABASE


def update_data(P=None, I=None, D=None, S=None, k=None, b=None, model=None):
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

        # 动态构建更新语句的一部分
        updates = []
        params = []
        if P is not None:
            updates.append("P = %s")
            params.append(P)
        if I is not None:
            updates.append("I = %s")
            params.append(I)
        if D is not None:
            updates.append("D = %s")
            params.append(D)
        if S is not None:
            updates.append("S = %s")
            params.append(S)
        if k is not None:
            updates.append("k = %s")
            params.append(k)
        if b is not None:
            updates.append("b = %s")
            params.append(b)

        # 检查是否提供了需要更新的字段
        if not updates:
            log.info("没有提供更新的数据")
            return

        update_query = "UPDATE InstrumentParameters SET " + ", ".join(updates) + " WHERE Model = %s;"
        params.append(model)  # 添加 Model 作为 WHERE 子句的参数

        # 执行SQL语句
        cursor.execute(update_query, params)

        # 提交到数据库执行
        conn.commit()

        # 插入成功消息
        log.info("数据成功更新!")

    except mysql.connector.Error as err:
        # 返回错误消息
        log.error(f"错误: {err}")

    finally:
        # 关闭cursor和连接
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# 调用函数示例
if __name__ == '__main__':
    update_data(None, 43, None, None, None, None, "ETOYS1233")
