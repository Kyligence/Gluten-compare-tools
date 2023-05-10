create database compare_tools;
--use compare_tools;

CREATE TABLE compare_tools.inconsistent_record (
id bigint(20) NOT NULL AUTO_INCREMENT,
project  text CHARACTER SET utf8 NOT NULL,
query text CHARACTER SET utf8 NOT NULL,
gluten_result text CHARACTER SET utf8 NOT NULL,
normal_result text CHARACTER SET utf8 NOT NULL,
tag text CHARACTER SET utf8 NOT NULL,
createtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (id)
);

CREATE TABLE compare_tools.response_time (
id bigint(20) NOT NULL AUTO_INCREMENT,
project  text CHARACTER SET utf8 NOT NULL,
query text CHARACTER SET utf8 NOT NULL,
gluten_res_time bigint,
normal_res_time bigint,
createtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (id)
);

CREATE TABLE compare_tools.error_category (
id bigint(20) NOT NULL AUTO_INCREMENT,
keywords  text CHARACTER SET utf8 NOT NULL,
tag text CHARACTER SET utf8 NOT NULL,
status text CHARACTER SET utf8 NOT NULL,
createtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (id)
);

insert into compare_tools.error_category(keywords,tag,status)
values('SELECT /*+,OBJECT STORAGE Exception', 'comment_analyze', 'unsolved'),
(': Object,not found', 'sql_object_not_found', 'unsolved'),
('s3: //,[OBJECT STORAGE Exception] Input path does not exist', 's3_path_not_found', 'unsolved'),
('[OBJECT STORAGE Exception],com.amazonaws.services.s3.model.AmazonS3Exception: Forbidden (Service: Amazon S3', 's3_access_forbidden', 'unsolved'),
('KE-010001201:,t find project', 'project_not_found', 'unsolved'),
('[OBJECT STORAGE Exception] : Instantiate org.apache.hadoop.fs.s3a.auth.AssumedRoleCredentialProvider,Service: AWSSecurityTokenService,Error Code: AccessDenied', 'aws_access_denied', 'unsolved'),
('[OBJECT STORAGE Exception] Table or view not found', 'table_view_not_found' ,'unsolved'),
('Column,not found in', 'column_not_found' ,'unsolved'),
('Cannot apply,FLOOR,to arguments of type', 'floor_args_error' ,'unsolved'),
('Illegal use of,NULL', 'Illegal_use_of_null' ,'unsolved'),
('The query exceeds the set time limit', 'time_out' ,'unsolved'),
('OBJECT STORAGE Exception,ExecutorLostFailure,Job aborted due to stage failure,Remote RPC client disassociated', 'executor_lost' ,'unsolved'),
('OBJECT STORAGE Exception,ExecutorLostFailure,Job aborted due to stage failure,Executor heartbeat timed out after', 'executor_heartbeat_time_out' ,'unsolved'),
('OBJECT STORAGE Exception,org.apache.hadoop.hive.ql.metadata.HiveException,Unable to get database object', 'metadata_unable_to_get_database_object' ,'unsolved'),
('OBJECT STORAGE Exception,org.apache.hadoop.hive.ql.metadata.HiveException,Unable to fetch table', 'metadata_unable_to_fetch_table' ,'unsolved'),
('KE-010003208: Invalid username or password', 'invalid_username_or_password' ,'unsolved'),
