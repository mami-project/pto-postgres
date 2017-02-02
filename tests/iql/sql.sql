DROP TABLE IF EXISTS iql_test;

CREATE TABLE iql_test (
  oid BIGSERIAL NOT NULL,
  name VARCHAR(255) NOT NULL,
  val_n REAL,
  attr_a REAL NOT NULL,
  attr_b VARCHAR(255)[] NOT NULL,
  attr_c VARCHAR(255) NOT NULL
);

INSERT INTO iql_test(name, val_n, attr_a, attr_b, attr_c)
  VALUES
 ('msmnt1', 1.0, 1.0, ARRAY['a','b','c'], 'abc'),
 ('msmnt1', 1.0, 4.0, ARRAY['a','b','c'], 'def'),
 ('msmnt2', 1.0, 3.0, ARRAY['a','b','c'], 'def'),
 ('msmnt2', 1.0, 3.1, ARRAY['d','e','f'], 'qxz'),
 ('msmnt3', 1.0, 3.5, ARRAY['q','x','z'], 'lmo'),
 ('msmnt1', 2.0, 4.9, ARRAY['l','m','n'], 'bur'),
 ('msmnt4', 3.0, 1.7, ARRAY['l','m','n'], 'bir'),
 ('msmnt2', 1.1, 1.1, ARRAY['d','e','f'], 'bil'),
 ('msmnt5', 3.0, 5.0, ARRAY['u','m','g'], 'lol'),
 ('msmnt5', 6.0, 7.0, ARRAY['s','t','u'], 'lal'),
 ('msmnt5', 8.8, 9.0, ARRAY['s','t','u'], 'bri'),
 ('msmnt5', 6.0, 7.0, ARRAY['u','m','g'], 'zxy');
