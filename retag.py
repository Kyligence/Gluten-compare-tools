import pymysql
import operator

from core.connection.mysql_client import param

if __name__ == '__main__':
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

    conn = pymysql.connect(**param)  # 连接对象
    cur = conn.cursor()  # 游标对象，采用默认的数据格式

    sql0 = "select keywords,tag from error_category"
    cur.execute(sql0)
    results = cur.fetchall()
    for row in results:
        keywords = row[0].split(",")
        tag_in_error_category = row[1]
        kw_sql = ""
        for kw in keywords:
            kw_sql = kw_sql + "locate('" + kw + "', gluten_result) > 0 and "

        sql1 = "update inconsistent_record set tag='" + tag_in_error_category + "' where " \
               + kw_sql + "tag='unrecognized'"
        cur.execute(sql1)

    conn.commit()
    cur.close()
    conn.close()
