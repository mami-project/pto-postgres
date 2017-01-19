-- Conditions for the condition_tree

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

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(9, 'ce', 0, 'ecn.ce');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(10, 'ect_zero', 0, 'ecn.ect_zero');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(11, 'ect_one', 0, 'ecn.ect_one');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(12, 'super', 1, 'ecn.connectivity.super');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(13, 'works', 12, 'ecn.connectivity.super.works');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(14, 'broken', 12, 'ecn.connectivity.super.broken');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(15, 'transient', 12, 'ecn.connectivity.super.transient');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(16, 'offline', 12, 'ecn.connectivity.super.offline');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(17, 'weird', 12, 'ecn.connectivity.super.weird');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(18, 'path_dependent', 0, 'ecn.path_dependent');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(19, 'weak', 18, 'ecn.path_dependent.weak');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(20, 'strong', 18, 'ecn.path_dependent.strong');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(21, 'strict', 18, 'ecn.path_dependent.strict');

INSERT INTO condition_tree(cid, name, paretn, full_name)
 VALUES(22, 'site_dependent', 1, 'ecn.site_dependent');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(23, 'weak', 22, 'ecn.path_dependent.weak');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(24, 'strong', 22, 'ecn.path_dependent.strong');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(25, 'strict', 22, 'ecn.path_dependent.strict');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(26, 'seen', 10, 'ecn.ect_zero.seen');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(27, 'seen', 11, 'ecn.ect_one.seen');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(28, 'seen', 9, 'ecn.ce.seen');
