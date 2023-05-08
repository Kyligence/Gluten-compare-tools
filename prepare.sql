create database compare_tools;
use compare_tools;

CREATE TABLE inconsistent_record (
id bigint(20) NOT NULL AUTO_INCREMENT,
project  text CHARACTER SET utf8 NOT NULL,
query text CHARACTER SET utf8 NOT NULL,
gluten_result text CHARACTER SET utf8 NOT NULL,
normal_result text CHARACTER SET utf8 NOT NULL,
tag text CHARACTER SET utf8 NOT NULL,
createtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (id)
);

CREATE TABLE response_time (
id bigint(20) NOT NULL AUTO_INCREMENT,
project  text CHARACTER SET utf8 NOT NULL,
query text CHARACTER SET utf8 NOT NULL,
gluten_res_time bigint,
normal_res_time bigint,
createtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (id)
);

CREATE TABLE error_category (
id bigint(20) NOT NULL AUTO_INCREMENT,
keywords  text CHARACTER SET utf8 NOT NULL,
tag text CHARACTER SET utf8 NOT NULL,
status text CHARACTER SET utf8 NOT NULL,
createtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (id)
);

insert into error_category(keywords,tag,status)
values('SELECT /*+,OBJECT STORAGE Exception', 'comment_analyze', 'unsolved'),
(': Object,not found', 'sql_object_not_found', 'unsolved'),
('s3: //,[OBJECT STORAGE Exception] Input path does not exist', 's3_path_not_found', 'unsolved'),
('[OBJECT STORAGE Exception],com.amazonaws.services.s3.model.AmazonS3Exception: Forbidden (Service: Amazon S3', 's3_access_forbidden', 'unsolved'),
('KE-010001201:,t find project', 'project_not_found', 'unsolved'),
('[OBJECT STORAGE Exception] : Instantiate org.apache.hadoop.fs.s3a.auth.AssumedRoleCredentialProvider,Service: AWSSecurityTokenService,Error Code: AccessDenied', 'aws_access_denied', 'unsolved'),
('[OBJECT STORAGE Exception] Table or view not found', 'table_view_not_found' ,'unsolved');