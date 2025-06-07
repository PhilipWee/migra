create table t(id integer primary key, value text);

create view v as select * from t;

create view v2 as select * from t;

alter view v owner to schemainspect_test_role; 