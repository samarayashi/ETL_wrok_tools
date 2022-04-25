class DevInfo():
    def __init__(self, target_mrt_name, target_workflow_comment, target_session_name,
    target_mapping_name, ori_sql_query, ori_columns, post_sql, truncate_option) -> None:
        self.target_mrt_name = target_mrt_name
        self.target_workflow_comment = target_workflow_comment
        self.target_session_names = [target_session_name] 
        self.target_mapping_names = [target_mapping_name]
        self.ori_sql_queries = [ori_sql_query]
        self.all_ori_columns = [ori_columns]
        self.post_sqls = [post_sql]
        self.truncate_options = [truncate_option]