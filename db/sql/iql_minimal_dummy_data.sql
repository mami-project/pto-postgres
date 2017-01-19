INSERT INTO observation_set(osid, name, toi)
 VALUES(0, 'test0', 999999);

INSERT INTO observation_set(osid, name, toi)
 VALUES(1, 'test1', 999999);

INSERT INTO observation(oid, full_path, time_from, time_to, val_n, observation_set, condition)
 VALUES(0, ARRAY['192.168.1.100','192.168.1.1','166.166.166.166']::VARCHAR[],
       '2016-07-18T18:13:50.403000', '2016-07-18T18:14:50.403000', 1, 0, 2);

INSERT INTO observation(oid, full_path, time_from, time_to, val_n, observation_set, condition)
 VALUES(1, ARRAY['192.168.1.100','192.168.1.1','166.166.166.167']::VARCHAR[],
       '2016-07-18T18:13:50.403000', '2016-07-18T18:14:50.403000', 1, 0, 3);

INSERT INTO observation(oid, full_path, time_from, time_to, val_n, observation_set, condition)
 VALUES(2, ARRAY['192.168.1.100','192.168.1.1','166.166.166.166']::VARCHAR[],
       '2016-07-18T18:13:50.403000', '2016-07-18T18:14:50.403000', 1, 1, 3);

INSERT INTO observation(oid, full_path, time_from, time_to, val_n, observation_set, condition)
 VALUES(3, ARRAY['192.168.1.100','192.168.1.1','166.166.166.167']::VARCHAR[],
       '2016-07-18T18:13:50.403000', '2016-07-18T18:14:50.403000', 1, 1, 3);

INSERT INTO observation(oid, full_path, time_from, time_to, val_n, observation_set, condition)
 VALUES(4, ARRAY['192.168.1.100','192.168.1.1','166.166.166.168']::VARCHAR[],
       '2016-07-18T18:13:50.403000', '2016-07-18T18:14:50.403000', 1, 1, 3);
