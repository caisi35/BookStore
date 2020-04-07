import pymysql.cursors


class ToConn:
    def __init__(self):
        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            db='bookstore',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    # 查询数据库信息
    def get_db(self, sql, t=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, t)
                return cursor
        # 关闭数据库连接
        finally:
            self.connection.close()

    # 执行操作命令
    def to_db(self, sql, t=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, t)
                return self.connection
        finally:
            pass

