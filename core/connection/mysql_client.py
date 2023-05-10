import pymysql
import operator

# ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';
# FLUSH PRIVILEGES;

param = {
    'host': '127.0.0.1',
    'port': 3306,
    'db': 'compare_tools',
    'user': 'root',
    'password': 'lHuang0928_7750',
    'charset': 'utf8',
}


# CREATE TABLE inconsistent_record (
# id bigint(20) NOT NULL AUTO_INCREMENT,
# project  text CHARACTER SET utf8 NOT NULL,
# query text CHARACTER SET utf8 NOT NULL,
# gluten_result text CHARACTER SET utf8 NOT NULL,
# normal_result text CHARACTER SET utf8 NOT NULL,
# tag text CHARACTER SET utf8 NOT NULL,
# createtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
# PRIMARY KEY (id)
# );

# CREATE TABLE error_category (
# id bigint(20) NOT NULL AUTO_INCREMENT,
# keywords  text CHARACTER SET utf8 NOT NULL,
# tag text CHARACTER SET utf8 NOT NULL,
# status text CHARACTER SET utf8 NOT NULL,
# createtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
# PRIMARY KEY (id)
# );

def insert_into_inconsistent_record(*args):
    conn = pymysql.connect(**param)  # 连接对象
    try:
        with conn.cursor() as cur:  # 游标对象，采用默认的数据格式

            tag = "unrecognized"
            sql0 = "select keywords,tag from error_category"
            cur.execute(sql0)
            results = cur.fetchall()
            gluten_result = args[2]
            for row in results:
                keywords = row[0]
                tag_in_error_category = row[1]
                error_matched = True
                for kw in keywords.split(","):
                    error_matched = error_matched and operator.contains(gluten_result, kw)
                if error_matched:
                    tag = tag_in_error_category
                    break

            sql1 = "insert into inconsistent_record(project,query,gluten_result,normal_result,tag) " \
                   "values(%s, %s, %s, %s, %s)"
            params = args + (tag,)
            cur.execute(sql1, params)  # sql语句参数化，防止攻击！
            conn.commit()
        cur.close()  # 关闭游标
    finally:
        conn.close()  # 关闭连接


# CREATE TABLE response_time (
# id bigint(20) NOT NULL AUTO_INCREMENT,
# project  text CHARACTER SET utf8 NOT NULL,
# query text CHARACTER SET utf8 NOT NULL,
# gluten_res_time bigint,
# normal_res_time bigint,
# createtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
# PRIMARY KEY (id)
# );
def insert_into_response_time(*args):
    conn = pymysql.connect(**param)  # 连接对象
    try:
        with conn.cursor() as cur:  # 游标对象，采用默认的数据格式
            sql = "insert into response_time(project,query,gluten_res_time,normal_res_time) values(%s, %s, %s, %s)"
            params = args
            cur.execute(sql, params)  # sql语句参数化，防止攻击！
            conn.commit()
        cur.close()  # 关闭游标
    finally:
        conn.close()  # 关闭连接
