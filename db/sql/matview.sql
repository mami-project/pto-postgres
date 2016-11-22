CREATE MATERIALIZED VIEW iql_data
AS
 SELECT observation.id AS oid,
    observation.condition AS name,
    observation.val_i,
    observation.val_s,
    observation.time_to,
    observation.time_from,
    observation.path_id,
    path.full_path,
    path.dip,
    path.sip,
    (SELECT ARRAY(SELECT name FROM path_node JOIN node ON node.id = path_node.node_id WHERE path_id = observation.path_id ORDER BY path_node.pos)) as path_nodes,
    analyzer.name AS analyzer
   FROM observation
     JOIN path ON observation.path_id = path.id
     JOIN analyzer ON analyzer.id = observation.analyzer_id;

CREATE INDEX idx_dip ON iql_data(dip);
CREATE INDEX idx_name ON iql_data(name);
CREATE INDEX idx_name_val_i ON iql_data(name, val_i);
CREATE INDEX idx_name_val_s ON iql_data(name, val_s);
CREATE INDEX idx_path_id ON iql_data(path_id);
CREATE INDEX idx_sip ON iql_data(sip);
CREATE INDEX idx_val_i ON iql_data(val_i);
CREATE INDEX idx_val_s ON iql_data(val_s);
CREATE INDEX idx_path_nodes ON iql_data USING GIN(path_nodes);
