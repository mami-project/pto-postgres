INSERT INTO condition_tree(cid, name, parent, full_name) 
 VALUES(0, 'ecn', NULL, 'ecn');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(1, 'connectivity', 0, 'ecn.connectivity');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(2, 'works', 1, 'ecn.connectivity.works');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(3, 'broken', 1, 'ecn.connectivity.broken');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(4, 'transient', 1, 'ecn.connectivity.transient');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(5, 'offline', 1, 'ecn.connectivity.offline');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(6, 'negotiation_attempt', 0, 'ecn.negotiation_attempt');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(7, 'succeeded', 6, 'ecn.negotiation_attempt.succeeded');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(8, 'failed', 6, 'ecn.negotiation_attempt.failed');

INSERT INTO observation_set(osid, toc, toi)
 VALUES(0, 0, 999999);

INSERT INTO observation_set(osid, toc, toi)
 VALUES(1, 1, 999999);

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
