import pymysql
import operator

from core.connection.mysql_client import param

if __name__ == '__main__':

    conn = pymysql.connect(**param)  # 连接对象
    try:
        with conn.cursor() as cur:  # 游标对象，采用默认的数据格式
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

            sql2 = "delete from compare_tools.inconsistent_record " \
                   "where tag='unrecognized' and (normal_result like 'The query exceeds the set time limit%' " \
                   "or normal_result like '[OBJECT STORAGE Exception]%' " \
                   "or normal_result like '%not found within%' " \
                   "or normal_result like '%Unable to fetch table%')"
            cur.execute(sql2)
            conn.commit()
            cur.close()
    finally:
        conn.close()
