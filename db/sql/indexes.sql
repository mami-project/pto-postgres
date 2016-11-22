CREATE INDEX idx_path_id_ ON path(id);
CREATE INDEX idx_node_id_ ON node(id);
CREATE INDEX idx_path_node_node_id ON path_node(node_id);
CREATE INDEX idx_path_node_path_id ON path_node(path_id);
