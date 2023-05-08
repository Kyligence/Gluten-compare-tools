# Gluten-compare-tools
## Background
This tool forwards http requests to downstreams ,which is mainly designed to record the difference of the resutls between two 
comparing products.
Also you can classify those differences by offerring tags and keywords.



## Design
To be 

## Usage
1 install python dependency package

`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple retrying`

`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pymysql`

`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple flask`

2 get an existing mysql or setup one yourself

3 run prepare.sql with mysql client

`Table inconsistent_record:record difference or runtime error of the two comparing products and tag the difference`

`Table response_time:if no inconsistentence, record the response time of the two comparing products for performance statistics later`

`Table error_category:difference or error feature,use keywords and tag to describe this`

4 config

`core/connection/mysql_client.py: config mysql connection info in param`

`core/common/config.py: config DEST_URLS for your own path`

5 run

`python3 main.py`
pull up http forwarder service and tag the difference or error according to table error_category

`python3 retag.py` or
`python3 retag_deep.py`
tag the history unrecognized error record in table inconsistent_record according to table error_category.
If you add some new error category in table error_category,you can run this command to tag the history record
in table inconsistent_record.

6 check the unrecognized error in mysql table

`select * from inconsistent_record where tag='unrecognized'`





