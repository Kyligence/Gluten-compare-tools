import json
import unittest

from core.message.ke_response_parser import KEResponseParser
from core.result.ke_comparer import KEComparer


class TestSum(unittest.TestCase):

    def test_float_check(self):
        double1 = json.loads("""
        {"code":"000","data":{"glutenFallback": "0","columnMetas":[{"isNullable":1,"displaySize":2147483647,"label":"avg(CNT)","name":"avg(CNT)","schemaName":null,"catelogName":null,"tableName":null,"precision":0,"scale":0,"columnType":8,"columnTypeName":"DOUBLE","caseSensitive":false,"autoIncrement":false,"searchable":false,"currency":false,"definitelyWritable":false,"writable":false,"signed":true,"readOnly":false}],"results":[["1348.0625"]],"affectedRowCount":0,"exceptionMessage":null,"duration":4217,"scanRows":null,"scanBytes":null,"failTimes":-1,"resultRowCount":1,"shufflePartitions":1,"hitExceptionCache":false,"storageCacheUsed":false,"storageCacheType":null,"queryStatistics":null,"queryId":"b6999318-1851-f6eb-5080","server":"10.198.33.188:8190","signature":null,"engineType":"HIVE","traces":[{"name":"HTTP_RECEPTION","group":null,"duration":11},{"name":"GET_ACL_INFO","group":"PREPARATION","duration":0},{"name":"SQL_TRANSFORMATION","group":"PREPARATION","duration":8},{"name":"SQL_PARSE_AND_OPTIMIZE","group":"PREPARATION","duration":70},{"name":"MODEL_MATCHING","group":"PREPARATION","duration":41},{"name":"SQL_PUSHDOWN_TRANSFORMATION","group":null,"duration":4},{"name":"SPARK_JOB_EXECUTION","group":null,"duration":4083}],"exception":false,"stopByUser":false,"totalScanRows":-1,"totalScanBytes":-1,"partial":false,"prepare":false,"timeout":false,"refused":false,"isException":false,"appMasterURL":"/kylin/sparder/SQL/execution/?id=0","pushDown":true,"is_prepare":false,"is_timeout":false,"is_refused":false,"is_stop_by_user":false,"realizations":[],"executed_plan":null},"msg":""}
        """)
        double2 = json.loads("""
        {"code":"000","data":{"glutenFallback": "0","columnMetas":[{"isNullable":1,"displaySize":2147483647,"label":"avg(CNT)","name":"avg(CNT)","schemaName":null,"catelogName":null,"tableName":null,"precision":0,"scale":0,"columnType":8,"columnTypeName":"DOUBLE","caseSensitive":false,"autoIncrement":false,"searchable":false,"currency":false,"definitelyWritable":false,"writable":false,"signed":true,"readOnly":false}],"results":[["1348.062500001"]],"affectedRowCount":0,"exceptionMessage":null,"duration":4217,"scanRows":null,"scanBytes":null,"failTimes":-1,"resultRowCount":1,"shufflePartitions":1,"hitExceptionCache":false,"storageCacheUsed":false,"storageCacheType":null,"queryStatistics":null,"queryId":"b6999318-1851-f6eb-5080","server":"10.198.33.188:8190","signature":null,"engineType":"HIVE","traces":[{"name":"HTTP_RECEPTION","group":null,"duration":11},{"name":"GET_ACL_INFO","group":"PREPARATION","duration":0},{"name":"SQL_TRANSFORMATION","group":"PREPARATION","duration":8},{"name":"SQL_PARSE_AND_OPTIMIZE","group":"PREPARATION","duration":70},{"name":"MODEL_MATCHING","group":"PREPARATION","duration":41},{"name":"SQL_PUSHDOWN_TRANSFORMATION","group":null,"duration":4},{"name":"SPARK_JOB_EXECUTION","group":null,"duration":4083}],"exception":false,"stopByUser":false,"totalScanRows":-1,"totalScanBytes":-1,"partial":false,"prepare":false,"timeout":false,"refused":false,"isException":false,"appMasterURL":"/kylin/sparder/SQL/execution/?id=0","pushDown":true,"is_prepare":false,"is_timeout":false,"is_refused":false,"is_stop_by_user":false,"realizations":[],"executed_plan":null},"msg":""}
        """)

        double3 = json.loads("""
            {"code":"000","data":{"glutenFallback": "0","columnMetas":[{"isNullable":1,"displaySize":2147483647,"label":"avg(CNT)","name":"avg(CNT)","schemaName":null,"catelogName":null,"tableName":null,"precision":0,"scale":0,"columnType":8,"columnTypeName":"DOUBLE","caseSensitive":false,"autoIncrement":false,"searchable":false,"currency":false,"definitelyWritable":false,"writable":false,"signed":true,"readOnly":false}],"results":[["1349.0625"]],"affectedRowCount":0,"exceptionMessage":null,"duration":4217,"scanRows":null,"scanBytes":null,"failTimes":-1,"resultRowCount":1,"shufflePartitions":1,"hitExceptionCache":false,"storageCacheUsed":false,"storageCacheType":null,"queryStatistics":null,"queryId":"b6999318-1851-f6eb-5080","server":"10.198.33.188:8190","signature":null,"engineType":"HIVE","traces":[{"name":"HTTP_RECEPTION","group":null,"duration":11},{"name":"GET_ACL_INFO","group":"PREPARATION","duration":0},{"name":"SQL_TRANSFORMATION","group":"PREPARATION","duration":8},{"name":"SQL_PARSE_AND_OPTIMIZE","group":"PREPARATION","duration":70},{"name":"MODEL_MATCHING","group":"PREPARATION","duration":41},{"name":"SQL_PUSHDOWN_TRANSFORMATION","group":null,"duration":4},{"name":"SPARK_JOB_EXECUTION","group":null,"duration":4083}],"exception":false,"stopByUser":false,"totalScanRows":-1,"totalScanBytes":-1,"partial":false,"prepare":false,"timeout":false,"refused":false,"isException":false,"appMasterURL":"/kylin/sparder/SQL/execution/?id=0","pushDown":true,"is_prepare":false,"is_timeout":false,"is_refused":false,"is_stop_by_user":false,"realizations":[],"executed_plan":null},"msg":""}
            """)

        results = {}
        results["source_message"] = {"sql": "testsql"}
        results["addition"] = "test"
        results["results"] = []
        result1 = {"dest_url": {"tag": "normal", "url": ""}, "result": double1}
        result2 = {"dest_url": {"tag": "gluten", "url": ""}, "result": double2}
        result3 = {"dest_url": {"tag": "gluten", "url": ""}, "result": double3}
        results["results"].append(result1)
        results["results"].append(result2)

        ke = KEResponseParser()
        parse_result = ke.parse_dest_response(results)
        self.assertEqual(parse_result.results[0].schema[0].is_float, True)
        self.assertEqual(parse_result.results[1].schema[0].is_float, True)

        compare = KEComparer()
        compare.insert_result = False
        self.assertEqual(compare.compare(parse_result), True)

        results["results"].clear()
        results["results"].append(result1)
        results["results"].append(result3)
        parse_result = ke.parse_dest_response(results)
        self.assertEqual(parse_result.results[0].schema[0].is_float, True)
        self.assertEqual(parse_result.results[1].schema[0].is_float, True)
        self.assertEqual(compare.compare(parse_result), False)


    def test_sum_tuple(self):
        self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")


if __name__ == '__main__':
    unittest.main()
