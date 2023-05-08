import pymysql
import operator

from core.connection.mysql_client import param

if __name__ == '__main__':

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
               + kw_sql + "1=1"
        cur.execute(sql1)

    conn.commit()
    cur.close()
    conn.close()
